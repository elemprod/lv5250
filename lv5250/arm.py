
import axis
from axis import *


class Arm(object):

    # LabVolt 5250 Robot Arm Axis Scale Constant
    GRIPPER_SCALE = 0.1
    WRIST_ROLL_SCALE = 0.01
    WRIST_PITCH_SCALE = 0.01
    ELBOW_SCALE = 0.01
    SHOULDER_SCALE = 0.01
    BASE_SCALE = 0.01

    def __init__(self,
                 gripper_scale,
                 wrist_roll_scale,
                 wrist_pitch_scale,
                 elbow_scale,
                 shoulder_scale,
                 base_scale):
        self._gripper = LinearAxis(gripper_scale)
        self._wrist_roll = RotaryAxis(wrist_roll_scale)

    # Gripper Axis
    gripper = axis.Axis()
    # Wrist Roll Axis
    wrist_roll = axis.Axis()
    #Writst Pitch Axis
    wrist_pitch = axis.Axis()
    # Elbow Axis
    elbow = axis.Axis()
    # Shoulder Axis
    shoulder = axis.Axis()
    # Base Axis
    base = axis.Axis()

    @property
    def gripper(self):
        return self.gripper

    @property
    def wrist_roll(self):
        return self.wrist_roll

    @property
    def wrist_pitch(self):
        return self.wrist_pitch

    @property
    def elbow(self):
        return self.elbow

    @property
    def shoulder(self):
        return self.shoulder

    @property
    def base(self):
        return self.base
