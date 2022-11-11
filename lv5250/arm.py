
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
        The current arm position.  Position limits disabled so the position
        is stored even if it is outside of the limts.
        """
        self.position = Axises(False)

        """
        The commanded Arm Position.  Position limits enabled to protect the
        Arm from being commanded to an invalid position.
        """
        self.command = Axises(True)


if __name__ == "__main__":
    arm = Arm()

    print(
        f'Shoulder Offsett {arm.command.shoulder.offsett}, Scale: {arm.command.shoulder.scale}')
    arm.command.shoulder.degrees = 108
    print('Shoulder: {} deg / {} Cnts'.format(arm.command.shoulder.degrees,
          arm.command.shoulder.counts))
