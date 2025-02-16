"""
Module: MonitorGUI.py
Description: Implements the MonitorGUI class providing a multi-tabbed interface for:
             - Process log
             - Joystick monitor
             - Raspberry Pi communications (sent/received messages)
             - MAVLink communications (sent/received messages)
             - Configuration editor (via ConfigEditorFrame)
"""

import tkinter as tk
from tkinter import ttk
import logging
from gui.ConfigEditor import ConfigEditorFrame
from interfaces.UDPChannel import UDPChannel
from gui.TextHandler import TextHandler
# from interfaces.UDPChannel import UDPChannel  # For TextHandler import if needed


class MonitorGUI:
    """
    Main GUI for monitoring the system.
    """
    def __init__(self, missionPlanner):
        self.mp_ = missionPlanner
        self.root_ = tk.Tk()
        self.root_.title("Mission Planner Monitor")
        self.notebook_ = ttk.Notebook(self.root_)
        self.notebook_.pack(expand=True, fill="both")

        # Tab 1: Process Log
        self.tabLog_ = tk.Frame(self.notebook_)
        self.notebook_.add(self.tabLog_, text="Process Log")
        self.logText_ = tk.Text(self.tabLog_, wrap="word")
        self.logText_.pack(expand=True, fill="both")
        self.textHandler_ = TextHandler(self.logText_)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.textHandler_.setFormatter(formatter)
        logging.getLogger().addHandler(self.textHandler_)
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info("Process log started.")


        # Tab 2: Joystick Monitor
        self.tabJoystick_ = tk.Frame(self.notebook_)
        self.notebook_.add(self.tabJoystick_, text="Joystick Monitor")
        self.joystickLabel_ = tk.Label(self.tabJoystick_, text="Joystick Values:\n", justify="left", anchor="w")
        self.joystickLabel_.pack(fill="both", padx=10, pady=10)

        # Tab 3: Raspberry Pi Monitor
        self.tabRaspi_ = tk.Frame(self.notebook_)
        self.notebook_.add(self.tabRaspi_, text="Raspberry Monitor")
        self.raspiText_ = tk.Text(self.tabRaspi_, wrap="word", state="disabled")
        self.raspiText_.pack(expand=True, fill="both")
        self.raspiText_.tag_configure("sent", foreground="green", justify="left")
        self.raspiText_.tag_configure("received", foreground="blue", justify="right")

        # Tab 4: MAVLink Monitor
        self.tabMavlink_ = tk.Frame(self.notebook_)
        self.notebook_.add(self.tabMavlink_, text="MAVLink Monitor")
        self.mavlinkText_ = tk.Text(self.tabMavlink_, wrap="word", state="disabled")
        self.mavlinkText_.pack(expand=True, fill="both")
        self.mavlinkText_.tag_configure("sent", foreground="green", justify="left")
        self.mavlinkText_.tag_configure("received", foreground="blue", justify="right")

        # Tab 5: Configuration Editor
        self.tabConfig_ = tk.Frame(self.notebook_)
        self.notebook_.add(self.tabConfig_, text="Configuration")
        self.configEditor_ = ConfigEditorFrame(self.tabConfig_, self.mp_)
        self.configEditor_.pack(expand=True, fill="both", padx=10, pady=10)

        self.UpdateGUI()

    def UpdateGUI(self):
        js = self.mp_.state_.joystick_
        jsText = (
            f"Joystick X: {js.joystickX_:.2f}\n"
            f"Joystick Y: {js.joystickY_:.2f}\n"
            f"Joystick Z: {js.joystickZ_:.2f}\n"
            f"Button: {js.joystickButton_}\n"
            f"Temperature: {js.temperature_:.2f}"
        )
        self.joystickLabel_.config(text=jsText)

        while not self.mp_.raspiMessageQueue_.empty():
            msgType, message = self.mp_.raspiMessageQueue_.get()
            self.raspiText_.config(state="normal")
            self.raspiText_.insert(tk.END, message + "\n", msgType)
            self.raspiText_.config(state="disabled")
            self.raspiText_.see(tk.END)

        while not self.mp_.mavlinkMessageQueue_.empty():
            msgType, message = self.mp_.mavlinkMessageQueue_.get()
            self.mavlinkText_.config(state="normal")
            self.mavlinkText_.insert(tk.END, message + "\n", msgType)
            self.mavlinkText_.config(state="disabled")
            self.mavlinkText_.see(tk.END)

        self.root_.after(500, self.UpdateGUI)

    def Run(self):
        self.root_.mainloop()
