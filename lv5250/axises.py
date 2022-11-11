
import axis
from axis import LinearAxis, RotaryAxis, RotaryAxisRelative, AxisType
from arm_config import ArmConfig


class AxisesGround:

    #TODO no longer valid with new method of referencig all axis to ground.

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

    def __init__(self, limits_en=True):
        """
        Initializes each Arm Axis with the constants from the ArmConfig
        """
        if limits_en:
            # Gripper Axis
            self.gripper = LinearAxis(
                scale=ArmConfig.GRIPPER_SCALE,
                min_cnt=ArmConfig.GRIPPER_MIN,
                max_cnt=ArmConfig.GRIPPER_MAX)

            # Writst Roll Axis
            self.wrist_roll = RotaryAxis(
                scale=ArmConfig.WRIST_ROLL_SCALE,
                offsett=ArmConfig.WRIST_ROLL_OFFSETT_DEG,
                min_cnt=ArmConfig.WRIST_ROLL_MIN,
                max_cnt=ArmConfig.WRIST_ROLL_MAX)

            # Shoulder Axis
            self.shoulder = RotaryAxis(
                scale=ArmConfig.SHOULDER_SCALE,
                offsett=ArmConfig.SHOULDER_OFFSETT_DEG,
                cb_update=self._shoulder_cb_update,
                min_cnt=ArmConfig.SHOULDER_MIN,
                max_cnt=ArmConfig.SHOULDER_MAX)

            # The Elbow Axis is constrained by the relative
            # angle to the Shoulder Axis.
            self.elbow = RotaryAxisRelative(
                scale=ArmConfig.ELBOW_SCALE,
                offsett=ArmConfig.ELBOW_OFFSETT_DEG,
                cb_update=self._elbow_cb_update,
                rel_angle_func=self._shoulder_angle,
                rel_angle_min=ArmConfig.SHOULDER_TO_ELBOW_MIN_DEG,
                rel_angle_max=ArmConfig.SHOULDER_TO_ELBOW_MAX_DEG)

            # The Wrist Pitch Axis is constrained by the relative
            # angle to the Elbow Axis.
            self.wrist_pitch = RotaryAxisRelative(
                scale=ArmConfig.WRIST_PITCH_SCALE,
                offsett=ArmConfig.WRIST_PITCH_OFFSETT_DEG,
                cb_update=None,
                rel_angle_func=self._elbow_angle,
                rel_angle_min=ArmConfig.ELBOW_TO_WRIST_PITCH_MIN_DEG,
                rel_angle_max=ArmConfig.ELBOW_TO_WRIST_PITCH_MAX_DEG
                )

            # Base Axis
            self.base = RotaryAxis(
                scale=ArmConfig.BASE_SCALE,
                offsett=ArmConfig.BASE_OFFSETT_DEG,
                min_cnt=ArmConfig.BASE_MIN,
                max_cnt=ArmConfig.BASE_MAX)
        else:
            # Configure the Axis with No Limits

            self.gripper = LinearAxis(
                ArmConfig.GRIPPER_SCALE, None, None)

            self.wrist_roll = RotaryAxis(
                ArmConfig.WRIST_ROLL_SCALE,
                ArmConfig.WRIST_ROLL_OFFSETT_DEG, None, None)

            self.shoulder = RotaryAxis(
                ArmConfig.SHOULDER_SCALE,
                ArmConfig.SHOULDER_OFFSETT_DEG, None, None)

            self.elbow = RotaryAxis(
                ArmConfig.ELBOW_SCALE,
                ArmConfig.ELBOW_OFFSETT_DEG, None, None)

            self.wrist_pitch = RotaryAxis(
                ArmConfig.WRIST_PITCH_SCALE,
                ArmConfig.WRIST_PITCH_OFFSETT_DEG, None, None)

            self.base = RotaryAxis(
                ArmConfig.BASE_SCALE,
                ArmConfig.BASE_OFFSETT_DEG, None, None)

    def _shoulder_angle(self):
        """
        Returns the current ground referenced shoulder angle in degrees.
        """
        return self.shoulder.angle

    def _shoulder_cb_update(self):
        """
        Shoulder update callback implementation.

        Both the Elbow and Wrist Pitch Axis must be updated following a
        Shoulder Axis update since their positions are constrained by the
        elbow axis.
        """
        self.elbow.update()

    def _elbow_angle(self):
        """
        Returns the current ground referenced elbow angle in degrees.
        """
        return self.elbow.angle

    def _elbow_cb_update(self):
        """
        Elbow update callback implementation.

        The Wrist Pitch Axis must be updated following a Elbow Axis update
        since its position is constrained by the Elbow Axis position.
        """
        self.wrist_pitch.update()
