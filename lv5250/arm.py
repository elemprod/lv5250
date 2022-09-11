
import axis
from axis import LinearAxis, RotaryAxis
from arm_config import ArmConfig


class Arm:

    def __init__(self):
        self.gripper = LinearAxis(
            ArmConfig.GRIPPER_SCALE, ArmConfig.GRIPPER_MIN, ArmConfig.GRIPPER_MAX)

        self.wrist_roll = RotaryAxis(
            ArmConfig.WRIST_ROLL_SCALE, ArmConfig.WRIST_ROLL_MIN, ArmConfig.WRIST_ROLL_MAX)

        self.wrist_pitch = RotaryAxis(
            ArmConfig.WRIST_PITCH_SCALE, ArmConfig.WRIST_PITCH_MIN, ArmConfig.WRIST_PITCH_MAX)

        self.elbow = RotaryAxis(ArmConfig.ELBOW_SCALE,
                                ArmConfig.ELBOW_MIN, ArmConfig.ELBOW_MAX)

        self.shoulder = RotaryAxis(
                ArmConfig.SHOULDER_SCALE, ArmConfig.SHOULDER_MIN, ArmConfig.SHOULDER_MAX)

        self.base = RotaryAxis(ArmConfig.BASE_SCALE,
                               ArmConfig.BASE_MIN, ArmConfig.BASE_MAX)

    # @property
    # def gripper(self):
    #     return self.gripper
    #
    # @gripper.setter
    # def gripper(self, instance):
    #     self.gripper = instance
    #
    # # Wrist Roll Axis
    #
    # @property
    # def wrist_roll(self):
    #     return self.wrist_roll
    #
    # @wrist_roll.setter
    # def wrist_roll(self, instance):
    #     self.wrist_roll = instance
    #
    # # Writst Pitch Axis
    # @property
    # def wrist_pitch(self):
    #     return self.wrist_pitch
    #
    # # Elbow Axis
    # @property
    # def elbow(self):
    #     return self.elbow
    #
    # # Shoulder Axis
    # @property
    # def shoulder(self):
    #     return self.shoulder
    #
    # # Base Axis
    # @property
    # def base(self):
    #     return self.base
