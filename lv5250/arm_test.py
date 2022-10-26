import arm_cmd

import axis
import encoder
from axis import *
from encoder import *

from axis import RotaryAxis
from axis import LinearAxis

import arm_monitor
from arm_monitor import *

#
# class ArmTest:
#
#     serial_port = ArmSerial()
#
#     def __init__(self):
#         self.serial_port.open()
#
#     def test(self):
#         lv5250 = Arm()
#         command = ArmCmd()
#         rx = ArmRx()
#
#         print(self.serial_port.read())
#         self.serial_port.send(command.enable())
#         print(self.serial_port.read())
#         self.serial_port.send(command.get_pos())
#         position = self.serial_port.read()
#         rx.rx_process(position, lv5250)
#         self.serial_port.send(command.move_inc(50, AxisType.BASE, -100))
#         print(self.serial_port.read())
#         self.serial_port.send(command.get_pos())
#         position = self.serial_port.read()
#         rx.rx_process(position, lv5250)

# Build the GUI


print("Arm Test Start")
monitor = ArmMonitor()
monitor.mainloop()

#lv5250 = Arm()
#monitor.update_arm(lv5250)
#monitor.wrist_roll_cur.set("Test 3")
#monitor.update()


#test = ArmTest()
#test.test()
#test.serial_port.close()
