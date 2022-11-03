
import axis
from axis import LinearAxis, RotaryAxis, AxisType
from arm_config import ArmConfig


class AxisesGround:

    """
    Class representing the angle of each axises in degrees referenced to
    the ground or the absolute axis angle.  The angle of each axis with
    respect to ground is dependent  the sume on the angles of the previous
    joints and therefore must be calculated.

    Parameters:
    wrist_pitch: The absolute angle of the wrist in degrees.
    elbow: The absolute angle of the eblow in degrees.
    shoulder: The absolute angle of the shoulder in degrees.
    """

    def __init__(self, wrist_pitch: float, elbow: float, shoulder: float):
        self.wrist_pitch = wrist_pitch
        self.elbow = elbow
        self.shoulder = shoulder


class Axises:
    """
    Class representing a collection LabVolt 5250 robot axis positions.

    Can be used to represent a desired arm position or the current arm
    position.
    """

    def __init__(self):
        """
        Initializes each Arm Axis with the constants from the ArmConfig
        """
        # Gripper Axis
        self.gripper = LinearAxis(
            ArmConfig.GRIPPER_SCALE,
            ArmConfig.GRIPPER_MIN,
            ArmConfig.GRIPPER_MAX)

        # Writst Roll Axis
        self.wrist_roll = RotaryAxis(
            ArmConfig.WRIST_ROLL_SCALE,
            ArmConfig.WRIST_ROLL_OFFSETT_DEG,
            ArmConfig.WRIST_ROLL_MIN,
            ArmConfig.WRIST_ROLL_MAX)

        # Wrist Pitch Axis
        self.wrist_pitch = RotaryAxis(
            ArmConfig.WRIST_PITCH_SCALE,
            ArmConfig.WRIST_PITCH_OFFSETT_DEG,
            ArmConfig.WRIST_PITCH_MIN,
            ArmConfig.WRIST_PITCH_MAX)

        # Elbow Axis
        self.elbow = RotaryAxis(
            ArmConfig.ELBOW_SCALE,
            ArmConfig.ELBOW_OFFSETT_DEG,
            ArmConfig.ELBOW_MIN,
            ArmConfig.ELBOW_MAX)

        # Shoulder Axis
        self.shoulder = RotaryAxis(
            ArmConfig.SHOULDER_SCALE,
            ArmConfig.SHOULDER_OFFSETT_DEG,
            ArmConfig.SHOULDER_MIN,
            ArmConfig.SHOULDER_MAX)

        # Base Axis
        self.base = RotaryAxis(
            ArmConfig.BASE_SCALE,
            ArmConfig.BASE_OFFSETT_DEG,
            ArmConfig.BASE_MIN,
            ArmConfig.BASE_MAX)

    @property
    def absolute(self) -> AxisesGround:
        """
        Get the absolute / ground referenced angle of an axises in degrees.

        """
        shoulder = self.shoulder.degrees
        elbow = shoulder + self.elbow.degrees
        wrist_pitch = elbow + self.wrist_pitch.degrees
        return AxisesGround(wrist_pitch, elbow, shoulder)

    #tood setter
