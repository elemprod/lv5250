from arm_manager import ArmManager

import arm
import arm_uart

from arm import Arm
from axis import AxisType

from arm_uart import ArmMessage, ArmUART

import queue
import time

import enum
from enum import Enum, auto


class FindHwLimits:
    """
    Find's the Hardware Limit Switch Encoder Positions for each Axis.

    Note that Gripper Axis does not have a limit swithc.
    """

    def __init__(self, port: str):
        print("Arm Find HW Limits Init")
        self.speed = 50
        self.mngr = ArmManager(port)
        # Limit Position Variables
        self.base_min = None
        self.base_max = None
        self.shoulder_min = None
        self.shoulder_max = None
        self.elbow_min = None
        self.elbow_max = None
        self.wrist_pitch_max = None
        self.wrist_pitch_min = None
        self.wrist_roll_max = None
        self.wrist_roll_min = None
        self._active = False

    def active(self):
        return self._active

    def start(self, speed: int):

        self._active = True

        self.speed = int(speed)

        # Send the Remotem, Clear E-Stop 7 HardHome Command's to
        # Initialize the Arm
        self.mngr.remote_cmd()
        self.mngr.clear_estop_cmd()
        self.mngr.hard_home_cmd()

        # Find the Base Limit's
        self.mngr.move_to_limit_cmd(
            AxisType.BASE, self.speed, self._base_max_cb)
        self.mngr.move_to_limit_cmd(
            AxisType.BASE, -self.speed, self._base_min_cb)
        # Move back to the zero position.
        self.mngr.move_to_cmd(self.speed, 0, 0, 0, 0, 0, 0, None)

        # Find the Elbow limits
        self.mngr.move_to_limit_cmd(
            AxisType.ELBOW, self.speed, self._elbow_max_cb)
        self.mngr.move_to_limit_cmd(
            AxisType.ELBOW, -self.speed, self._elbow_min_cb)
        # Move back to the zero position.
        self.mngr.move_to_cmd(self.speed, 0, 0, 0, 0, 0, 0, None)

        # Find the Wrist Pitch Limit's
        self.mngr.move_to_limit_cmd(
            AxisType.WRIST_PITCH, self.speed, self._wrist_pitch_max_cb)
        self.mngr.move_to_limit_cmd(
            AxisType.WRIST_PITCH, -self.speed, self._wrist_pitch_min_cb)

    def _base_max_cb(self, arm: Arm):
        """Find Positive Base Limit Callback """
        self.base_max = arm.base.current
        print('Base Positive Limit {}'.format(arm.base.current))

    def _base_min_cb(self, arm: Arm):
        """Find Negative Base Limit Callback """
        self.base_min = arm.base.current
        print('Base Negative Limit {}'.format(arm.base.current))

    def _elbow_max_cb(self, arm: Arm):
        """Find Positive Elbow Limit Callback """
        self.elbow_max = arm.base.current
        print('Elbow Positive Limit {}'.format(self.elbow_max))

    def _elbow_min_cb(self, arm: Arm):
        """Find Negative Elbow Limit Callback """
        self.elbow_min = arm.elbow.current
        print('Elbow Negative Limit {}'.format(self.elbow_min))

    def _shoulder_max_cb(self, arm: Arm):
        """Find Positive Shoulder Limit Callback """
        self.shoulder_max = arm.shoulder.current
        print('Shoulder Positive Limit {}'.format(self.shoulder_max))

    def _shoulder_min_cb(self, arm: Arm):
        """Find Negative Shoulder Limit Callback """
        self.shoulder_min = arm.shoulder.current
        print('Shoulder Negative Limit {}'.format(self.shoulder_min))

    def _wrist_roll_max_cb(self, arm: Arm):
        """Find Positive Wrist Roll Limit Callback """
        self.wrist_roll_max = arm.wrist_roll.current
        print('Wrist Roll Positive Limit {}'.format(self.wrist_roll_max))

    def _wrist_roll_min_cb(self, arm: Arm):
        """Find Negative Wrist Roll Limit Callback """
        self.wrist_roll_min = arm.wrist_roll.current
        print('Wrist Roll Negative Limit {}'.format(self.wrist_roll_min))

    def _wrist_pitch_max_cb(self, arm: Arm):
        """Find Positive Wrist Pitch Limit Callback """
        self.wrist_pitch_max = arm.wrist_pitch.current
        print('Wrist Pitch Positive Limit {}'.format(self.wrist_pitch_max))

    def _wrist_pitch_min_cb(self, arm: Arm):
        """Find Negative Wrist Pitch Limit Callback """
        self.wrist_pitch_min = arm.wrist_pitch.current
        print('Wrist Pitch Negative Limit {}'.format(self.wrist_pitch_min))
        self.mngr.move_to_cmd(self.speed, 0, 0, 0, 0, 0, 0, None)

        # Pitch the Wrist and Elbow Up in order to avoid hitting the table
        # during the find shoulder limits.
        self.mngr.move_to_cmd(self.speed, 0, 0, 0, 0, 0, 0, None)
        self.mngr.move_to_cmd(self.speed, 0, 0, -20000, 0, 0, 0, None)
        self.mngr.move_to_cmd(self.speed, 0, 0, -20000, -20000, 0, 0, None)

        # #Start the Shoulder limit Find
        self.mngr.move_to_limit_cmd(
            AxisType.SHOULDER, self.speed, self._shoulder_max_cb)
        self.mngr.move_to_limit_cmd(
            AxisType.SHOULDER, -self.speed, self._shoulder_min_cb)
        # Move back to the zero position.Mo
        self.mngr.move_to_cmd(self.speed, 0, 0, 0, 0, 0, 0, self._done_cb)

    def _done_cb(self, arm: Arm):
        """ Final Callback after all moves are complete."""
        print('*** Find HW Limit Complete  ***')
        self._active = False


if __name__ == "__main__":

    # The Serial Port
    PORT = '/dev/cu.usbserial-FT5ZVFRV'

    find_limit = FindHwLimits(PORT)
    find_limit.start(50)
    # Wait for the moves to complete
    while(find_limit.active()):
        time.sleep(1)
