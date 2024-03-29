from lv5250 import *
from lv5250.arm import *
from lv5250.axis import *
from lv5250.axises import *
from lv5250.arm_uart import *

import queue
import time

from typing import Callable


def limit_check(value: int, limit_min: int, limit_max: int) -> int:
    if value < limit_min:
        return limit_min
    elif value > limit_max:
        return limit_max
    else:
        return value


class IncMoveMsg:
    """
    Incremental Move Object.
    Store an incremental move information so that the new position can be
    calculated when the message is generated.

    Parameters:
    axis:  The axis to move.
    speed: The speed
    counts: The distance in encoder counts to move.
    """

    def __init__(self, axis: AxisType, speed: int, counts: int):
        self.axis = AxisType(axis)
        self.speed = limit_check(int(speed), 1, 99)
        self.counts = int(counts)


class ArmMngrMessage(ArmMessage):
    """
    Arm Message Subclass.

    Parameters:
    cb_final: The user level callback to make once the message as been sent and
    a resp is received or or the message times out.

    """

    def __init__(self,
                 command: str,
                 timeout: int = 5,
                 resp: str = None,
                 resp_ignore: str = None,
                 cb_start=None,
                 cb_done=None,
                 cb_other=None,
                 cb_final=None,
                 axises: Axises = None,
                 inc_move: IncMoveMsg = None):
        super().__init__(command=command,
                         timeout=timeout,
                         resp=resp,
                         resp_ignore=resp_ignore,
                         cb_start=cb_start,
                         cb_done=cb_done,
                         cb_other=cb_other)
        self.cb_final = cb_final
        # Absolute move command Axises
        self.axises = axises
        # Incremental move object for an incremental move command.
        self.inc_move = inc_move


