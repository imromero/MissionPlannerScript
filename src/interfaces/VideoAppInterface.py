"""
Module: VideoAppInterface.py
Description: Sends telemetry and other state data from the Mission Planner to a video application via UDP.
"""

import struct
from interfaces.UDPChannel import UDPChannel

class VideoAppInterface:
    """
    Manages sending data to the video application.
    """
    def __init__(self, udpIpRec, txPortVideoApp):
        self.txChannel_ = UDPChannel(udpIpRec, txPortVideoApp, isReceiver=False)
        self.udpIpRec_ = udpIpRec
        self.txPortVideoApp_ = txPortVideoApp

    def MissionPlannerToVideoApp(self, state):
        while True:
            videoappData = struct.pack('ffiff',
                                       state.telemetry_.altitude_,
                                       state.battery_.batteryRemaining_,
                                       state.control_.nnToggle_,
                                       state.telemetry_.accelZ_,
                                       state.joystick_.temperature_)
            self.txChannel_.Send(videoappData, self.udpIpRec_, self.txPortVideoApp_)