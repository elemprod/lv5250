
import axis
from axis import LinearAxis, RotaryAxis, AxisType
from arm_config import ArmConfig

import enum
from enum import Enum, auto

from axises import Axises

#


class ArmConnectionState(Enum):
    """The Arm's current serial connection state. """
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
