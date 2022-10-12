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

# ArmMessage Subclass with a Final Callback which returns the updated Arm Object
# once the command completes.


class ArmMessageMngr(ArmMessage):
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
        Get the Arm Object

        Parameters:
        block: Wait for an Arm Object to available?
        timeout: Maximuim time to wait (seconds)

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

    def get_pos_cmd(self, cb: None) -> None:
        """
        Add a Get Position Command to the TX Que.

        Parameters:
        cb: Function to be called once the Get Position command has
        been sent and a response is received or the reques times out.
        """
        message = ArmMessageMngr(command='GET POS',
                                 response='P',
                                 timeout=2,
                                 cb_start=None,
                                 cb_done=self._get_pos_cmd_end_cb,
                                 cb_other=self._other_response_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    def move_to_cmd(self, speed: int, gripper: int, wrist_roll: int, wrist_pitch: int, elbow: int, shoulder: int, base: int, cb: None) -> None:
        """
        Add a Move Position command to the TX Que.

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

        message = ArmMessageMngr(command=cmd_str,
                                 response='>END',
                                 timeout=5,
                                 cb_start=self._move_to_cmd_start_cb,
                                 cb_done=self._move_to_cmd_end_cb,
                                 cb_other=self._other_response_cb,
                                 cb_final=cb)
        self._arm_uart.tx_msg_enque(message)

    # Function for sending the Remote Command.
    # Enables serial control of the Arm.
    def remote_cmd(self, cb: None) -> None:
        """
        Add a Remote Command to the TX Que.

        The remote command notifies the Arm the the Serial Interface is Active
        and generally only needs to be sent once at the start of serial
        control.
        """
        message = ArmMessage(command='REMOTE',
                             response='>OK',
                             timeout=1,
                             cb_start=self._remote_cmd_start_cb,
                             cb_done=self._remote_cmd_done_cb,
                             cb_other=self._other_response_cb)
        self._arm_uart.tx_msg_enque(message)

    # Function for sending the Hard Home Command
    # Commands to the robot to find the hardware limit switch positions.
    def hard_home_cmd(self, cb: None) -> None:
        """
        Add a Hard Home Command to the TX Que.

        The Hard Home commands finds each of the Arm Limit switch positions
        and centers the Arm's position.  The command would typically be sent
        at the start of each session or after the arm looses its position
        due to colliding with something.

        Parameters:
        cb: Function to be called once the Hard Home completes or
        it times out.
        """
        message = ArmMessage(command='HARDHOME',
                             response='>END',
                             timeout=30,
                             cb_start=self._hard_home_cmd_start_cb,
                             cb_done=self._hard_home_cmd_done_cb,
                             cb_other=self._other_response_cb)
        self._arm_uart.tx_msg_enque(message)

    # Function for sending the Free Command
    # Disables closed loop control of the Arm.
    def free_cmd(self, cb: None) -> None:
        """
        Add a Free Command to the TX Que.

        The Free Command disables closed loop control of the Arm enabling it
        to be moved.

        Parameters:
        cb: Function to be called once the Free Command completes or
        it times out.
        """
        message = ArmMessage(command='FREE',
                             response='>OK',
                             timeout=1,
                             cb_start=None,
                             cb_done=None,
                             cb_other=self._other_response_cb)
        self._arm_uart.tx_msg_enque(message)

    def torque_cmd(self, cb: None) -> None:
        """
        Add a Torque Command to the TX Que.

        The Torque Command enables closed loop control of the Arm.

        Parameters:
        cb: Function to be called once the Torque Command completes or
        it times out.
        """
        message = ArmMessage(command='TORQUE',
                             response='>OK',
                             timeout=1,
                             cb_start=None,
                             cb_done=None,
                             cb_other=self._other_response_cb)
        self._arm_uart.tx_msg_enque(message)

    # Function for sending the Shutdown Command
    # Turns off the Arm.
    def shutdown_cmd(self, cb: None) -> None:
        """
        Add a Shutdown Command to the TX Que.

        Parameters:
        cb: Function to be called once the Shutdown Command completes or
        it times out.
        """
        message = ArmMessage(command='SHUTDOWN',
                             response='>OK',
                             timeout=1,
                             cb_start=None,
                             cb_done=None,
                             cb_other=self._other_response_cb)
        self._arm_uart.tx_msg_enque(message)

    def move_to_limit_cmd(self, axis: AxisType, speed: int, cb: None) -> None:
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
        msg = ArmMessage(command=cmd_str,
                         response='>LIMIT',
                         timeout=30,
                         cb_start=None,
                         cb_done=self._move_to_limit_end_cb,
                         cb_other=self._other_response_cb)
        self._arm_uart.tx_msg_enque(msg)
        # Enque get position command so the position is updated after the move
        # completes since the move command does not automatically send the
        # positiuon if it encounters a limit switch.
        self.get_pos_cmd(cb)

    def move_inc_cmd(self, axis: AxisType, speed: int, counts: int, get_pos: True, cb: None) -> None:
        """
        Add an Incremental Move Command to the TX Que.

        Moves a single axis by a fixed distance from the current location.

        Parameters:
        axis: The axis to move.
        speed: Arm speed 1 to 99 %
        counts: Distance to move (encoder counts)
        get_pos: Should the get position command be automatically sent before
        making the move.  Not necessary if the internal Arm position has already
        been updated.
        cb: Function to be called once the Shutdown Command completes or
        it times out.
        """
        pass

    # Function for handling a Find Axis Limit command

    def _find_axis_limit_end_cb(self, message: ArmMessage, response: str):
        print('Find Limit Response: {}'.format(response))

    # Internal function for updating the shared arm object with a new version.

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

    def _get_pos_cmd_end_cb(self, message: ArmMessageMngr, response: str):
        """
        Handle the Get Position Responsee

        Updates the Arm object and makes the final callback.
        """
        print('Position Response: {}'.format(response))
        self._handle_position(response)
        # Make the final callback.
        if callable(message.cb_final):
            message.cb_final(self._arm_local)

    # Function called at the start of a Run Command
    def _move_to_cmd_start_cb(self, message: ArmMessage):
        # Parse the pending commanded postion and update in the Arm Object
        if message.command:
            str_arr = message.command.split()
            if len(str_arr) == 11 and str_arr[0] == 'RUN':
                self._arm_local.gripper.command.count = int(str_arr[3])
                self._arm_local.wrist_roll.command.count = int(str_arr[4])
                self._arm_local.wrist_pitch.command.count = int(str_arr[5])
                self._arm_local.elbow.command.count = int(str_arr[6])
                self._arm_local.shoulder.command.count = int(str_arr[7])
                self._arm_local.base.command.count = int(str_arr[8])
                self._arm_update(self._arm_local)
            else:
                print("Invalid Run Command")
                print(message.command)

    # Generic Function for handling a Other (Unexcepted) Responses
    def _other_response_cb(self, message: ArmMessage, response: str):
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

    # Function for handling a Run Command End response
    def _move_to_cmd_end_cb(self, message: ArmMessage, response: str):
        print('Run Command Complete : {}'.format(response))

    def _hard_home_cmd_done_cb(self, message: ArmMessage, response: str):
        print("Hard Home Command Complete")
        # print('Gripper HW Limit: {}, {}'.format(self._arm_local.gripper.current.count_min,
        #       self._arm_local.gripper.current.count_max))
        # print('Wrist Roll HW Limit: {}, {}'.format(self._arm_local.wrist_roll.current.count_min,
        #       self._arm_local.wrist_roll.current.count_max))
        # print('Wrist Pitch HW Limit: {}, {}'.format(self._arm_local.wrist_pitch.current.count_min,
        #       self._arm_local.wrist_pitch.current.count_max))
        # print('Elbow HW Limit: {}, {}'.format(self._arm_local.elbow.current.count_min,
        #       self._arm_local.elbow.current.count_max))
        # print('Shoulder HW Limit: {}, {}'.format(self._arm_local.shoulder.current.count_min,
        #       self._arm_local.shoulder.current.count_max))
        # print('Base HW Limit: {}, {}'.format(self._arm_local.base.current.count_min,
        #       self._arm_local.base.current.count_max))

    def _hard_home_cmd_start_cb(self, message: ArmMessage):
        print("Hard Home Command Start")

    def _remote_cmd_done_cb(self, message: ArmMessage, response: str):
        print(response)
        print("Remote Command Complete")

    def _remote_cmd_start_cb(self, message: ArmMessage):
        print("Remote Command Start")

    def _handle_position(self, response: str):
        """
        Handle Position Response Message

        Position responses start with a P and contain each of the current Arm
        Axis encoder positions.
        """
        if response:
            str_arr = response.split()
            if len(str_arr) == 9 and str_arr[0] == 'P':
                self._arm_local.gripper.current.count = int(str_arr[1])
                self._arm_local.wrist_roll.current.count = int(str_arr[2])
                self._arm_local.wrist_pitch.current.count = int(str_arr[3])
                self._arm_local.elbow.current.count = int(str_arr[4])
                self._arm_local.shoulder.current.count = int(str_arr[5])
                self._arm_local.base.current.count = int(str_arr[6])
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
        Handle Position Response Message

        Status Responses start with a ? and contain all Arm state information.
        """
        if response:
            str_arr = response.split()
            if len(str_arr) == 23 and str_arr[0] == '?':
                # TODO:  handle the other fields
                self._arm_local.gripper.current.count = int(str_arr[10])
                self._arm_local.wrist_roll.current.count = int(str_arr[11])
                self._arm_local.wrist_pitch.current.count = int(str_arr[12])
                self._arm_local.elbow.current.count = int(str_arr[13])
                self._arm_local.shoulder.current.count = int(str_arr[14])
                self._arm_local.base.current.count = int(str_arr[15])
                self._arm_update(self._arm_local)
                #print(response)
            else:
                print('Unhandled Status: {}'.format(response))


# Test Class for the Arm Maanager


class ArmManagerTest:
    # Serial Port
    PORT = '/dev/cu.usbserial-FT5ZVFRV'

    def __init__(self):
        print("Arm Manager Test Init")
        self.manager = ArmManager(ArmManagerTest.PORT)


if __name__ == "__main__":
    test = ArmManagerTest()
    test.manager.remote_cmd()
    test.manager.hard_home_cmd()
    test.manager.find_axis_limit(AxisType.BASE)
    #test.manager.move_to_cmd(99, 0, -0000, 0, 0, 0, 0)
    #test.manager.hard_home_cmd()
    #time.sleep(20)
    # for _ in range(100):
    #     test.manager.get_pos_cmd()
    #     test.manager.move_to_cmd(99, 0, 1000, 3000, 0, 0, 0)
    #     test.manager.get_pos_cmd()
    #     test.manager.move_to_cmd(99, 0, 1000, -3000, 0, 0, 0)
    time.sleep(60)
