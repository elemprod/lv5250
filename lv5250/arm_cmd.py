
import axis
from axis import *
import encoder
from encoder import *
from enum import Enum, auto
# Generate ARM Commands.  All methods return bytes objects.


class ArmCmd:
    # Genertes an incremental move command for signle a axis
    def move_inc(self, speed: int, axis: AxisType, counts: int):
        if speed < 1:
            speed = 1
        if speed > 100:
            speed = 100

        ret_str = 'MOVE {} {} {}\r'.format(
            str(speed), str(int(axis)), str(counts))
        print(ret_str)
        return bytes(ret_str, 'utf-8')
