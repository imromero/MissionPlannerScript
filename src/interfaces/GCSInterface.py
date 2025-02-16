"""
Module: GCSInterface.py
Description: Manages communication with the Ground Control Station (GCS) via UDP.
"""

import time
import struct
import logging
from interfaces.UDPChannel import UDPChannel

class GCSInterface:
    """
    Handles GCS communications via UDP.
    
    Attributes:
        metaChannel_ (UDPChannel): Channel for meta data.
        touchChannel_ (UDPChannel): Channel for touch data.
    """
    def __init__(self, udpIpRec, portRecMeta, portRecTouch):
        self.metaChannel_ = UDPChannel(udpIpRec, portRecMeta, isReceiver=True)
        self.touchChannel_ = UDPChannel(udpIpRec, portRecTouch, isReceiver=True)
    
    def TouchAppReceiver(self, state):
        logging.info("GCS interface started.")
        while True:
            try:
                data, address = self.touchChannel_.Receive(1024)
                unpacked = struct.unpack('=iiiiiii', data)
                state.control_.activeControl_ = unpacked[1]
                state.control_.gcsCamera_ = unpacked[2]
                state.control_.nn_ = unpacked[3]
                state.control_.smartDeploy_ = unpacked[4]
                state.control_.gcsCommand1_ = unpacked[5]
                state.control_.gcsCommand2_ = unpacked[6]
                logging.debug(f"GCS active control: {state.control_.activeControl_}")
            except Exception as e:
                logging.error(f"GCS receiver error: {e}")
    
    def GCSControlHandler(self, state, mavlinkInterface):
        while True:
            if state.control_.activeControl_ != 0:
                if state.control_.activeControl_ == 1:
                    state.rc_channels_.cameraValue_ = state.control_.metaCamera_
                    state.gimbal_.deploy12_ = state.control_.metaCommand1_
                    state.gimbal_.deploy34_ = state.control_.metaCommand2_
                    self.GCSCommandsToDrone(state, mavlinkInterface)
                if state.control_.activeControl_ == 2:
                    if state.control_.activeControlPrev_ != 2:
                        state.control_.activeControlPrev_ = state.control_.activeControl_
                        state.gimbal_.pwmPitch_ = state.gimbal_.gimbalPitchNeutral_
                        state.gimbal_.pwmYaw_ = state.gimbal_.gimbalYawNeutral_
                    if state.joystick_.joystickButton_ == 1:
                        state.gimbal_.pwmPitch_ = state.gimbal_.gimbalPitchNeutral_
                        state.gimbal_.pwmYaw_ = state.gimbal_.gimbalYawNeutral_
                    state.rc_channels_.cameraValue_ = state.control_.gcsCamera_
                    state.gimbal_.deploy12_ = state.control_.gcsCommand1_
                    state.gimbal_.deploy34_ = state.control_.gcsCommand2_
                    state.gimbal_.pwmPitch_ += int(state.joystick_.joystickY_ * state.gimbal_.gimbalGain_)
                    state.gimbal_.pwmYaw_ += int(state.joystick_.joystickX_ * state.gimbal_.gimbalGain_)
                    self.GCSCommandsToDrone(state, mavlinkInterface)
            else:
                state.rc_channels_.cameraValue_ = 0
                state.gimbal_.deploy12_ = 0
                state.gimbal_.deploy34_ = 0
                state.gimbal_.pwmPitch_ = 0
                state.gimbal_.pwmYaw_ = 0
    
    def GCSCommandsToDrone(self, state, mavlinkInterface):
        if state.control_.activeControl_ != 0:
            if state.gimbal_.pwmPitch_ > state.gimbal_.pwmPitchMax_:
                state.gimbal_.pwmPitch_ = state.gimbal_.pwmPitchMax_
            if state.gimbal_.pwmPitch_ < state.gimbal_.pwmPitchMin_:
                state.gimbal_.pwmPitch_ = state.gimbal_.pwmPitchMin_
            if state.gimbal_.pwmYaw_ > state.gimbal_.pwmYawMax_:
                state.gimbal_.pwmYaw_ = state.gimbal_.pwmYawMax_
            if state.gimbal_.pwmYaw_ < state.gimbal_.pwmYawMin_:
                state.gimbal_.pwmYaw_ = state.gimbal_.pwmYawMin_
            if state.rc_channels_.cameraValue_ == 1:
                state.rc_channels_.cameraValue_ = 1095
            if state.rc_channels_.cameraValue_ == 2:
                state.rc_channels_.cameraValue_ = 1535
            mavlinkInterface.SendRCChannelPWM(state.gimbal_.deploy12_,
                                              state.gimbal_.deploy34_,
                                              state.rc_channels_.cameraValue_,
                                              state.gimbal_.pwmPitch_,
                                              state.gimbal_.pwmYaw_)
            state.gimbal_.pitchPrev_ = state.gimbal_.pwmPitch_
            time.sleep(0.2)