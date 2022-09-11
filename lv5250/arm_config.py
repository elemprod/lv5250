

# LabVolt 5250 Robot Arm Configuration
# Defines the Scale Constants, Min Hardware Limit and Max Hardware
# Limits for each axis.

class ArmConfig:

    # Gripper Axis linear movement scale in units of mm per count
    GRIPPER_SCALE = 0.1
    GRIPPER_MIN = 0
    GRIPPER_MAX = 100000

    # Wrist Rotation scale in units of degrees per count
    WRIST_ROLL_SCALE = 0.01
    WRIST_ROLL_MIN = 0
    WRIST_ROLL_MAX = 100000

    WRIST_PITCH_SCALE = 0.01
    WRIST_PITCH_MIN = 0
    WRIST_PITCH_MAX = 100000

    ELBOW_SCALE = 0.01
    ELBOW_MIN = 0
    ELBOW_MAX = 100000

    SHOULDER_SCALE = 0.01
    SHOULDER_MIN = 0
    SHOULDER_MAX = 100000

    BASE_SCALE = 0.01
    BASE_MIN = 0
    BASE_MAX = 100000
