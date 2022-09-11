

# Data Class representing a single Optical Encoder's state.
class Encoder:

    def __init__(self, cnt=0):
        self._count = cnt

    # Current Encoder's Absolute Position in Counts
    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, cnt):
        self._count = int(cnt)

    # Comparison Overloaded Operators
    def __lt__(self, other):
        return self._count < other.count

    def __le__(self, other):
        return self._count <= other.count

    def __eq__(self, other):
        return self._count == other.count

    def __ne__(self, other):
        return self._count != other.count

    def __gt__(self, other):
        return self._count > other.count

    def __ge__(self, other):
        return self._count >= other.count

# Data Class representing a single Rotary Encoder's Postiion.
# A Rotary Ecoders positions can be accessed in units of both degrees
# and encoder counts.


class RotaryEncoder(Encoder):

    def __init__(self, scale, count=0):
        super().__init__(count)
        self._scale = float(scale)

    # Scaling Factor used to convert an absolute position in units of encoder
    # counts to an aboslute position in units of degrees.
    # postion in degrees = scale * position in counts
    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, scale):
        self._scale = float(scale)

    # The encoder's current absolute position in units of degrees.
    @property
    def position(self):
        return self.count * self._scale

    @position.setter
    def position(self, degrees):
        self.count = round(degrees / self._scale)

# Data Class representing a single Linear Encoder's Postiion.
# A Linear Ecoder's positions can be accessed in units of both mm
# and encoder counts.


class LinearEncoder(Encoder):

    def __init__(self, scale, count=0):
        super().__init__(int(count))
        self._scale = float(scale)

    # Scaling Factor used to convert an absolute position in units of encoder
    # counts to an aboslute position in units of milimeters.
    # postion in mm = scale * position in counts
    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, scale):
        self._scale = float(scale)

    # The encoder's current absolute position in units of mm.
    @property
    def position(self):
        return self.count * self._scale

    @position.setter
    def position(self, mm):
        self.count = round(mm / self._scale)
