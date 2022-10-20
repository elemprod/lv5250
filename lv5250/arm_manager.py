import arm
import arm_uart

from arm import Arm
from axis import AxisType

from arm_uart import ArmMessage, ArmUART

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


class ArmMngrMessage(ArmMessage):
    """
    ArmMessage Subclass for internal ArmManager use.

    """

    def __init__(self, command: str, timeout=5, response: str = None, cb_start=None, cb_done=None, cb_other=None, cb_final=None):
        super().__init__(command, timeout, response, cb_start, cb_done, cb_other)
        # The user level callback to make after the Arm object is updated.
        self.cb_final = cb_final


class ArmManager:

    def __init__(self, port: str):
        """
        ArmManager Initializer

        Parameters:
        port: String description of the port.
        """
        self._arm_uart = arm_uart.ArmUART(port)
        # Internal Arm Data Object
        self._arm_local = arm.Arm()

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
        block: Shuld the function wait for an Arm Object to available or
        return immediately if no object is available.

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
        been sent and a response is received or the reques times out.
        """
        message = ArmMngrMessage(command='GET POS',
                                 response='P',
                                 timeout=2,
                                 cb_done=self._get_pos_cmd_end_cb,
                                 cb_other=self._other_response_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    def get_status_cmd(self, cb=None) -> None:
        """
        Add a Get Status Command to the TX Que.

        Parameters:
        cb: Function to be called once the Get Position command has
        been sent and a response is received or the reques times out.
        """
        message = ArmMngrMessage(command='?',
                                 response='?',
                                 timeout=2,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_response_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    def clear_estop_cmd(self, cb=None) -> None:
        """
        Add a Clear E-Stop Command to the TX Que.

        Parameters:
        cb: Function to be called once the Get Position command has
        been sent and a response is received or the reques times out.
        """
        message = ArmMngrMessage(command='SET ESTOP 0',
                                 response='>OK',
                                 timeout=2,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_response_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    def move_to_cmd(self, speed: int, gripper: int, wrist_roll: int, wrist_pitch: int, elbow: int, shoulder: int, base: int, cb=None) -> None:
        """
        Add a Move an Absolute Position Command to the TX Que.

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

        speed = limit_check(speed, 1, 99)
        cmd_str = 'RUN {} 0 {} {} {} {} {} {} 0 1'.format(
            speed, gripper, wrist_roll, wrist_pitch, elbow, shoulder, base)

        message = ArmMngrMessage(command=cmd_str,
                                 response='>END',
                                 timeout=30,
                                 cb_start=self._move_to_cmd_start_cb,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_response_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    def remote_cmd(self, cb=None) -> None:
        """
        Add a Remote Command to the TX Que.

        The remote command notifies the Arm the the Serial Interface is Active
        and generally only needs to be sent once to enable serial control.
        """
        message = ArmMngrMessage(command='REMOTE',
                                 response='>OK',
                                 timeout=5,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_response_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    def close_gripper_cmd(self, cb=None) -> None:
        """
        Add a Close Gripper Command to the TX Que.

        The remote command notifies the Arm the the Serial Interface is Active
        and generally only needs to be sent once to enable serial control.
        """
        message = ArmMngrMessage(command='MOVE 50 0 1',
                                 response='>OK',
                                 timeout=5,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_response_cb,
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
                                 response='>END',
                                 timeout=30,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_response_cb,
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
                                 response='>OK',
                                 timeout=1,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_response_cb,
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
                                 response='>OK',
                                 timeout=1,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_response_cb,
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
                                 response='>OK',
                                 timeout=1,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_response_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    def move_to_limit_cmd(self, axis: AxisType, speed: int, cb=None) -> None:
        """
        Add a Move to Limit Switch Command to the TX Que.

        Moves an axis until the limit switch is detected.

        Parameters:
        axis: The axis to move.  Note that not all axis have limit switches.
        speed: Arm speed -99 to 99 %
        cb: Function to be called once the Shutdown Command completes or
        it times out.
        """
        if speed < 0:
            dir = -1    # reverse
        else:
            dir = 1     # forward
        speed = abs(speed)
        speed = limit_check(speed, 0, 99)

        cmd_str = 'MOVE {} {} {}'.format(speed, axis.value, dir)
        # The final callback is made by the get position comand.
        msg = ArmMngrMessage(command=cmd_str,
                             response='>LIMIT',
                             timeout=20,
                             cb_other=self._other_response_cb,
                             cb_final=cb)
        self._arm_uart.tx_msg_enque(msg)
        # Add get position command so the position is updated after the move
        # completes since the move command does not automatically update the
        # position when it encounters a limit switch.
        self.get_pos_cmd(cb)

    def move_inc_cmd(self, axis: AxisType, speed: int, counts: int, cb=None) -> None:
        """
        Add an Incremental Move Command to the TX Que.

        Moves a single axis by a distance from its current location.
        Note that it is assumed the interal Arm object contains the current
        arm position.  If this is not the case, an arm position update should
        be requested first.

        Parameters:
        axis: The axis to move.
        speed: Arm speed 1 to 99 %
        counts: Distance to move (encoder counts)
        cb: Function to be called once the Shutdown Command completes or
        it times out.
        """
        message = ArmMngrMessage(command=None,
                                 response='>OK',
                                 timeout=30,
                                 cb_start=self._move_inc_cmd_start_cb,
                                 cb_done=self._cmd_done_cb,
                                 cb_other=self._other_response_cb,
                                 cb_final=cb)
        message.axis = axis
        message.speed = speed
        message.counts = counts
        self._arm_uart.tx_msg_enque(message)

    def _move_inc_cmd_start_cb(self, message: ArmMngrMessage) -> ArmMngrMessage:
        """
        Move Incremental Start Callback
        """
        if message.axis == AxisType.BASE:
            pass

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

    # Function for handling a Get Position End response

    def _get_pos_cmd_end_cb(self, message: ArmMngrMessage, response: str):
        """
        Get Position Command End Callback

        Updates the Arm object and makes the final callback.
        """
        print('Position Response: {}'.format(response))
        self._handle_position(response)
        # Make the final callback.
        if callable(message.cb_final):
            message.cb_final(self._arm_local)

    # Function called at the start of a Run Command
    def _move_to_cmd_start_cb(self, message: ArmMngrMessage) -> ArmMngrMessage:
        # Parse the pending commanded postion and update in the Arm Object
        if message.command:
            str_arr = message.command.split()
            if len(str_arr) == 11 and str_arr[0] == 'RUN':
                self._arm_local.gripper.command = int(str_arr[3])
                self._arm_local.wrist_roll.command = int(str_arr[4])
                self._arm_local.wrist_pitch.command = int(str_arr[5])
                self._arm_local.elbow.command = int(str_arr[6])
                self._arm_local.shoulder.command = int(str_arr[7])
                self._arm_local.base.command = int(str_arr[8])
                self._arm_update(self._arm_local)
            else:
                print("Invalid Run Command")
                print(message.command)
        return message

    def _cmd_done_cb(self, message: ArmMngrMessage, response: str):
        """
        Shared Message Done Callback for messages which don't require any
        special completition work.  Makes the user level final callback
        if set.
        """
        if callable(message.cb_final):
            message.cb_final(self._arm_local)

    # Generic Function for handling a Other (Unexcepted) Responses
    def _other_response_cb(self, message: ArmMngrMessage, response: str):
        #TODO update the ARM state
        if response:
            str_arr = response.split()
            if len(str_arr) > 0:
                command = str_arr[0]
                # Attempt to Detect the Response Type
                if command == 'P':
                    # Position Response
                    self._handle_position(response)
                elif command == '?':
                    self._handle_status(response)
                elif command == 'ERR':
                    print('Error Response: {}'.format(response))
                elif command == 'ESTOP':
                    print('E-Stop Response: {}'.format(response))
                elif command == '>LIMIT':
                    print('Unexpected Limit Responses: {}'.format(response))
                elif command == 'GRIP_OBJECT':
                    print(response)
                elif command == 'END':
                    print('Unexpected End Response: {}'.format(response))
                elif command == '>OK':
                    print('Ok Response: {}'.format(response))
                elif command == '>STEP':
                    # STEP Responses are Received During a Hard Home
                    print('Step Response: {}'.format(response))
                else:
                    print('Unhandled Response: {}'.format(response))

    def _handle_position(self, response: str):
        """
        Handle Position Responses

        Position responses start with a P and contain each of the current Arm
        Axis encoder positions.
        """
        if response:
            str_arr = response.split()
            if len(str_arr) == 9 and str_arr[0] == 'P':
                self._arm_local.gripper.current = int(str_arr[1])
                self._arm_local.wrist_roll.current = int(str_arr[2])
                self._arm_local.wrist_pitch.current = int(str_arr[3])
                self._arm_local.elbow.current = int(str_arr[4])
                self._arm_local.shoulder.current = int(str_arr[5])
                self._arm_local.base.current = int(str_arr[6])
                self._arm_update(self._arm_local)
                print(response)
                # TODO:  handle the last two fields but we don't know their meaning

                # print('Gripper : {}'.format(str_arr[1]))
                # print('Wrist Roll : {}'.format(str_arr[2]))
                # print('Wrist Pitch : {}'.format(str_arr[3]))
                # print('Elbow : {}'.format(str_arr[4]))
                # print('Shoulder : {}'.format(str_arr[5]))
                # print('Base : {}'.format(str_arr[6]))

    def _handle_status(self, response: str):
        """
        Handle Status Responses

        Status Responses start with a ? and contain all Arm state information.
        """
        if response:
            str_arr = response.split()
            if len(str_arr) == 23 and str_arr[0] == '?':
                # TODO:  handle the other fields
                self._limit_decode(int(str_arr[8]))

                self._arm_local.gripper.current = int(str_arr[10])
                self._arm_local.wrist_roll.current = int(str_arr[11])
                self._arm_local.wrist_pitch.current = int(str_arr[12])
                self._arm_local.elbow.current = int(str_arr[13])
                self._arm_local.shoulder.current = int(str_arr[14])
                self._arm_local.base.current = int(str_arr[15])
                self._arm_update(self._arm_local)
                #print(response)
            else:
                print('Unhandled Status: {}'.format(response))

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


class ArmManagerTest:
    # Serial Port
    PORT = '/dev/cu.usbserial-FT5ZVFRV'

    def __init__(self):
        print("Arm Manager Test Init")
        self.manager = ArmManager(ArmManagerTest.PORT)


if __name__ == "__main__":
    test = ArmManagerTest()
    test.manager.remote_cmd()
    test.manager.clear_estop_cmd()
    #test.manager.hard_home_cmd()
    test.manager.move_to_cmd(99, 0, -100000, 0, 0, 0, 0)
    #test.manager.close_gripper_cmd()
    #test.manager.move_to_cmd(99, 0, 0, 0, 0, 0, 0)
    #test.manager.move_to_cmd(99, 100000, 0, 0, 0, 0, 0)
    #test.manager.hard_home_cmd()
    #time.sleep(20)
    # for _ in range(100):
    #     test.manager.get_pos_cmd()
    #     test.manager.move_to_cmd(99, 0, 1000, 3000, 0, 0, 0)
    #     test.manager.get_pos_cmd()
    #     test.manager.move_to_cmd(99, 0, 1000, -3000, 0, 0, 0)
    time.sleep(60)
