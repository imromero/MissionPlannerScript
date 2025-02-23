
import struct
from interfaces.UDPChannel import UDPChannel
import time
import logging

class VideoAppInterface:
    def __init__(self, udpIpRec, txPortVideoApp):
        self.logger = logging.getLogger("Video Interface")
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
            time.sleep(0.05)