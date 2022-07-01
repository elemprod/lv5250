import arm_cmd
import arm_serial
import axis
import encoder
from arm_cmd import *
from arm_serial import *
from axis import *
from encoder import *


class ArmTest:

    def __init__(self):
        self.arm_serial = ArmSerial()
        self.arm_serial.open()

    def test(self):
        command = ArmCmd()
        wrist_cmd = command.move_inc(60, AxisType.WRIST_PITCH, 5000)
        print(wrist_cmd)
        #self.arm_serial.send(wrist_cmd)
        base_cmd = command.move_inc(60, AxisType.BASE, -2000)
        print(base_cmd)
        self.arm_serial.send(base_cmd)
        #arm_serial.send(command.move_inc(60, AxisType.ELBOW, -1000))


test = ArmTest()
test.test()
