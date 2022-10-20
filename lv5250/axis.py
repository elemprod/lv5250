
from encoder import Encoder
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
    def __init__(self,
                 min_cnt=None,
                 max_cnt=None,
                 state=AxisState.UNKNOWN):

        self._state = state

# TODO I'm not sure the encoder objec is adding any value with the way its current implemented

        # The Axis Current Encoder Position.
        self._current = Encoder(0)

        # The Axis Commanded Encoder Position.
        self._command = Encoder(0)

        # Set the hardware and software limits to the min / max count.
        if min_cnt is None:
            self._hw_limit_min = None
            self._sw_limit_min = None
        else:
            self._hw_limit_min = int(min_cnt)
            self._sw_limit_min = int(min_cnt)

        if max_cnt is None:
            self._hw_limit_max = None
            self._sw_limit_max = None
        else:
            self._hw_limit_max = int(max_cnt)
            self._sw_limit_max = int(max_cnt)

        # Calculate the effective limits to constrain commands to.
        self._update_limit_max()
        self._update_limit_min()

    def _update_limit_max(self):
        """
        Function for updating the axis maximuim encoder count limit to be the
        lesser of the hardware and software limit.
        """
        if self._hw_limit_max is None:
            self._limit_max = self._sw_limit_max
        elif self._sw_limit_max <= self._hw_limit_max:
            self._limit_max = self._sw_limit_max
        else:
            return self._hw_limit_max

    def _update_limit_min(self):
        """
        Function for updating the axis minimuim encoder count limit to be the
        greater of the hardware and software limit.
        """
        if self._hw_limit_min is None:
            self._limit_min = self._sw_limit_min
        elif self._sw_limit_min >= self._hw_limit_min:
            self._limit_min = self._sw_limit_min
        else:
            self._limit_min = self._hw_limit_min

    # The Current State of the Axis
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = AxisState(state)

    @property
    def hw_limit_max(self):
        """
        Get the hardware max limit in units of encoder counts.
        """
        return self._hw_limit_max

    @hw_limit_max.setter
    def hw_limit_max(self, limit):
        """
        Set the hardware max limit in units of encoder counts.

        Movement past this limit would trip the hardware limit switch.
        """
        self._hw_limit_max = int(limit)
        self._update_limit_max()

    @property
    def sw_limit_max(self):
        """
        Get the software max limit in units of encoder counts.
        """
        return self._sw_limit_max

    @sw_limit_max.setter
    def sw_limit_max(self, limit):
        """
        Set the software max limit in units of encoder counts.

        The software max limit be set to less than the hardware max limit to
        constrain the axis positions which can be commanded.
        """
        self._sw_limit_max = int(limit)
        self._update_limit_max()

    @property
    def hw_limit_min(self):
        """
        Get the hardware min limit in units of encoder counts.

        Movement past this limit would trip the hardware limit switch.
        """
        return self._hw_limit_min

    @hw_limit_min.setter
    def hw_limit_min(self, limit):
        """
        Set the hardware min limit in units of encoder counts.
        """
        self._hw_limit_min = int(limit)
        self._update_limit_min()

    @property
    def sw_limit_min(self):
        """
        Get the axis software min limit in units of encoder counts.
        """
        return self._sw_limit_min

    @sw_limit_min.setter
    def sw_limit_min(self, limit):
        """
        Set the axis software min limit in units of encoder counts.

        Can be set to greater than the hardware min limit to constrain the
        axis positions which can be commanded.
        """
        self._sw_limit_min = int(limit)
        self._update_limit_min()

    def limit_check(self, counts: int) -> int:
        """
        Function for limiting an Encoder Count Value to be within the configured
        software and hardware limits.  Returns the limited encoder count value.
        """
        if self._limit_max is not None and counts > self._limit_max:
            return self._limit_max
        elif self._limit_max is not None and counts < self._limit_min:
            return self._limit_min
        else:
            return counts

    @property
    def current(self) -> int:
        """
        Get the axis current position in units of encoder counts.
        """
        return self._current.count

    @current.setter
    def current(self, count: int):
        """
        Set the axis current position in units of encoder counts.
        """
        self._current.count = int(count)

    @property
    def command(self) -> int:
        """
        Get the axis commanded position in units of encoder counts.
        """
        return self._command.count

    @command.setter
    def command(self, count: int):
        """
        Set the axis commanded position in units of encoder counts.

        Note that commanded position is constrained to the Software and
        Hardware Limit's.
        """
        self._command.count = self.limit_check(int(count))


class RotaryAxis(Axis):
    """
    Data Class representing a single rotary axis.
    """

    def __init__(self, scale: float, min_cnt: int, max_cnt: int, state=AxisState.STOPPED):
        super().__init__(min_cnt, max_cnt, state)
        self._scale = float(scale)

    @property
    def scale(self) -> float:
        """
        Get the Axis Scale

        Scale is a constant used to convert a position in units
        of encoder counts to a position in units of degrees.
        postion (degs) = scale * position (cnts)
        """
        return self._scale

    @property
    def current_deg(self) -> float:
        """
        Get the current axis position in units of rotary degrees.
        """
        return self.current.count * self.scale

    @current_deg.setter
    def current_deg(self, degrees: float):
        """
        Set the current axis position in units of rotary degrees.
        """
        self.current.count = round(degrees / self.scale)

    @property
    def command_deg(self) -> float:
        """
        Get the commanded axis position in units of rotary degrees.
        """
        return self.command.count * self.scale

    @command_deg.setter
    def command_deg(self, degrees: float):
        """
        Set the commanded axis position in units of rotary degrees.
        """
        self.command.count = round(degrees / self.scale)


class LinearAxis(Axis):
    """
    Data Class representing a single rotary axis.

    """

    def __init__(self, scale, min_cnt, max_cnt, state=AxisState.STOPPED):
        super().__init__(min_cnt, max_cnt, state)
        self._scale = float(scale)

    @property
    def scale(self) -> float:
        """
        Get the Axis Scale

        Scale is a constant used to convert a position in units of
        encoder counts to a position in units of milimeters.
        postion in mm = scale * position in counts
        """
        return self._scale

    @property
    def current_mm(self) -> float:
        """
        Get the current axis position in units of mm.
        """
        return self.current.count * self.scale

    @current_mm.setter
    def current_mm(self, mm: float):
        """
        Set the current axis position in units of mm.
        """
        self.current.count = round(mm / self.scale)

    @property
    def command_mm(self) -> float:
        """
        Get the commanded axis position in units of mm.
        """
        return self.command.count * self.scale

    @command_mm.setter
    def command_mm(self, mm: float):
        """
        Set the commanded axis position in units of mm.
        """
        self.command.count = round(mm / self.scale)
