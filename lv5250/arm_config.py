

class ArmConfig:

    """
    LabVolt 5250 Robot Arm Configuration

    Defines the scale constant for converting an encoder count reading to
    axis roation position in degreess or linear movement in mm.

    The Min / Max Encoder count is also defined for each axis as required to
    constrain axis movements to avoid tripiing the hardware limit switches.

    The Min / Max Encoder values were determined experimentally by running the
    find_hw_limits.py program.
    """

    # Gripper Axis Linear Scale
    GRIPPER_SCALE = 0.1             # (mm per encoder count)
    GRIPPER_MIN = 0
    GRIPPER_MAX = 100000
    #TODO - gripper limits

    # The Wrist Roll axis has a hardware switch in center (neutral)
    # position and it can be continously rotated without limit.
    WRIST_ROLL_SCALE = 0.0019       # (degs of rotation per count)
    WRIST_ROLL_MIN = None
    WRIST_ROLL_MAX = None

    WRIST_PITCH_SCALE = 0.01        # (degs of rotation per count)
    WRIST_PITCH_MIN = -43000
    WRIST_PITCH_MAX = 43000

    ELBOW_SCALE = 0.0015            # (degs of rotation per count)
    ELBOW_MIN = -160000
    ELBOW_MAX = 0

    SHOULDER_SCALE = 0.0015         # (degs of rotation per count)
    SHOULDER_MIN = -103000
    SHOULDER_MAX = 1800

    # Base Rotation
    BASE_SCALE = 0.0015             # (degs of rotation per count)
    BASE_MIN = -103000              # Measured as -104826
    BASE_MAX = 103000
