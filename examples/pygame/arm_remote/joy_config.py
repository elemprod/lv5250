import lv5250
from lv5250 import *
from lv5250.axis import *


class JoyKeyMap:
    def __init__(self, counts: int, axis: AxisType):
        # Number of counts to move the axis by
        self.counts = int(counts)
        # Which axis to move move when the button is pressed.
        self.axis = AxisType(axis)


class JoyConfig:

    def __init__(self):
        # Buttons
        self.buttons = [
            # Button 0
            JoyKeyMap(-40000, AxisType.ELBOW),
            # Button 1
            JoyKeyMap(-40000, AxisType.WRIST_PITCH),
            # Button 2
            JoyKeyMap(40000, AxisType.ELBOW),
            # Button 3
            JoyKeyMap(40000, AxisType.WRIST_PITCH),
            # Button 4
            JoyKeyMap(-40000, AxisType.SHOULDER),
            # Button 5
            JoyKeyMap(40000, AxisType.SHOULDER),
            # Button 6
            JoyKeyMap(40000, AxisType.BASE),
            # Button 7
            JoyKeyMap(-40000, AxisType.BASE),
            # Button 8
            None,
            # Button 9
            None,
            # Button 10
            None,
            # Button 11
            None
        ]
