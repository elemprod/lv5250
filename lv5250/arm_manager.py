import arm
import arm_uart

from arm import Arm
from arm_uart import ArmMessage, ArmUART

import queue
import time


class ArmManager:

    def __init__(self, port):
        self._arm_uart = arm_uart.ArmUART(port)
        # Internal Arm Data Object
        self._arm = arm.Arm()
        # Externally Shared Arm Data Object
        self._shared_arm = queue.Queue()

    # Function for adding a Get Position Command to the Que

    def get_pos_cmd(self):
        message = ArmMessage(command='GET POS',
                             response='P',
                             timeout=2,
                             cb_start=None,
                             cb_done=self._get_pos_cmd_end_cb,
                             cb_other=self._other_response_cb)
        self._arm_uart.tx_msg_enque(message)

    # Function for adding a Move to Position Command to the Que
    def run_cmd(self, speed, gripper, wrist_roll, wrist_pitch, elbow, shoulder, base):
        cmd_str = 'RUN {} 0 {} {} {} {} {} {} 0 1'.format(
            speed, gripper, wrist_roll, wrist_pitch, elbow, shoulder, base)

        message = ArmMessage(command=cmd_str,
                             response='>END',
                             timeout=5,
                             cb_start=self._run_cmd_start_cb,
                             cb_done=self._run_cmd_end_cb,
                             cb_other=self._other_response_cb)
        self._arm_uart.tx_msg_enque(message)

    # Function for sending the Remote Command.
    # Enables serial control of the Arm.
    def remote_cmd(self):
        print("Remote Cmd")
        message = ArmMessage(command='REMOTE',
                             response='>OK',
                             timeout=1,
                             cb_start=self._remote_cmd_start_cb,
                             cb_done=self._remote_cmd_done_cb,
                             cb_other=self._other_response_cb)
        self._arm_uart.tx_msg_enque(message)

    # Function for sending the Hard Home Command
    # Commands to the robot to find the hardware limit switch positions.
    def hard_home_cmd(self):
        print("Hard Home Cmd")
        message = ArmMessage(command='HARDHOME',
                             response='>END',
                             timeout=30,
                             cb_start=self._hard_home_cmd_start_cb,
                             cb_done=self._hard_home_cmd_done_cb,
                             cb_other=self._other_response_cb)
        self._arm_uart.tx_msg_enque(message)

    # Function for sending the Free Command
    # Disables closed loop control of the Arm.
    def free_cmd(self):
        print("Free Cmd")
        message = ArmMessage(command='FREE',
                             response='>OK',
                             timeout=1,
                             cb_start=None,
                             cb_done=None,
                             cb_other=self._other_response_cb)
        self._arm_uart.tx_msg_enque(message)

    # Function for sending the Torque Command
    # Enables closed loop control of the Arm.
    def torque_cmd(self):
        print("Torque Cmd")
        message = ArmMessage(command='TORQUE',
                             response='>OK',
                             timeout=1,
                             cb_start=None,
                             cb_done=None,
                             cb_other=self._other_response_cb)
        self._arm_uart.tx_msg_enque(message)

    # Function for sending the Shutdown Command
    # Turns off the Arm.
    def shutdown_cmd(self):
        print("Shutdown Cmd")
        message = ArmMessage(command='SHUTDOWN',
                             response='>OK',
                             timeout=1,
                             cb_start=None,
                             cb_done=None,
                             cb_other=self._other_response_cb)
        self._arm_uart.tx_msg_enque(message)

    # Function for handling a Get Position End response

    def _get_pos_cmd_end_cb(self, message: ArmMessage, response: str):
        print('Position Response: {}'.format(response))
        self._handle_position(response)

    # Function for called at the start of a Run Command
    def _run_cmd_start_cb(self, message: ArmMessage):
        # Parse the pending command and commanded postion in the Arm Object
        if message.command:
            str_arr = message.command.split()
            if len(str_arr) == 11 and str_arr[0] == 'RUN':
                self._arm.gripper.command.count = int(str_arr[3])
                self._arm.wrist_roll.command.count = int(str_arr[4])
                self._arm.wrist_pitch.command.count = int(str_arr[5])
                self._arm.elbow.command.count = int(str_arr[6])
                self._arm.shoulder.command.count = int(str_arr[7])
                self._arm.base.command.count = int(str_arr[8])
            else:
                print("Invalid Run Command")
                print(message.command)

    # Generic Function for handling a Other (Unexcepted) Responses
    def _other_response_cb(self, message: ArmMessage, response: str):
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
                elif command == 'LIMIT':
                    print('Unexpected Limit Responses: {}'.format(response))
                elif command == 'GRIP_OBJECT':
                    print(response)
                elif command == 'END':
                    print('Unexpected End Response: {}'.format(response))
                elif command == 'OK':
                    print('Unexpected Limit Response: {}'.format(response))
                elif command == '>STEP':
                    # STEP Responses are Received During a Hard Home
                    print('Step Response: {}'.format(response))
                else:
                    print('Unhandled Response: {}'.format(response))

    # Function for handling a Run Command End response
    def _run_cmd_end_cb(self, message: ArmMessage, response: str):
        print('Run Command Complete : {}'.format(response))

    def _hard_home_cmd_done_cb(self, message: ArmMessage, response: str):
        print("Hard Home Command Complete")

    def _hard_home_cmd_start_cb(self, message: ArmMessage):
        print("Hard Home Command Start")

    def _remote_cmd_done_cb(self, message: ArmMessage, response: str):
        print(response)
        print("Remote Command Complete")

    def _remote_cmd_start_cb(self, message: ArmMessage):
        print("Remote Command Start")

    # Function for handling a position response.
    def _handle_position(self, response: str):
        if response:
            str_arr = response.split()
            if len(str_arr) == 9 and str_arr[0] == 'P':
                self._arm.gripper.current.count = int(str_arr[1])
                self._arm.wrist_roll.current.count = int(str_arr[2])
                self._arm.wrist_pitch.current.count = int(str_arr[3])
                self._arm.elbow.current.count = int(str_arr[4])
                self._arm.shoulder.current.count = int(str_arr[5])
                self._arm.base.current.count = int(str_arr[6])
                # todo handle the last two fields - don't current know their meaning.

                # print('Gripper : {}'.format(str_arr[1]))
                # print('Wrist Roll : {}'.format(str_arr[2]))
                # print('Wrist Pitch : {}'.format(str_arr[3]))
                # print('Elbow : {}'.format(str_arr[4]))
                # print('Shoulder : {}'.format(str_arr[5]))
                # print('Base : {}'.format(str_arr[6]))

    # Function for handling a status response.
    def _handle_status(self, response: str):
        if response:
            str_arr = response.split()
            if len(str_arr) == 23 and str_arr[0] == '?':
                # todo handle the other fields

                self._arm.gripper.current.count = int(str_arr[10])
                self._arm.wrist_roll.current.count = int(str_arr[11])
                self._arm.wrist_pitch.current.count = int(str_arr[12])
                self._arm.elbow.current.count = int(str_arr[13])
                self._arm.shoulder.current.count = int(str_arr[14])
                self._arm.base.current.count = int(str_arr[15])

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
    for _ in range(10):
        #test.manager.get_pos_cmd()
        test.manager.run_cmd(50, 1000, 1000, 20000, 0, 0, 0)
        #test.manager.get_pos_cmd()
        test.manager.run_cmd(50, 1000, 1000, -20000, 0, 0, 0)
    time.sleep(60)
