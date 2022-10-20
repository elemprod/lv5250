

class Encoder:
    """
    Data Class representing a single Optical Encoder's state.
    """

    def __init__(self, cnt=0):
        self._count = cnt

    # Encoder Position in Counts
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
