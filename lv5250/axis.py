
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
    Class representing a a single Robot Arm's axis position in native units
    of encoder counts. The axis software and hardware encoder count limits can
    optionally be configured to constrain the axis poisition.

    The hardware limits represent the min and max encoder counts values
    required to protect the hardware for exceeding its mechannical limits and
    tripping the limit switches.  The hardware limits would typically be set
    during initialion.

    The software limits are meant to be dynamic limits which can be
    updated constrain the axis position.

    Parameters:

    cb_update: Callback to make when the encoder value is set.

    min_cnt: The minimuim value to limit encoder count too.

    max_cnt: The maximuim value to limit encoder count too.

    """

    def __init__(
            self,
            cb_update=None,
            min_cnt: int = None,
            max_cnt: int = None):
        # The Axis Position in Encoder Counts
        self._counts = 0
        self._cb_update = cb_update

        # Set the hardware and software limits to the min / max count.
        if min_cnt is None:
            self._hw_cnt_min = None
            self._sw_cnt_min = None
        else:
            self._hw_cnt_min = int(min_cnt)
            self._sw_cnt_min = int(min_cnt)

        if max_cnt is None:
            self._hw_cnt_max = None
            self._sw_cnt_max = None
        else:
            self._hw_cnt_max = int(max_cnt)
            self._sw_cnt_max = int(max_cnt)

    def cnt_max(self) -> int:
        """
        Get the axis maximuim encoder count limit.
        The limit is the lesser of the hardware and software limit.
        """
        if self._hw_cnt_max is None:
            return self._sw_cnt_max
        elif self._sw_cnt_max is None:
            return self._hw_cnt_max
        elif self._sw_cnt_max <= self._hw_cnt_max:
            return self._sw_cnt_max
        else:
            return self._hw_cnt_max

    def cnt_min(self) -> int:
        """
        Get the axis minimuim encoder count limit.
        The limit is the greater of the hardware and software limit.
        """
        if self._hw_cnt_min is None:
            return self._sw_cnt_min
        elif self._sw_cnt_min is None:
            return self._hw_cnt_min
        elif self._sw_cnt_min >= self._hw_cnt_min:
            return self._sw_cnt_min
        else:
            return self._hw_cnt_min

    @property
    def hw_cnt_max(self):
        """
        Get the hardware max limit in units of encoder counts.
        """
        return self._hw_cnt_max

    @hw_cnt_max.setter
    def hw_cnt_max(self, limit: int):
        """
        Set the hardware max limit in units of encoder counts.

        Movement past this limit would trip the hardware limit switch.
        """
        self._hw_cnt_max = limit

    @property
    def sw_cnt_max(self):
        """
        Get the software max limit in units of encoder counts.
        """
        return self._sw_cnt_max

    @sw_cnt_max.setter
    def sw_cnt_max(self, limit: int):
        """
        Set the software max limit in units of encoder counts.

        The software max limit can be set to less than the hardware max limit
        to constrain the axis positions.
        """
        self._sw_cnt_max = limit

    @property
    def hw_cnt_min(self):
        """
        Get the hardware min limit in units of encoder counts.

        Movement past this limit would trip the hardware limit switch.
        """
        return self._hw_cnt_min

    @hw_cnt_min.setter
    def hw_cnt_min(self, limit: int):
        """
        Set the hardware min limit in units of encoder counts.
        """
        self._hw_cnt_min = limit

    @property
    def sw_cnt_min(self):
        """
        Get the axis software min limit in units of encoder counts.
        """
        return self._sw_cnt_min

    @sw_cnt_min.setter
    def sw_cnt_min(self, limit: int):
        """
        Set the axis software min limit in units of encoder counts.

        Can be set to greater than the hardware min limit to constrain the
        axis positions.
        """
        self._sw_cnt_min = limit

    def cnt_limit(self, counts: int) -> int:
        """
        Function for limiting an encoder count value to be within the
        configured software and hardware limits.  Returns the limited
        encoder count value.
        """
        counts = int(counts)
        counts_max = self.cnt_max()
        counts_min = self.cnt_min()
        #print(f'Cnts: {counts}  Min: {counts_min}, Max: {counts_max}')
        if counts_max is not None and counts > counts_max:
            print('{} Counts Limited to {} Counts'.format(
                counts, counts_max))
            return counts_max
        elif counts_min is not None and counts < counts_min:
            print('{} Counts Limited to {} Counts'.format(
                counts, counts_min))
            return counts_min
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
        self._counts = self.cnt_limit(counts)
        if callable(self._cb_update):
            # Make the counts updated call back
            self._cb_update()


class RotaryAxis(Axis):
    """
    Class representing a single rotary axis which can be optionally
    constrained to a maximuim and minimuim encoder count value.  The class
    enables accessing the axis's angular position in units of degrees.  The
    encoder count value is stored in the native units of encoder counts and the
    angular conversion happens during the setter and getter functions.

    Parameters:

    scale:  The axis scaling constant used to convert encoder counts to
    a rotary angle in degrees with units of degrees per encoder count.

    offsett:  The axis offsett from the encoder count zero position in
    units of degrees.

    cb_update: Callback to make when the encodder value is set.

    min_cnt: The minimuim value to limit encoder count too.

    max_cnt: The maximuim value to limit encoder count too.
    """

    def __init__(self,
                 scale: float,
                 offsett: float,
                 cb_update=None,
                 min_cnt: int = None,
                 max_cnt: int = None):
        super().__init__(min_cnt=min_cnt, max_cnt=max_cnt, cb_update=cb_update)
        self._scale = float(scale)
        self._offsett = float(offsett)

    @property
    def scale(self) -> float:
        """
        Get the Axis Scale in units of degrees per encoder count.

        Scale is the constant used to convert a position in units
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
    def angle(self) -> float:
        """
        Get the axis angle in units of angular degrees.
        """
        return self.cnt_to_angle(self.counts)

    @angle.setter
    def angle(self, angle: float):
        """
        Set the axis angle in units of angular degrees.
        """
        self.counts = self.angle_to_cnt(angle)

    @property
    def sw_angle_min(self) -> float:
        """
        Get the software minimuim limit in units degrees.
        """
        return self.cnt_to_angle(self.sw_cnt_min)

    @sw_angle_min.setter
    def sw_angle_min(self, limit: float):
        """
        Set the software minimuim limit in units of degrees.
        """
        self.sw_cnt_min = self.angle_to_cnt(limit)

    @property
    def sw_angle_max(self) -> float:
        """
        Get the software maximuim limit in units degrees.
        """
        return self.cnt_to_angle(self.sw_cnt_max)

    @sw_angle_max.setter
    def sw_angle_max(self, limit: float):
        """
        Set the software maximuim limit in units of degrees.
        """
        self.sw_cnt_max = self.angle_to_cnt(limit)

    def angle_limit_360(self, angle: float) -> float:
        """
        Function for converting an angle outside of +/- 360 deg to the
        equivalent angle limited to that range.
        """
        while angle > 360:
            angle = angle - 360
        while angle < -360:
            angle = angle + 360
        return angle

    def angle_to_cnt(self, angle: float) -> int:
        """
        Function for converting angle in degrees to encoder counts.
        """
        angle = self.angle_limit_360(angle)
        return round((angle - self.offsett) / self.scale)

    def cnt_to_angle(self, counts: int) -> float:
        """
        Function for converting an encoder count value to an angle in degrees.
        """
        return (counts * self.scale) + self.offsett


