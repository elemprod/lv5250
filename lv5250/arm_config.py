
class ArmConfig:

    """
    LabVolt 5250 Robot Arm Configuration

    Defines scaling and offsett constants which are used to convert an encoder
    count value to an axis angular position in degrees or a linear position in
    mm.  The axis reference angles were choose to math the LabVolt Windows
    control program.

    Minimuim and Maximuim Encoder count vales are also defined for each axis
    and represent the encoder count value limits required to constrain axis
    movements to avoid triiggering the hardware limit switches.

    Note that the specified limits are only valid after the Arm has completed a
    Hard Home movement to set it's zero points.

    Note that Robot Arm must be a calibrated for best results.

    https://youtu.be/ErEE73Acwwg
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
    GRIPPER_MIN = None
    GRIPPER_MAX = None
    #TODO - gripper limits

    # The Wrist Roll axis has a hardware switch in the center (neutral)
    # position.  It can be continously rotated without limit.
    # A value of None is used for the Min and Max limits to disable them.
    WRIST_ROLL_SCALE = 0.0019       # Angular degrees per encoder count
    WRIST_ROLL_OFFSETT_DEG = 90     # Roll angle at zero counts.
    WRIST_ROLL_MIN = None
    WRIST_ROLL_MAX = None

    # Wrist Pitch Axis.  Angle with respect to Elbow Axis.
    WRIST_PITCH_SCALE = -1/567.54   # Angular degrees per encoder count
    WRIST_PITCH_OFFSETT_DEG = 0   # Wrist to elbow angle at zero counts.
    WRIST_PITCH_MIN = -39728        # Counts at Neg. Limit Switch (70 deg)
    WRIST_PITCH_MAX = 25540         # Counts at Pos. Limit Switch (-45 deg)

    # The Elbow Axis Angle with Respect to Shoulder Axis
    ELBOW_SCALE = -1/659.785        # Angular degrees per encoder count
    ELBOW_OFFSETT_DEG = -90         # Elbow to shoulder angle at zero counts.

    # Note the nominal offsett value of -90 deg may not be perfectly match a
    # particular arm since the limit switch position is adjustable.
    ELBOW_MIN = -146471             # Counts at Neg. Limit Switch (132 deg)
    ELBOW_MAX = 13195               # Counts at Pos. Limit Switch (-110 deg)

    # Shoulder Angle with respect to Base Axis / Ground.
    SHOULDER_SCALE = 1/659.785      # Angular degrees per encoder count
    SHOULDER_OFFSETT_DEG = 108      # Shoulder to ground angle at zero counts.

    # Note the nominal offsett value of 108 deg may not be perfectly match a
    # particular arm since the limit switch position is adjustable.  A more
    # exact value can be determined by adjusting this offsett so the arm's
    # position at the 0 and 98 deg points matches that measured with a level.
    SHOULDER_MIN = -104245          # Counts at Neg. Limit Switch (-50 deg)
    SHOULDER_MAX = 2638             # Counts at Pos. Limit Switch (112 deg)

    # Base Rotation
    BASE_SCALE = 1/659.785          # Angular degrees per encoder count
    BASE_OFFSETT_DEG = 0
    BASE_MIN = -102266              # Counts at Neg. Limit Switch (-155 deg)
    BASE_MAX = 102266               # Counts at Pos. Limit Switch (155 deg)
