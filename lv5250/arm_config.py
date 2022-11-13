
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
    Hard Home movement at power up to set it's internal zero points.

    Note that Robot Arm must be a calibrated using the hand pendant.  The
    calibration procedure is described in the following video.

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
    WRIST_ROLL_OFFSETT_DEG = 0     # Roll angle at zero counts.
    WRIST_ROLL_MIN = None
    WRIST_ROLL_MAX = None

    # Wrist Pitch Axis.  Angle with respect to the Base Axis / Ground.
    WRIST_PITCH_SCALE = -1/567.54   # Angular degrees per encoder count
    WRIST_PITCH_OFFSETT_DEG = 0     # Wrist to elbow angle at zero counts.
    ELBOW_TO_WRIST_PITCH_MIN_DEG = -60    # Minimuin Relative Angle
    ELBOW_TO_WRIST_PITCH_MAX_DEG = 85     # Maximuin relative Angle

    # The Elbow Axis Angle with respect to ground.
    ELBOW_SCALE = -1/659.785        # Angular degrees per encoder count
    ELBOW_OFFSETT_DEG = 0           # Elbow angle at zero counts.

    # Elbow Axis position must be constrained with respect the the
    # shoulder axis angle to avoid tripping the limit switch.
    SHOULDER_TO_ELBOW_MIN_DEG = -125    # Minimuin Relative Angle
    SHOULDER_TO_ELBOW_MAX_DEG = 125     # Maximuin relative Angle

    # Shoulder Axis Angle with respect to Ground.
    SHOULDER_SCALE = 1/659.785      # Angular degrees per encoder count
    SHOULDER_OFFSETT_DEG = 108      # Shoulder angle at zero counts.
    SHOULDER_MIN = -91058           # Counts at Neg. Limit Switch (-30 deg)
    SHOULDER_MAX = 7928             # Counts at Pos. Limit Switch (120 deg)

    # Base Rotation
    BASE_SCALE = 1/659.785          # Angular degrees per encoder count
    BASE_OFFSETT_DEG = 0
    BASE_MIN = -102266              # Counts at Neg. Limit Switch (-155 deg)
    BASE_MAX = 102266               # Counts at Pos. Limit Switch (155 deg)
