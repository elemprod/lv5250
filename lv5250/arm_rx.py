import arm
from arm import *

from enum import Enum

#Serial RX Processor Class


class Arm_Rx:

    def rx(rx: str, arm_inst: arm):
        arm.base.counts = 0
