import enum
from enum import Enum, auto

from lv5250 import *
from lv5250.axis import *
from lv5250.axises import *


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
