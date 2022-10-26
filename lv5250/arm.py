
import axis
from axis import LinearAxis, RotaryAxis, AxisType
from arm_config import ArmConfig

import enum
from enum import Enum, auto


# Enumneration represnting the ARM's serial connection state.
class ArmConnectionState(Enum):
    UNKNOWN = auto()        # Uknown / Not previously connected
    DISCONNECTED = auto()   # Currently Disconnected.
    CONNECTED = auto()      # Currently Connected


class Arm:

    def __init__(self):

        self.state = ArmConnectionState.UNKNOWN

        # Initialize each Arm Axis with the constants from the ArmConfig
        # Gripper Axis
        self.gripper = LinearAxis(
            ArmConfig.GRIPPER_SCALE, ArmConfig.GRIPPER_MIN, ArmConfig.GRIPPER_MAX)
        # Writst Roll Axis
        self.wrist_roll = RotaryAxis(
            ArmConfig.WRIST_ROLL_SCALE, ArmConfig.WRIST_ROLL_OFFSETT_DEG, ArmConfig.WRIST_ROLL_MIN, ArmConfig.WRIST_ROLL_MAX)
        # Wrist Pitch Axis
        self.wrist_pitch = RotaryAxis(
            ArmConfig.WRIST_PITCH_SCALE, ArmConfig.WRIST_PITCH_OFFSETT_DEG, ArmConfig.WRIST_PITCH_MIN, ArmConfig.WRIST_PITCH_MAX)
        # Elbow Axis
        self.elbow = RotaryAxis(ArmConfig.ELBOW_SCALE, ArmConfig.ELBOW_OFFSETT_DEG,
                                ArmConfig.ELBOW_MIN, ArmConfig.ELBOW_MAX)
        # Shoulder Axis
        self.shoulder = RotaryAxis(
                ArmConfig.SHOULDER_SCALE, ArmConfig.SHOULDER_OFFSETT_DEG,
                ArmConfig.SHOULDER_MIN, ArmConfig.SHOULDER_MAX)
        # Base Axis
        self.base = RotaryAxis(ArmConfig.BASE_SCALE, 0,
                               ArmConfig.BASE_MIN, ArmConfig.BASE_MAX)

    @property
    def axis_deg_abs(self, axis: AxisType) -> float:
        """
        Get the absolute (ground referenced) axis angle.
        """
        pass
        # if axis == AxisType.GRIPPER:
        #
        # elif axis == AxisType.WRIST_ROLL:
        # elif axis == AxisType.ELBOW:
        # elif axis == AxisType.SHOULDER:
        # elif axis == AxisType.BASE:
        #
        # else:
        #     return None


if __name__ == "__main__":
    arm = Arm()
    arm.wrist_pitch.command_deg = 110
    print('Wrist Pitch: {} deg / {} Cnts'.format(arm.wrist_pitch.command_deg,
          arm.wrist_pitch.command))
    arm.wrist_pitch.command_deg = 10
    print('Wrist Pitch: {} deg / {} Cnts'.format(arm.wrist_pitch.command_deg,
          arm.wrist_pitch.command))
    arm.wrist_pitch.command_deg = 175
    print('Wrist Pitch: {} deg / {} Cnts'.format(arm.wrist_pitch.command_deg,
          arm.wrist_pitch.command))
