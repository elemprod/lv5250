import arm_cmd
import arm_serial
import arm_rx
import axis
import encoder
from arm_cmd import *
from arm_serial import *
from arm_rx import *
from axis import *
from encoder import *

from axis import RotaryAxis
from axis import LinearAxis


class ArmTest:

    serial_port = ArmSerial()

    def __init__(self):
        self.serial_port.open()

    def test(self):
        lv5250 = Arm()
        command = ArmCmd()
        rx = ArmRx()

        print(self.serial_port.read())
        self.serial_port.send(command.enable())
        print(self.serial_port.read())
        self.serial_port.send(command.get_pos())
        position = self.serial_port.read()
        rx.rx_process(position, lv5250)
        self.serial_port.send(command.move_inc(50, AxisType.BASE, -100))
        print(self.serial_port.read())
        self.serial_port.send(command.get_pos())
        position = self.serial_port.read()
        rx.rx_process(position, lv5250)


test = ArmTest()
test.test()
test.serial_port.close()