class RotaryAxisRelative(RotaryAxis):
    """
    Class representing a single rotary axis which is constrained by a
    relative angle to another rotary axis.  The associated axis angle is
    assumed to have a dynamic value.  The axis angle is constrained by
    min and max angles which are relative to the assocated axis.

    Rotary axis angles are stored as a ground referenced (absolute) angles
    to match the robot arm's movement commands.  The Elbow Axis is constrained
    by its relative angle to the Shoulder Axis.  The Wrist Pitch Axis is
    constrained its relative angle to the Elbow Axis. The relative axis
    constraints are need to limit the axis movement commands to avoid
    tripping the hardware limit switches.

    Parameters:

    scale:  The axis scaling constant used to convert encoder counts to
    a rotary angle in degrees with units of degrees per encoder count.

    offsett:  The axis offsett from the encoder count zero position in
    units of degrees.

    cb_update: Callback to make when the encoder value is set.

    rel_angle_func: The function to call to retrieve the current absolute angle
    of the assocated axis in units of degrees.

    rel_angle_min: The minimuin angle between the associated axis and
    the axis in units of degrees.

    rel_angle_max: The maximuin angle between the associated axis and
    the axis in units of degrees.

    """

    def __init__(self,
                 scale: float,
                 offsett: float,
                 cb_update=None,
                 rel_angle_func=None,
                 rel_angle_min: float = None,
                 rel_angle_max: float = None):
        super().__init__(scale=scale, offsett=offsett, cb_update=cb_update)
        self._rel_angle_func = rel_angle_func
        self._rel_angle_min = rel_angle_min
        self._rel_angle_max = rel_angle_max

    def assoc_angle_limit(self, angle: float) -> float:
        """
        Function for constraining a ground referenced axis angle to the
        the relative angle limits.

        """
        if callable(self._rel_angle_func):
            # Get the ground referenced angle for the associated axis.
            assoc_axis_angle = float(self._rel_angle_func())
            if assoc_axis_angle is None:
                print('Associated Angle Function Returned None')
                # return the orignal angle
                return angle
            # Calculate the angle between the associated axis and the axis.
            relative_angle = assoc_axis_angle - angle
            if self._rel_angle_max is not None and relative_angle > self._rel_angle_max:
                # The relative angle between the associated axis and the axis exceeded the max limit.
                print(
                    f'Axis Command {angle:0.1f}, Associated Axis {assoc_axis_angle:0.1f}, Relative Angle: {relative_angle:0.1f} degs')
                return_angle = assoc_axis_angle - self._rel_angle_max
                print(
                    f'Axis Command {angle:0.1f} deg limited to {return_angle:0.1f} deg to meet the {self._rel_angle_max:0.1f} deg constraint.')
                return return_angle
            elif self._rel_angle_min is not None and relative_angle < self._rel_angle_min:
                # The relative angle between the associated axis and the axis
                # was less than the min limit.
                print(
                    f'Axis {angle:0.1f}, Associated Axis Angle {assoc_axis_angle:0.1f}, Relative Angle: {relative_angle:0.1f} degs')
                return_angle = assoc_axis_angle - self._rel_angle_min
                print(
                    f'Axis {angle:0.1f} deg limited to {return_angle:0.1f} deg to meet the {self._rel_angle_min:0.1f} deg constraint.')
                return return_angle
            else:
                return angle
        else:
            # print('Associated Angle Function Not Callable')
            return angle

    def update(self):
        """
        Update the axis angle after making the associated axis relative angle
        limit checks.  This can be called when the associated axis changes to
        limit check the new relative axis angle.
        """
        angle = self.angle
        angle = self.assoc_angle_limit(angle)
        self.counts = self.angle_to_cnt(angle)

    @property
    def angle(self) -> float:
        """
        Get the axis angle in units of angular degrees.
        """
        return self.cnt_to_angle(self.counts)

    @angle.setter
    def angle(self, angle: float):
        """
        Set the axis angle in units of angular degrees.
        The angle is constrained by the relative angle limits.
        """
        angle = self.assoc_angle_limit(angle)
        self.counts = self.angle_to_cnt(angle)


class LinearAxis(Axis):
    """
    Class representing a single linear axis.

    """

    def __init__(self, scale, min_cnt, max_cnt):
        super().__init__(min_cnt=min_cnt, max_cnt=max_cnt)
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
        Get the axis position in units of mm.
        """
        return self.counts * self._scale

    @mm.setter
    def mm(self, mm: float):
        """
        Set the counts axis position in units of mm.
        """
        self.counts = round(mm / self._scale)
