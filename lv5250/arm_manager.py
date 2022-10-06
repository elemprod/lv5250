import arm
import arm_uart

from arm import Arm
from arm_uart import ArmMessage, ArmUART

import queue
import time


class ArmManager:

    def __init__(self, port):
        self._arm_uart = arm_uart.ArmUART(port)
        # internal Arm Data Object
        self._arm = arm.Arm()
        # external Arm Data Object
        #self._shared_arm = queue.Queue()

    # Function for adding a Get Position Command to the Que

    def get_pos_cmd(self):
        message = ArmMessage(command='GET POS',
                             response='P',
                             timeout=2,
                             cb_start=None,
                             cb_done=self.get_pos_cmd_end_cb,
                             cb_other=None)
        self._arm_uart.tx_msg_enque(message)

    # Function for handling a Get Position End response
    def get_pos_cmd_end_cb(self, message: ArmMessage, response: str):
        print('Position : {}'.format(response))
        if response:
            str_arr = response.split()
            if len(str_arr) == 9 and str_arr[0] == 'P':
                self._arm.gripper.current.count = int(str_arr[1])
                self._arm.wrist_roll.current.count = int(str_arr[2])
                self._arm.wrist_pitch.current.count = int(str_arr[3])
                self._arm.elbow.current.count = int(str_arr[4])
                self._arm.shoulder.current.count = int(str_arr[5])
                self._arm.base.current.count = int(str_arr[6])
                # print('Gripper : {}'.format(str_arr[1]))
                # print('Wrist Roll : {}'.format(str_arr[2]))
                # print('Wrist Pitch : {}'.format(str_arr[3]))
                # print('Elbow : {}'.format(str_arr[4]))
                # print('Shoulder : {}'.format(str_arr[5]))
                # print('Base : {}'.format(str_arr[6]))

    # Function for adding a Move to Position Command to the Que
    def run_cmd(self, speed, gripper, wrist_roll, wrist_pitch, elbow, shoulder, base):
        cmd_str = 'RUN {} 0 {} {} {} {} {} {} 0 1'.format(
            speed, gripper, wrist_roll, wrist_pitch, elbow, shoulder, base)

        message = ArmMessage(command=cmd_str,
                             response='>END',
                             timeout=2,
                             cb_start=self.run_cmd_start_cb,
                             cb_done=None,
                             cb_other=self.run_cmd_other_cb)
        self._arm_uart.tx_msg_enque(message)

    # Function for called at the start of a Run Command
    def run_cmd_start_cb(self, message: ArmMessage):
        # store the commanded postion in the Arm Object
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

    # Function for handling a Run Command Other Response
    def run_cmd_other_cb(self, message: ArmMessage, response: str):
        print(response)

    # Function for handling a Run Command End response
    def run_cmd_end_cb(self, message: ArmMessage, response: str):
        #
        print(response)

    def hard_home_cmd(self):
        print("Hard Home Cmd")
        message = ArmMessage(command='HARDHOME',
                             response='>END',
                             timeout=30,
                             cb_start=self.hard_home_cmd_start_cb,
                             cb_done=self.hard_home_cmd_done_cb,
                             cb_other=self.hard_home_cmd_other_cb)
        self._arm_uart.tx_msg_enque(message)

    def hard_home_cmd_done_cb(self, message: ArmMessage, response: str):
        print("Hard Home Done")

    def hard_home_cmd_other_cb(self, message: ArmMessage, response: str):
        print(response)

    def hard_home_cmd_start_cb(self, message: ArmMessage):
        print("Hard Home Cmd Start")

    def remote_cmd(self):
        print("Remote Cmd")
        message = ArmMessage(command='REMOTE',
                             response='>OK',
                             timeout=1,
                             cb_start=self.remote_cmd_start_cb,
                             cb_done=self.remote_cmd_done_cb,
                             cb_other=self.remote_cmd_other_cb)
        self._arm_uart.tx_msg_enque(message)

    def remote_cmd_done_cb(self, message: ArmMessage, response: str):
        print(response)
        print("Remote Done")

    def remote_cmd_other_cb(self, message: ArmMessage, response: str):
        print(response)

    def remote_cmd_start_cb(self, message: ArmMessage):
        print("Remote Cmd Start")

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
    #test.manager.hard_home_cmd()
    for _ in range(10):
        test.manager.get_pos_cmd()
        test.manager.run_cmd(50, 1000, 1000, 20000, 0, 0, 0)
        test.manager.get_pos_cmd()
        test.manager.run_cmd(50, 1000, 1000, -20000, 0, 0, 0)
    time.sleep(180)
