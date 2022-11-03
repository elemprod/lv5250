
import axis
from axis import LinearAxis, RotaryAxis, AxisType
from arm_config import ArmConfig

import enum
from enum import Enum, auto

from axises import Axises

# Enumneration represnting the ARM's serial connection state.


class ArmConnectionState(Enum):
    UNKNOWN = auto()        # Uknown / Not previously connected
    DISCONNECTED = auto()   # Currently Disconnected.
    CONNECTED = auto()      # Currently Connected


class Arm:

    def __init__(self):

        self.state = ArmConnectionState.UNKNOWN

        """
        The current arm position
        """
        self.position = Axises()

        """
        The commanded Arm Position.
        """
        self.command = Axises()


if __name__ == "__main__":
    arm = Arm()

    print(
        f'Shoulder Offsett {arm.command.shoulder.offsett}, Scale: {arm.command.shoulder.scale}')
    arm.command.shoulder.degrees = 108
    print('Shoulder: {} deg / {} Cnts'.format(arm.command.shoulder.degrees,
          arm.command.shoulder.counts))
