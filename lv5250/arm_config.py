

class ArmConfig:

    """
    LabVolt 5250 Robot Arm Configuration

    Defines a scale constant which is used for converting an encoder count
    value to an axis angular position in degrees or a linear position in mm.

    The Min / Max Encoder count aree also defined for each axis and represent
    the encoder values required to constrain axis movements to avoid triiggering
    the hardware limit switches.

    Note that the limits are only valid after the Arm has completed a
    Hard Home.
    """

    # Gripper Axis Linear Scale
    # Note that the Gripper Axis does not have a limit switch.  Care must be
    # taken when opening the gripper or it may become stuck open .  The 4 bar
    # mechanical linkage which supports the Gripper pads is driven by a worm
    # gear drive that can not be turned by hand unlike the other axis. If the
    # gripper is openned too far, it may be become stuck open.  The  only
    # solution for unsticking the axis, which we have discovered, is to power
    # the motor in reverse with an external power supply.
    GRIPPER_SCALE = 0.1             # (mm per encoder count)
    GRIPPER_MIN = 0
    GRIPPER_MAX = 100000
    #TODO - gripper limits

    # The Wrist Roll axis has a hardware switch in  the center (neutral)
    # position.  It can be continously rotated without limit.
    # Setting the wrist seeems to require setting two axis, needs mroe work.
    WRIST_ROLL_SCALE = 0.0019       # Angular degrees per encoder count
    WRIST_ROLL_OFFSETT_DEG = 90
    WRIST_ROLL_MIN = None
    WRIST_ROLL_MAX = None

    # Wrist Pitch Axis.  Angle with respect to Elbow Axis.
    WRIST_PITCH_SCALE = -1/567.54    # Angular degrees per encoder count
    WRIST_PITCH_OFFSETT_DEG = 110
    WRIST_PITCH_MIN = -36890        # Counts at Neg. Limit Switch (175 deg)
    WRIST_PITCH_MAX = 56754         # Counts at Pos. Limit Switch (10 deg)

    # The Elbow Axis Angle with Respect to Shoulder Axis
    ELBOW_SCALE = -1/659.785        # Angular degrees per encoder count
    ELBOW_OFFSETT_DEG = -90
    ELBOW_MIN = -146471             # Counts at Neg. Limit Switch (132 deg)
    ELBOW_MAX = 13195               # Counts at Pos. Limit Switch (-110 deg)

    # Shoulder Angle with respect to Base Axis / Ground.
    SHOULDER_SCALE = 1/659.785      # Angular degrees per encoder count
    SHOULDER_OFFSETT_DEG = 108
    SHOULDER_MIN = -104245          # Counts at Neg. Limit Switch (-50 deg)
    SHOULDER_MAX = 2638             # Counts at Pos. Limit Switch (112 deg)

    # Base Rotation
    BASE_SCALE = 1/659.785          # Angular degrees per encoder count
    BASE_MIN = -102266              # Counts at Neg. Limit Switch (-155 deg)
    BASE_MAX = 102266               # Counts at Pos. Limit Switch (155 deg)
