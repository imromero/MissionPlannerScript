"""
Module: MissionPlanner.py
Description: Orchestrates the entire system by loading configuration, initializing state and interfaces,
             and starting all communication threads and the GUI.
"""

import threading
import queue
import logging
import subprocess
import sys
from ConfigLoader import ConfigLoader
from state.DroneState import DroneState
from interfaces.MavLinkInterface import MavlinkInterface
from interfaces.GCSInterface import GCSInterface
from interfaces.Raspinterface import RaspiInterface
from interfaces.UsbJoystickInterface import USBJoystickInterface
from interfaces.VideoAppInterface import VideoAppInterface
from interfaces.MetaInterface import MetaInterface
from gui.MonitorGUI import MonitorGUI

class MissionPlanner:
    """
    Orchestrates the Mission Planner system.
    
    Attributes:
        config_ (ConfigLoader): Loaded configuration parameters.
        state_ (DroneState): Current state of the drone.
        raspiMessageQueue_ (Queue): Queue for Raspberry Pi messages.
        mavlinkMessageQueue_ (Queue): Queue for MAVLink messages.
        Interface objects for communication.
    """
    def __init__(self):

        logging.basicConfig(level=logging.DEBUG)
        logging.info("Starting Mission Planner...")
        self.config_ = ConfigLoader("config.xml")
        self.raspiMessageQueue_ = queue.Queue()
        self.mavlinkMessageQueue_ = queue.Queue()
        self.state_ = DroneState()
        self.state_.id_ = self.config_.id_
        self.state_.rc_channels_.rcChannelPitch_ = self.config_.channelPitch_
        self.state_.rc_channels_.rcChannelYaw_ = self.config_.channelYaw_
        self.state_.rc_channels_.rcChannelCam_ = self.config_.channelCam_
        self.state_.rc_channels_.rcChannelDeploy1_ = self.config_.channelDeploy1_
        self.state_.rc_channels_.rcChannelDeploy2_ = self.config_.channelDeploy2_
        self.state_.gimbal_.gimbalGain_ = self.config_.gain_
        self.state_.gimbal_.gimbalPitchNeutral_ = self.config_.pitchNeutral_
        self.state_.gimbal_.gimbalYawNeutral_ = self.config_.yawNeutral_
        self.state_.gimbal_.pwmPitchMin_ = self.config_.pwmPitchMin_
        self.state_.gimbal_.pwmPitchMax_ = self.config_.pwmPitchMax_
        self.state_.gimbal_.pwmYawMin_ = self.config_.pwmYawMin_
        self.state_.gimbal_.pwmYawMax_ = self.config_.pwmYawMax_

        self.mavlinkInterface_ = MavlinkInterface(self.state_, self.config_.mavlinkConnection_)
        self.mavlinkInterface_.message_queue_ = self.mavlinkMessageQueue_

        self.gcsInterface_ = GCSInterface(self.config_.udpIpRec_,
                                           self.config_.portRecMeta_,
                                           self.config_.portRecTouch_)
        self.raspiInterface_ = RaspiInterface(self.config_.udpIpRec_,
                                               self.config_.portRecJoystick_,
                                               self.config_.portRecTemperature_,
                                               self.config_.exponentialFactor_)
        self.raspiInterface_.message_queue = self.raspiMessageQueue_

        self.videoappInterface_ = VideoAppInterface(self.config_.udpIpRec_,
                                                    self.config_.txPortVideoApp_)

        self.metaInterface_ = MetaInterface(self.config_.udpIpMeta_,
                                            self.config_.udpIpRec_,
                                            self.config_.portSendMeta_,
                                            self.config_.portRecMeta_)

        self.usbJoystickInterface_ = USBJoystickInterface(self.state_, self.config_.exponentialFactor_)


    def InstallDependencies(self):
        """
        Installs the dependencies defined in requirements.txt using pip.
        """
        try:
            logging.info("Installing dependencies...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            logging.info("Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error("Failed to install dependencies: " + str(e))
            sys.exit(1)
            
    def ApplyNewConfig(self, newConfig):
        """
        Applies new configuration settings to the system.
        
        Args:
            newConfig (ConfigLoader): New configuration parameters.
        """
        self.config_ = newConfig
        self.state_.id_ = self.config_.id_
        self.state_.rc_channels_.rcChannelPitch_ = self.config_.channelPitch_
        self.state_.rc_channels_.rcChannelYaw_ = self.config_.channelYaw_
        self.state_.rc_channels_.rcChannelCam_ = self.config_.channelCam_
        self.state_.rc_channels_.rcChannelDeploy1_ = self.config_.channelDeploy1_
        self.state_.rc_channels_.rcChannelDeploy2_ = self.config_.channelDeploy2_
        self.state_.gimbal_.gimbalGain_ = self.config_.gain_
        self.state_.gimbal_.gimbalPitchNeutral_ = self.config_.pitchNeutral_
        self.state_.gimbal_.gimbalYawNeutral_ = self.config_.yawNeutral_
        self.state_.gimbal_.pwmPitchMin_ = self.config_.pwmPitchMin_
        self.state_.gimbal_.pwmPitchMax_ = self.config_.pwmPitchMax_
        self.state_.gimbal_.pwmYawMin_ = self.config_.pwmYawMin_
        self.state_.gimbal_.pwmYawMax_ = self.config_.pwmYawMax_
        if self.config_.joysticMode_ == "usb" and hasattr(self, "usbJoystickInterface_"):
            self.usbJoystickInterface_.exponential_factor = self.config_.exponentialFactor_
        elif self.config_.joysticMode_ == "udp":
            self.raspiInterface_.exponential_factor = self.config_.exponentialFactor_
        logging.info("New configuration applied.")

    def Start(self):
        """
        Starts all communication threads and then launches the GUI.
        """

        logging.debug("GUI initialized.")
        self.InstallDependencies()
        logging.debug("Dependencies installed.")

        threading.Thread(target=self.mavlinkInterface_.PymavlinkRead, daemon=True).start()
        logging.debug("Starting touch app receiver thread...")
        threading.Thread(target=self.gcsInterface_.TouchAppReceiver, args=(self.state_,), daemon=True).start()

        threading.Thread(target=self.gcsInterface_.GCSControlHandler, args=(self.state_, self.mavlinkInterface_), daemon=True).start()
        threading.Thread(target=self.raspiInterface_.ReceiveTemperature, args=(self.state_,), daemon=True).start()

        if self.config_.joysticMode_ == "udp":
            threading.Thread(target=self.raspiInterface_.ReceiveJoystick, args=(self.state_,), daemon=True).start()
        elif self.config_.joysticMode_ == "usb":
            threading.Thread(target=self.usbJoystickInterface_.Run, daemon=True).start()

        gui = MonitorGUI(self)

        gui.Run()



if __name__ == "__main__":
    from MissionPlanner import MissionPlanner
    mp = MissionPlanner()
    mp.Start()