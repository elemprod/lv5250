
import axis
from axis import *
import encoder
from encoder import *
from enum import Enum, auto
# Generate ARM Commands.  All methods return bytes objects.


class ArmCmd:

    def enable(self):
        # enable the motors
        return bytes('TORQUE\r\n', 'utf-8')

    def get_pos(self):
        # enable the motors
        return bytes('GET POS\r\n', 'utf-8')

    # Genertes an incremental move command for signle axis
    def move_inc(self, speed: int, axis: AxisType, counts: int):
        if speed < 1:
            speed = 1
        if speed > 100:
            speed = 100

        ret_str = 'MOVE {} {} {}\r\n'.format(
            str(speed), str(axis.value), str(counts))
        print(ret_str)
        return bytes(ret_str, 'utf-8')

    # Genertes an incremental move command for signle a axis
    def run(self, speed: int, gripper: int, ):
        if speed < 1:
            speed = 1
        if speed > 100:
            speed = 100

        ret_str = 'MOVE {} {} {}\r\n'.format(
            str(speed), str(axis.value), str(counts))
        print(ret_str)
        return bytes(ret_str, 'utf-8')
