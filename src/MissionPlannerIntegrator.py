import threading
import logging
import subprocess
import sys
from ConfigLoader import ConfigLoader
from state.DroneState import DroneState
from interfaces.MavLinkReaderInterface import MavlinkReaderInterface
from interfaces.MavLinkWriterInterface import MavlinkWriterInterface
from interfaces.GCSInterface import GCSInterface
from interfaces.Raspinterface import RaspiInterface
from interfaces.UsbJoystickInterface import USBJoystickInterface
from interfaces.VideoAppInterface import VideoAppInterface
from interfaces.MetaInterface import MetaInterface


class MissionPlannerIntegrator:
    def __init__(self):

        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger("MissionPlanner")
        self.components = []  # List to store initialized components
        logging.info("Starting Mission Planner...")
        self.config_ = ConfigLoader("config.xml")

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

        self.mavlinkReaderInterface_ = MavlinkReaderInterface(self.state_,
                                                              self.config_.udpIpMavlink_,
                                                              self.config_.portSendMavlink_)

        self.mavLinkWriterInterface = MavlinkWriterInterface(self.state_,
                                                              self.config_.udpIpMavlink_,
                                                              self.config_.portSendMavlink_)

        self.gcsInterface_ = GCSInterface(self.config_.udpIpRec_,
                                           self.config_.portRecMeta_,
                                           self.config_.portRecTouch_)
        self.raspiInterface_ = RaspiInterface(self.config_.udpIpRec_,
                                               self.config_.portRecJoystick_,
                                               self.config_.portRecTemperature_,
                                               self.config_.exponentialFactor_)

        self.videoappInterface_ = VideoAppInterface(self.config_.udpIpRec_,
                                                    self.config_.txPortVideoApp_)

        self.metaInterface_ = MetaInterface(self.config_.udpIpMeta_,
                                            self.config_.udpIpRec_,
                                            self.config_.portSendMeta_,
                                            self.config_.portRecMeta_)

        self.usbJoystickInterface_ = USBJoystickInterface(self.state_, self.config_.exponentialFactor_,self.config_.deadZone,self.mavLinkWriterInterface)


    def InstallDependencies(self):
        try:
            logging.info("Installing dependencies...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            logging.info("Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error("Failed to install dependencies: " + str(e))
            sys.exit(1)
            


    def Start(self):

        self.logger.info("Starting Mission Planner Integration process")
        self.logger.info("Installing dependencies")
        self.InstallDependencies()
        self.logger.debug("Dependencies installed.")

        threads = []

        self.logger.debug("Starting Mavlink Reader Interface thread...")
        t_mav = threading.Thread(
            target=self.mavlinkReaderInterface_.MavlinkReader,
            name="Mavlink Reader Interface Thread",
            daemon=False  # Set to False so that the thread runs as a non-daemon thread
        )
        t_mav.start()
        threads.append(t_mav)

        self.logger.debug("Starting Touch App Receiver thread...")
        t_touch = threading.Thread(
            target=self.gcsInterface_.TouchAppReceiver,
            args=(self.state_,),
            name="Touch App Receiver Thread",
            daemon=False
        )
        t_touch.start()
        threads.append(t_touch)

        self.logger.debug("Starting GSC Control Interface thread...")
        t_gcs = threading.Thread(
            target=self.gcsInterface_.GCSControlHandler,
            args=(self.state_, self.mavlinkReaderInterface_),
            name="GCS Control Handler Thread",
            daemon=False
        )
        t_gcs.start()
        threads.append(t_gcs)

        self.logger.debug("Starting Temperature Reader Interface thread...")
        t_temp = threading.Thread(
            target=self.raspiInterface_.ReceiveTemperature,
            args=(self.state_,),
            name="Temperature Reader Interface Thread",
            daemon=False
        )
        t_temp.start()
        threads.append(t_temp)


        t_usbjoy = threading.Thread(
            target=self.usbJoystickInterface_.Run,
            name="USBJoystickThread",
            daemon=False
        )
        t_usbjoy.start()
        threads.append(t_usbjoy)

        self.logger.info("All threads have been launched.")
        # Wait for all threads to finish
        for thread in threads:
            self.logger.info(f"Waiting for thread {thread.name} to finish...")
            thread.join()

        self.logger.info("All threads have terminated. Mission Planner Integration process completed.")


if __name__ == "__main__":

    mp = MissionPlannerIntegrator()
    mp.Start()