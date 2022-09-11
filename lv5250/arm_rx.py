import arm
from arm import *

from enum import Enum

#Serial RX Processor Class


class ArmRx:

    def __init__(self):
        pass

    def rx_process(self, rx_bytes: bytes, arm_inst: Arm):
        print(rx_bytes)
        tokens = rx_bytes.split(bytes(' ', 'utf-8'))
        print(tokens)
        if((tokens[0] == bytes('P', 'utf-8')) & (len(tokens) == 10)):
          # Position Read
          arm_inst.gripper.current.count = int(tokens[1])
          arm_inst.wrist_roll.current.count = int(tokens[2])
          arm_inst.wrist_pitch.current.count = int(tokens[3])
          arm_inst.elbow.current.count = int(tokens[4])
          arm_inst.shoulder.current.count = int(tokens[5])
          arm_inst.base.current.count = int(tokens[6])

          print("Position Read")
          print("Gripper: ", arm_inst.gripper.current.count)
