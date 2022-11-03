
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


class Axis:
    """
    Class representing a single robot arm axis position.
    """

    def __init__(self,
                 min_cnt=None,
                 max_cnt=None):

        # The Axis Position in Encoder Counts
        self._counts = 0

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

        # Calculate the effective limits to constrain positions to.
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
            self._limit_max = self._hw_limit_max

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

        The software max limit can be set to less than the hardware max limit
        to constrain the axis positions.
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
        axis positions.
        """
        self._sw_limit_min = int(limit)
        self._update_limit_min()

    def limit_check(self, counts: int) -> int:
        """
        Function for limiting an encoder count value to be within the
        configured software and hardware limits.  Returns the limited
        encoder count value.
        """
        counts = int(counts)
        if self._limit_max is not None and counts > self._limit_max:
            print('{} Limited to {}'.format(counts, self._limit_max))
            return self._limit_max
        elif self._limit_min is not None and counts < self._limit_min:
            print('{} Limited to {}'.format(counts, self._limit_min))
            return self._limit_min
        else:
            return counts

    @property
    def counts(self) -> int:
        """
        Get the axis position in units of encoder counts.
        """
        return self._counts

    @counts.setter
    def counts(self, counts: int):
        """
        Set the axis position in units of encoder counts.

        Note that position is constrained to the Software and
        Hardware Limit's.
        """
        self._counts = self.limit_check(counts)


class RotaryAxis(Axis):
    """
    Data Class representing a single rotary axis.
    """

    def __init__(self,
                 scale: float,
                 offsett: float,
                 min_cnt: int,
                 max_cnt: int):
        super().__init__(min_cnt, max_cnt)
        self._scale = float(scale)
        self._offsett = float(offsett)

    @property
    def scale(self) -> float:
        """
        Get the Axis Scale in units of degrees per encoder count.

        Scale is a constant used to convert a position in units
        of encoder counts to a position in units of degrees.
        postion (degs) = scale (deg/cnt) * position (cnts) + offsett(deg)
        """
        return self._scale

    @property
    def offsett(self) -> float:
        """
        Get the Axis Offsett in units of degrees.

        Offsett is a constant used to convert a position in units
        of encoder counts to a position in units of degrees.
        position (degs) = scale (deg/cnt) * position (cnts) + offsett(deg)
        """
        return self._offsett

    @property
    def degrees(self) -> float:
        """
        Get the axis position in units of rotary degrees.
        """
        return (self.counts * self.scale) + self.offsett

    @degrees.setter
    def degrees(self, degrees: float):
        """
        Set the axis position in units of rotary degrees.
        """
        self.counts = round((degrees - self.offsett) / self.scale)
        #print(f'Offsett {self.offsett}')
        #print(f'Degs Setter {degrees:.1f} / {self.counts}')


class LinearAxis(Axis):
    """
    Data Class representing a single linear axis.

    """

    def __init__(self, scale, min_cnt, max_cnt):
        super().__init__(min_cnt, max_cnt)
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
    def mm(self) -> float:
        """
        Get the counts axis position in units of mm.
        """
        return self.counts * self.scale

    @mm.setter
    def counts_mm(self, mm: float):
        """
        Set the counts axis position in units of mm.
        """
        self.counts = round(mm / self.scale)
