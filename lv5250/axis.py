import encoder
from encoder import *
from enum import Enum, auto

# Enumeration Representing the Axis's current staticmethod(


class AxisState(enum):
    UNKNOWN = auto()
    STOPPED = auto()
    MOVING = auto()

# Data Class representing a single robot arm axis.


class Axis(object):
    def __init__(self, state):
        self.state = state

    # The Current State of the Axis
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = AxisState(state)

# Data Class representing a single rotary axis.


class RotaryAxis(Axis):

    def __init__(self, scale, min_cnt, max_cnt, state=AxisState.STOPPED):
        self.state = state
        self._current = encoder.RotaryEncoder(scale)
        self._command = encoder.RotaryEncoder(scale)

        # Set the hardware and software limits to the max count.
        self._hw_limit_max = encoder.RotaryEncoder(scale, int(max_cnt))
        self._sw_limit_max = encoder.RotaryEncoder(scale, int(max_cnt))

        # Set the hardware and software limits to the min count.
        self._hw_limit_min = encoder.RotaryEncoder(scale, int(min_cnt))
        self._sw_limit_min = encoder.RotaryEncoder(scale, int(min_cnt))

        # Current Axis Position
        @property
        def current(self):
            return self._current

        # Commanded Axis Position (Target or Goal Position)
        @property
        def command(self):
            return self._command

        # Encoder position at the axis hardware maximuim limit .  Movement past
        # this position would trip the maximuim limit switch.
        @property
        def hw_limit_max(self):
            return self._hw_limit_max

        # Encoder position at it's software maximuim limit .
        # Can be programmed to less than the hardware limit to constrain axis positions.
        @property
        def sw_limit_max(self):
            return self._sw_limit_max

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

        # Encoder position at the axis software minimuim limit.
        # Can be programmed to greater than the hardware limit to constrain axis positions.
        @property
        def sw_limit_min(self):
            return self._sw_limit_min

        # Encoder position at it's minimuim limit constrained by the
        # greater of the hardware and software limit minimuim positions.
        @property
        def limit_min(self):
            if(self._sw_limit_min <= self._hw_limit_min):
                return self._sw_limit_min
            else:
                return self._hw_limit_min

# Data Class representing a single linear axis.


class LinearAxis(Axis):

    # encoder_scale scaling factor for converting encoder counts to degrees
    def __init__(self, scale, state=AxisState.STOPPED):
        self.state = state
        self._current = encoder.LinearEncoder(scale)
        self._command = encoder.LinearEncoder(scale)

        # Current Axis Postion
        @ property
        def current(self):
            return self._current

        # Commanded Axis Position
        @ property
        def command(self):
            return self._command
