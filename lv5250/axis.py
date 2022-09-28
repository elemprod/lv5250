
import encoder
from encoder import *
import enum
from enum import Enum, auto

# Enumeration for each Axis's Type


class AxisType(Enum):
    GRIPPER = 0
    WRIST_ROLL = 1
    WRIST_PITCH = 2
    ELBOW = 3
    SHOULDER = 4
    BASE = 5

# Enumeration Representing the Axis's current staticmethod(


class AxisState(Enum):
    UNKNOWN = auto()
    STOPPED = auto()
    MOVING = auto()

# Data Class representing a single robot arm axis.


class Axis:
    def __init__(self, scale, min_cnt, max_cnt, state):
        self._state = state
        # Set the hardware and software limits to the min / max count.
        self._hw_limit_max = int(max_cnt)
        self._sw_limit_max = int(max_cnt)
        self._hw_limit_min = int(min_cnt)
        self._sw_limit_min = int(min_cnt)

    # The Current State of the Axis
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = AxisState(state)

    # Encoder position at the axis hardware maximuim limit .  Movement past
    # this position would trip the maximuim limit switch.
    @property
    def hw_limit_max(self):
        return self._hw_limit_max

    @hw_limit_max.setter
    def hw_limit_max(self, limit):
        self._hw_limit_max = int(limit)

    # Encoder position at it's software maximuim limit .
    # Can be programmed to less than the hardware limit to constrain axis positions.
    @property
    def sw_limit_max(self):
        return self._sw_limit_max

    @sw_limit_max.setter
    def sw_limit_max(self, limit):
        self._sw_limit_max = int(limit)

    # Encoder position at it's maximuim limit constrained by the
    # lesser of the hardware and software limit maximuim positions.
    @property
    def limit_max(self):
        if(self._sw_limit_max <= self._hw_limit_max):
            return self._sw_limit_max
        else:
            return self._hw_limit_max

    # Encoder position at the axis hardware minimuim limit .  Movement past
    # this position would trip the minimuim limit switch.
    @property
    def hw_limit_min(self):
        return self._hw_limit_min

    @hw_limit_min.setter
    def hw_limit_min(self, limit):
        self._hw_limit_min = int(limit)

    # Encoder position at the axis software minimuim limit.
    # Can be programmed to greater than the hardware limit to constrain axis positions.
    @property
    def sw_limit_min(self):
        return self._sw_limit_min

    @sw_limit_min.setter
    def sw_limit_min(self, limit):
        self._sw_limit_min = int(limit)

    # Encoder position at it's minimuim limit constrained by the
    # greater of the hardware and software limit minimuim positions.
    @property
    def limit_min(self):
        if(self._sw_limit_min <= self._hw_limit_min):
            return self._sw_limit_min
        else:
            return self._hw_limit_min

# Data Class representing a single rotary axis.
# Contains a collection of encoder objects representing the current position,
# the commanded position, the hardware min and max limit positions annd the
# software min and max limit positions.


class RotaryAxis(Axis):

    def __init__(self, scale, min_cnt, max_cnt, state=AxisState.STOPPED):
        super().__init__(scale, min_cnt, max_cnt, state)

        # The Axis last read encoder postion.
        self.current = encoder.RotaryEncoder(scale, 0)
        # The Axis commanded (target) encoder costion
        self.command = encoder.RotaryEncoder(scale, 0)

# Data Class representing a single linear axis.


class LinearAxis(Axis):

    # encoder_scale scaling factor for converting encoder counts to mm of travel
    def __init__(self, scale, min_cnt, max_cnt, state=AxisState.STOPPED):
        super().__init__(scale, min_cnt, max_cnt, state)

        # The Axis last read encoder postion.
        self.current = encoder.LinearEncoder(scale, 0)
        # The Axis commanded (target) encoder costion
        self.command = encoder.LinearEncoder(scale, 0)