class ArmManager:

    def __init__(self, port: str):
        """
        ArmManager Initializer

        Parameters:
        port: String description of the port.
        """
        self._arm_uart = ArmUART(port)
        # Internal Arm Data Object
        self._arm_local = Arm()

        # External Arm Data Object Queue
        # The object is updated with the current arm state, position and
        # commands as they are sent and received over the serial connection.
        # Implemented as Last In First Out Queue so that the user gets the
        # most recently updated version.
        self.arm = queue.LifoQueue()

    def arm_get(self, block=True, timeout=None) -> Arm:
        """
        Returns the Current Arm Object

        Parameters:
        block: Should the function wait for an Arm Object to available or
        return immediately if no object is available?

        timeout: Maximuim time to wait for the Arm Object (seconds)

        Returns:
        The most recently updated Arm Object or None if one is not available.
        """
        try:
            # Remove the latest version of the arm object from the queue
            arm_return = self.arm.get(block, timeout)
            # Remove the older objects from the queue.
            self.arm.queue.clear()
            return arm_return
        except queue.Empty:
            return None

    def get_pos_cmd(self, cb=None) -> None:
        """
        Add a Get Position Command to the TX Que.

        Parameters:
        cb: Function to be called once the Get Position command has
        been sent and a resp is received or the reques times out.
        """
        message = ArmMngrMessage(command='GET POS',
                                 resp='P',
                                 timeout=2,
                                 cb_done=self._get_pos_cmd_end_cb,
                                 cb_other=self._other_resp_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    def get_status_cmd(self, cb=None) -> None:
        """
        Add a Get Status Command to the TX Que.

        Parameters:
        cb: Function to be called once the Get Position command has
        been sent and a resp is received or the reques times out.
        """
        message = ArmMngrMessage(command='?',
                                 resp='?',
                                 timeout=2,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_resp_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    def clear_estop_cmd(self, cb=None) -> None:
        """
        Add a Clear E-Stop Command to the TX Que.

        Parameters:
        cb: Function to be called once the Get Position command has
        been sent and a resp is received or the reques times out.
        """
        message = ArmMngrMessage(command='SET ESTOP 0',
                                 resp='>OK',
                                 timeout=2,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_resp_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    def move_to_axises_cmd(self,
                           speed: int,
                           axises: Axises,
                           cb=None,
                           timeout: int = 30) -> None:
        """
        Add a Move to an Absolute Position Command to the TX Que.

        Parameters:
        speed: Arm speed,  1 to 99 %
        axises: The axises position to move to.
        cb: Function to be called once the move has been completed or times out.
        """
        # Create the move command string
        cmd_str = self._run_cmd_str(speed, axises)
        message = ArmMngrMessage(command=cmd_str,
                                 resp='>END',
                                 timeout=int(timeout),
                                 cb_start=self._move_to_cmd_start_cb,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_resp_cb,
                                 cb_final=cb,
                                 axises=axises)
        self._arm_uart.tx_msg_enque(message)

    def move_to_cmd(self, speed: int, gripper: int, wrist_roll: int, wrist_pitch: int, elbow: int, shoulder: int, base: int, cb=None) -> None:
        """
        Add a Move to an Absolute Position Command to the TX Que.

        Parameters:
        speed: Arm speed,  1 to 99 %
        gripper: Gripper Axis position (encoder counts)
        wrist_roll: Wrist Roll Axis position (encoder counts)
        wrist_pitch: Wrist Pitch Axis position (encoder counts)
        elbow: Elbow Axis position (encoder counts)
        shoulder: Shoulder Axis position (encoder counts)
        base: Base Axis position (encoder counts)
        cb: Function to be called once the move has been completed or times out.
        """

        # Create an axises with the command position.
        axises = Axises()
        axises.gripper.counts = gripper
        axises.wrist_roll.counts = wrist_roll
        axises.wrist_pitch.counts = wrist_pitch
        axises.elbow.counts = elbow
        axises.shoulder.counts = shoulder
        axises.base.counts = base

        # Create the move command string
        cmd_str = self._run_cmd_str(speed, axises)
        message = ArmMngrMessage(command=cmd_str,
                                 resp='>END',
                                 timeout=30,
                                 cb_start=self._move_to_cmd_start_cb,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_resp_cb,
                                 cb_final=cb,
                                 axises=axises)
        self._arm_uart.tx_msg_enque(message)

    def remote_cmd(self, cb=None) -> None:
        """
        Add a Remote Command to the TX Que.

        The remote command notifies the Arm the the Serial Interface is Active
        and generally only needs to be sent once to enable serial control at
        the start of a session.
        """
        message = ArmMngrMessage(command='REMOTE',
                                 resp='>OK',
                                 timeout=5,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_resp_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    def stop_cmd(self, cb=None) -> None:
        """
        Add a Stop Command to the TX Que.

        """
        message = ArmMngrMessage(command='STOP',
                                 resp='>OK',
                                 timeout=5,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_resp_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    def gripper_close_cmd(self,
                          speed: int = 50,
                          timeout: int = 10,
                          cb=None) -> None:
        """
        Add a Close Gripper Command to the TX Que and sait for the >GRIP_CLOSED
        response which indicates the Gripper is fully closed or grasping an
        object.

        Parameters:
        speed: Gripper speed (1 to 99%)
        timeout: The maximuim time to wait for the comamnd to complete (seconds)
        cb: Function to call once the command completes or it times out.
        """
        speed = limit_check(speed, 1, 99)
        message = ArmMngrMessage(command=f'MOVE {speed} 0 -1',
                                 resp='>GRIP_CLOSED',
                                 resp_ignore='>OK',
                                 timeout=int(timeout),
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_resp_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    def gripper_open_cmd(self,
                         speed: int = 50,
                         timeout: int = 20,
                         cb=None) -> None:
        #TODO this doesn't call back after the gripper is fully open
        # since there's not a response indicating when the gripper is fully
        # open
        """
        Add a Open Gripper Command to the TX Que.


        Parameters:
        speed: Gripper speed (1 to 99%)
        timeout: The maximuim time to wait for the comamnd to complete (seconds)
        cb: Function to call once the command completes or it times out.
        """

        speed = limit_check(speed, 1, 99)
        # The Arm replies with >OK immediately so we ignore that.
        message = ArmMngrMessage(command=f'MOVE {speed} 0 1',
                                 resp_ignore='>OK',
                                 timeout=int(timeout),
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_resp_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    def hard_home_cmd(self, cb=None) -> None:
        """
        Add a Hard Home Command to the TX Que.

        The Hard Home commands finds each of the Arm Limit switch positions
        and moves the the Arm to the zero position.  The command would
        typically be sent at the start of each session or after the arm looses
        it's position due to colliding with an obstacle.

        Parameters:
        cb: Function to be called once the Hard Home completes or
        it times out.
        """
        message = ArmMngrMessage(command='HARDHOME',
                                 resp='>END',
                                 timeout=30,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_resp_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    def free_cmd(self, cb=None) -> None:
        """
        Add a Free Command to the TX Que.

        The Free Command disables closed loop control of the Arm enabling it
        to be moved.

        Parameters:
        cb: Function to be called once the Free Command completes or
        it times out.
        """
        message = ArmMngrMessage(command='FREE',
                                 resp='>OK',
                                 timeout=1,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_resp_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    def torque_cmd(self, cb=None) -> None:
        """
        Add a Torque Command to the TX Que.

        The Torque Command enables closed loop control of the Arm.

        Parameters:
        cb: Function to be called once the Torque Command completes or
        it times out.
        """
        message = ArmMngrMessage(command='TORQUE',
                                 resp='>OK',
                                 timeout=1,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_resp_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    # Function for sending the Shutdown Command
    # Turns off the Arm.
    def shutdown_cmd(self, cb=None) -> None:
        """
        Add a Shutdown Command to the TX Que.

        Parameters:
        cb: Function to be called once the Shutdown Command completes or
        it times out.
        """
        message = ArmMngrMessage(command='SHUTDOWN',
                                 resp='>OK',
                                 timeout=1,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_resp_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    def move_to_limit_cmd(self, axis: AxisType, speed: int, cb=None, timeout: int = 30) -> None:
        """
        Add a Move to Limit Switch Command to the TX Que.

        Moves an axis until the limit switch is detected.

        Parameters:
        axis: The axis to move.  Note that not all axis have limit switches.
        speed: Arm speed -99 to 99 %
        cb: Function to be called once the limit switch is detected or the move
        times out.
        """

        cmd_str = self._move_cmd_str(axis, speed)
        # The final callback is made by the get position comand.
        msg = ArmMngrMessage(command=cmd_str,
                             resp='>LIMIT',
                             timeout=int(timeout),
                             cb_other=self._other_resp_cb,
                             cb_final=cb)
        self._arm_uart.tx_msg_enque(msg)
        # Add get position command so the position is updated after the move
        # completes since the move command does not automatically update the
        # position when it encounters a limit switch.
        self.get_pos_cmd(cb)

    def move_axis_cmd(self, axis: AxisType, speed: int, cb=None, timeout: int = 30) -> None:
        """
        Add a Move Axis Command to the TX Que.  The command moves the
        selected axis until the limit switch is detected or a stop command is
        sent.  The command returns once the OK response is received from the
        Arm or it times outs.

        Parameters:
        axis: The axis to move.
        speed: Arm speed -99 to 99 %
        cb: Function to be called once the move command is sent.
        """

        cmd_str = self._move_cmd_str(axis, speed)
        print(cmd_str)
        # The final callback is made by the get position comand.
        msg = ArmMngrMessage(command=cmd_str,
                             resp='>OK',
                             timeout=int(timeout),
                             cb_other=self._other_resp_cb,
                             cb_final=cb)
        self._arm_uart.tx_msg_enque(msg)

    def _move_cmd_str(self, axis: AxisType, speed: int) -> str:
        """
        Create a Move Command Message String.
        """
        speed_cmd = int(speed)
        if speed_cmd < 0:
            dir_cmd = -1    # reverse
        else:
            dir_cmd = 1     # forward
        speed_cmd = abs(speed)
        speed_cmd = limit_check(speed_cmd, 0, 99)

        cmd_str = 'MOVE {} {} {}'.format(speed_cmd, axis.value, dir_cmd)
        return cmd_str

    def move_inc_cmd(self, axis: AxisType, speed: int, counts: int, cb=None) -> None:
        """
        Add an Incremental Move Command to the TX Que.

        Moves a single axis by a distance from the last commanded position.

        Parameters:
        axis: The axis to move.
        speed: Arm speed 1 to 99 %
        counts: Incremental distance to move (encoder counts)
        cb: Function to be called once the Shutdown Command completes or
        it times out.
        """

        incremental = IncMoveMsg(axis, speed, counts)

        message = ArmMngrMessage(command=None,
                                 resp='>END',
                                 timeout=30,
                                 cb_start=self._move_inc_cmd_start_cb,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_resp_cb,
                                 cb_final=cb,
                                 inc_move=incremental)
        self._arm_uart.tx_msg_enque(message)

    def _move_inc_cmd_start_cb(self, message: ArmMngrMessage) -> ArmMngrMessage:
        """
        Move Incremental Start Callback.

        Create a move message by adding the incremental move to the
        last commanded position.
        """
        # Add the incremental move to the correct axis
        if message.inc_move.axis == AxisType.GRIPPER:
            self._arm_local.command.gripper.counts += message.inc_move.counts
        elif message.inc_move.axis == AxisType.WRIST_ROLL:
            self._arm_local.command.wrist_roll.counts += message.inc_move.counts
        elif message.inc_move.axis == AxisType.WRIST_PITCH:
            self._arm_local.command.wrist_pitch.counts += message.inc_move.counts
        elif message.inc_move.axis == AxisType.ELBOW:
            self._arm_local.command.elbow.counts += message.inc_move.counts
        elif message.inc_move.axis == AxisType.SHOULDER:
            self._arm_local.command.shoulder.counts += message.inc_move.counts
        elif message.inc_move.axis == AxisType.BASE:
            self._arm_local.command.base.counts += message.inc_move.counts

        # Generate the command string
        message.command = self._run_cmd_str(
            message.inc_move.speed, self._arm_local.command)
        print('Incremental Move Msg: {}'.format(message.command))
        self._arm_update(self._arm_local)
        return message

    def _arm_update(self, arm: Arm):
        """
        Update the shared Arm Object

        Parameters:
        arm: The updated Arm object
        """
        if arm:
            try:
                # Add object into the shared queue
                self.arm.put_nowait(arm)
            except queue.Full:
                # clear the queue if it's full and try again.
                self.arm.queue.clear()
                self._arm_update(arm)

    # Function for handling a Get Position End resp

    def _get_pos_cmd_end_cb(self, message: ArmMngrMessage, resp: str):
        """
        Get Position Command End Callback

        Updates the local Arm object and makes the final callback.

        """
        print('Position resp: {}'.format(resp))
        self._handle_position(resp)
        # Make the final callback.
        if callable(message.cb_final):
            message.cb_final(self._arm_local)

    # Function called at the start of a Run Command
    def _move_to_cmd_start_cb(self, message: ArmMngrMessage) -> ArmMngrMessage:
        # Update in the Arm Object with the new command.
        self._arm_local.command = message.axises
        self._arm_update(self._arm_local)
        return message

    def _cmd_done_cb(self, message: ArmMngrMessage, resp: str):
        """
        Shared Message Done Callback for messages which don't require any
        special completition work.  Makes the user level final callback
        if set.
        """
        if callable(message.cb_final):
            message.cb_final(self._arm_local)

    # Generic Function for handling a Other (Unexcepted) resps
    def _other_resp_cb(self, message: ArmMngrMessage, resp: str):
        #TODO update the ARM state
        if resp:
            str_arr = resp.split()
            if len(str_arr) > 0:
                command = str_arr[0]
                # Attempt to Detect the resp Type
                if command == 'P':  # Position resp
                    self._handle_position(resp)
                elif command == '?':
                    self._handle_status(resp)
                elif command == 'ERR':
                    print(f'Error resp: {resp}')
                elif command == 'ESTOP':
                    print(f'E-Stop resp: {resp}')
                elif command == '>LIMIT':
                    print(f'Unexpected Limit resps: {resp}')
                elif command == 'GRIP_OBJECT':
                    print(resp)
                elif command == 'END':
                    print(f'Unexpected End resp: {resp}')
                elif command == '>OK':
                    print(f'Ok resp: {resp}')
                elif command == '>STEP':
                    # STEP resps are Received During a Hard Home
                    print(f'Step resp: {resp}')
                else:
                    print(f'Unhandled resp: {resp}')

    def _handle_position(self, resp: str):
        """
        Handle Position resps

        Position resps start with a P and contain each of the current Arm
        Axis encoder positions.
        """
        if resp:
            str_arr = resp.split()
            if len(str_arr) == 9 and str_arr[0] == 'P':
                self._arm_local.position.gripper.counts = int(str_arr[1])
                self._arm_local.position.wrist_roll.counts = int(str_arr[2])
                self._arm_local.position.wrist_pitch.counts = int(str_arr[3])
                self._arm_local.position.elbow.counts = int(str_arr[4])
                self._arm_local.position.shoulder.counts = int(str_arr[5])
                self._arm_local.position.base.counts = int(str_arr[6])
                self._arm_update(self._arm_local)
                print(resp)
                # TODO:  handle the last two fields but we don't know their meaning

    def _handle_status(self, resp: str):
        """
        Handle Status resps

        Status resps start with a ? and contain all Arm state information.
        """
        if resp:
            str_arr = resp.split()
            if len(str_arr) == 23 and str_arr[0] == '?':
                # TODO:  handle the other fields
                self._limit_decode(int(str_arr[8]))

                self._arm_local.position.gripper.counts = int(str_arr[10])
                self._arm_local.position.wrist_roll.counts = int(str_arr[11])
                self._arm_local.position.wrist_pitch.counts = int(str_arr[12])
                self._arm_local.position.elbow.counts = int(str_arr[13])
                self._arm_local.position.shoulder.counts = int(str_arr[14])
                self._arm_local.position.base.counts = int(str_arr[15])
                self._arm_update(self._arm_local)
                #print(resp)
            else:
                print('Unhandled Status: {}'.format(resp))

    def _limit_decode(self, limit: int):
        if limit != 0:
            #print('Limit Sw: {}'.format(limit))
            if limit & (1 << AxisType.BASE.value):
                print('Base Limit Switch')
            if limit & (1 << AxisType.SHOULDER.value):
                print('Shoulder Limit Switch')
            if limit & (1 << AxisType.ELBOW.value):
                print('Elbow Limit Switch')
            if limit & (1 << AxisType.WRIST_PITCH.value):
                print('Wrist Pitch Limit Switch')
            if limit & (1 << AxisType.WRIST_ROLL.value):
                print('Wrist Roll Center Switch')
            if limit & (1 << AxisType.GRIPPER.value):
                print('Gripper Limit')

    def _run_cmd_str(self, speed: int, axises: Axises) -> str:
        """
        Create a Run Command Message String from the
        supplied Axises object
        """
        speed = limit_check(speed, 1, 99)
        return 'RUN {} 0 {} {} {} {} {} {} 0 1'.format(
                speed,
                axises.gripper.counts,
                axises.wrist_roll.counts,
                axises.wrist_pitch.counts,
                axises.elbow.counts,
                axises.shoulder.counts,
                axises.base.counts)

    def run_test_cmd(self):

        speed = 50
        # paramater 1 - uknown
        par_1 = 0         # doesn't see to change anything
        gripper = 5000
        wrist_roll = 0
        wrist_pitch = 0
        elbow = 0
        shoulder = 0
        base = 0
        par8 = 0
        par9 = 0

        cmd_str = 'RUN {} {} {} {} {} {} {} {} {} {}'.format(
                speed,
                par_1,
                gripper,
                wrist_roll,
                wrist_pitch,
                elbow,
                shoulder,
                base,
                par8,
                par9)
        print(cmd_str)
        message = ArmMngrMessage(command=cmd_str,
                                 resp='>END',
                                 timeout=30,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_resp_cb)
        self._arm_uart.tx_msg_enque(message)


def done_print_cb(arm):
    print(
        f'Gripper: {arm.position.gripper.counts} cnts / {arm.position.gripper.mm:.2f} mm')
    print(
        f'Wrist Roll: {arm.position.wrist_roll.counts} cnts / {arm.position.wrist_roll.angle:.1f} deg')
    print(
        f'Wrist Pitch: {arm.position.wrist_pitch.counts} cnts / {arm.position.wrist_pitch.angle:.1f} deg')
    print(
        f'Elbow: {arm.position.elbow.counts} cnts / {arm.position.elbow.angle:.1f} deg')
    print(
        f'Shoulder: {arm.position.shoulder.counts} cnts / {arm.position.shoulder.angle:.1f} deg')
    print(
        f'Base: {arm.position.base.counts} cnts / {arm.position.base.angle:.1f} deg')


def gripper_close_cb(arm):
    #manager.stop_cmd()
    print('gripper_close_cb()')


def gripper_open_cb(arm):
    #manager.stop_cmd()
    print('gripper_open_cb()')


if __name__ == "__main__":

    PORT = '/dev/cu.usbserial-FT5ZVFRV'
    manager = ArmManager(PORT)

    manager.remote_cmd()
    manager.clear_estop_cmd()
    manager.stop_cmd()

    for i in range(10):
        manager.move_axis_cmd(axis=AxisType.ELBOW, speed=20)
        time.sleep(1)
        manager.stop_cmd()

        manager.move_axis_cmd(axis=AxisType.ELBOW, speed=-20)
        time.sleep(1)
        manager.stop_cmd()

    #manager.hard_home_cmd()

    # manager.gripper_close_cmd(speed=60, timeout=10, cb=gripper_close_cb)
    # manager.get_pos_cmd(done_print_cb)
    # manager.gripper_open_cmd(speed=60, timeout=10, cb=gripper_open_cb)
    # manager.get_pos_cmd(done_print_cb)
    # manager.gripper_close_cmd(speed=60, timeout=10, cb=gripper_close_cb)
    # manager.get_pos_cmd(done_print_cb)

    # axises = Axises(limits_en=True)
    # axises.gripper.mm = 50
    # axises.wrist_roll.angle = 0
    # axises.shoulder.angle = 90
    # axises.elbow.angle = 0
    # axises.wrist_pitch.angle = 0
    # axises.base.angle = 0
    #
    # manager.move_to_axises_cmd(50, axises, done_print_cb)
    # manager.get_pos_cmd(done_print_cb)

    #axises.gripper.counts = 100
    #manager.move_to_axises_cmd(50, axises, done_print_cb)
    #axises.gripper.counts = 20000
    #manager.move_to_axises_cmd(50, axises, done_print_cb)
    #arm.get_pos_cmd(done_print_cb)

    #axises.wrist_pitch.angle = -10
    #arm.move_to_axises_cmd(50, axises)

    #arm.get_pos_cmd(done_print_cb)

    # axises.wrist_pitch.angle = 45
    # axises.elbow.angle = 0
    # axises.shoulder.angle = 0
    # axises.base.angle = 0
    # arm.move_to_axises_cmd(50, axises)
    # arm.get_pos_cmd(done_print_cb)
    #
    # axises.wrist_pitch.angle = 0
    # axises.elbow.angle = 0
    # axises.shoulder.angle = -30
    # axises.base.angle = 0
    # arm.move_to_axises_cmd(50, axises)
    # arm.get_pos_cmd(done_print_cb)

    #arm.move_to_limit_cmd(AxisType.SHOULDER, -10, print_abs_cb)
    #arm.get_pos_cmd(print_abs_cb)

    time.sleep(120)

    time.sleep(120)
