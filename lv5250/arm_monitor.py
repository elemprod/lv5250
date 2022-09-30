import arm
from arm import Arm

import tkinter as tk
from tkinter import ttk


class ArmMonitor(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("LV5250 Monitor")

        AXIS_TITLE_LBL_WIDTH = 10
        CUR_LBL_WIDTH = 12

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # Variables for the updatable Labels
        self.gripper_cur = tk.StringVar(self)
        self.gripper_cmd = tk.StringVar(self)
        self.wrist_roll_cur = tk.StringVar(self)
        self.wrist_roll_cmd = tk.StringVar(self)
        self.wrist_pitch_cur = tk.StringVar(self)
        self.wrist_pitch_cmd = tk.StringVar(self)
        self.elbow_cur = tk.StringVar(self)
        self.elbow_cmd = tk.StringVar(self)
        self.shoulder_cur = tk.StringVar(self)
        self.shoulder_cmd = tk.StringVar(self)
        self.base_cur = tk.StringVar(self)
        self.base_cmd = tk.StringVar(self)

        # Create the Top Row Titles
        self.title_axis_lbl = ttk.Label(
                master=self, text="Axis", anchor=tk.E, width=AXIS_TITLE_LBL_WIDTH).grid(row=0, column=0)
        self.title_cur_lbl = ttk.Label(
            master=self, text="Current").grid(row=0, column=1)
        self.title_cmd_lbl = ttk.Label(
                    master=self, text="Command").grid(row=0, column=2)

        # Create the Axis Title Labels
        self.gripper_title_lbl = ttk.Label(
            master=self, text="Gripper", anchor=tk.E, width=AXIS_TITLE_LBL_WIDTH).grid(row=1, column=0)
        self.wrist_roll_title_lbl = ttk.Label(
            master=self, text="Wrist Roll", anchor=tk.E, width=AXIS_TITLE_LBL_WIDTH).grid(row=2, column=0)
        self.wrist_pitch_title_lbl = ttk.Label(
            master=self, text="Pitch", anchor=tk.E, width=AXIS_TITLE_LBL_WIDTH).grid(row=3, column=0)
        self.elbow_title_lbl = ttk.Label(
            master=self, text="Elbow", anchor=tk.E, width=AXIS_TITLE_LBL_WIDTH).grid(row=4, column=0)
        self.shoulder_title_lbl = ttk.Label(
            master=self, text="Shoulder", anchor=tk.E, width=AXIS_TITLE_LBL_WIDTH).grid(row=5, column=0)
        self.base_title_lbl = ttk.Label(
            master=self, text="Base", anchor=tk.E, width=AXIS_TITLE_LBL_WIDTH).grid(row=6, column=0)

        # Create the Axis Current Value Labels
        self.gripper_cur_lbl = ttk.Label(
            master=self, textvariable=self.gripper_cur, anchor=tk.CENTER, width=CUR_LBL_WIDTH).grid(row=1, column=1)
        self.wrist_cur_roll_lbl = ttk.Label(
            master=self, textvariable=self.wrist_roll_cur, width=CUR_LBL_WIDTH).grid(row=2, column=1)
        self.wrist_pitch_cur_lbl = ttk.Label(
            master=self, textvariable=self.wrist_pitch_cur, width=CUR_LBL_WIDTH).grid(row=3, column=1)
        self.elbow_cur_lbl = ttk.Label(
            master=self, textvariable=self.elbow_cur, width=CUR_LBL_WIDTH).grid(row=4, column=1)
        self.shoulder_cur_lbl = ttk.Label(
            master=self, textvariable=self.shoulder_cur, width=CUR_LBL_WIDTH).grid(row=5, column=1)
        self.base_cur_lbl = ttk.Label(
            master=self, textvariable=self.base_cur, width=CUR_LBL_WIDTH).grid(row=6, column=1)

        self.gripper_cur.set("0")
        self.wrist_roll_cur.set("0")
        self.wrist_pitch_cur.set("0")
        self.elbow_cur.set("1")

    # Update the Arm Axis
    def update_arm(self, arm: Arm):
        self.gripper_cur.set(str(arm.gripper.current.count))
        self.wrist_roll_cur.set("Test")
        self.elbow_cur.set("4")
        print("update arm")
        #self.update_idletasks()
        #self.update()
