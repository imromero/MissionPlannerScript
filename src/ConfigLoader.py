import xml.etree.ElementTree as ET
import logging
import sys

def get_text(element):
    """Safely return element.text.strip() or an empty string."""
    return element.text.strip() if element is not None and element.text is not None else ""

class ConfigLoader:
    def __init__(self, filePath="config.xml"):
        self.filePath = filePath
        try:
            logging.info("Loading configuration from XML...")
            tree = ET.parse(filePath)
            root = tree.getroot()
            
            # Network configuration
            network = root.find("Network")
            self.udpIpRec_ = get_text(network.find("UDP_IP_REC"))
            self.udpIpMeta_ = get_text(network.find("UDP_IP_META"))
            self.udpIpMavlink_ = get_text(network.find("UDP_IP_MAVLINK"))

            
            # Ports configuration
            ports = root.find("Ports")
            self.portSendMeta_ = int(get_text(ports.find("PortSendMeta")))
            self.portRecMeta_ = int(get_text(ports.find("PortRecMeta")))
            self.portRecTouch_ = int(get_text(ports.find("PortRecTouch")))
            self.portRecJoystick_ = int(get_text(ports.find("PortRecJoystick")))
            self.portRecTemperature_ = int(get_text(ports.find("PortRecTemperature")))
            self.txPortVideoApp_ = int(get_text(ports.find("TxPortVideoApp")))
            self.portRecMavlink_ = int(get_text(ports.find("PortRecMavlink")))
            self.portSendMavlink_ = int(get_text(ports.find("PortSendMavlink")))
            
            # Joystick configuration
            joystick = root.find("Joystick")
            self.joysticMode_ = get_text(joystick.find("Mode")).lower()
            
            # Gimbal configuration
            gimbal = root.find("Gimbal")
            self.gain_ = float(get_text(gimbal.find("Gain")))
            self.pitchNeutral_ = int(get_text(gimbal.find("PitchNeutral")))
            self.yawNeutral_ = int(get_text(gimbal.find("YawNeutral")))
            self.pwmPitchMin_ = int(get_text(gimbal.find("PWMPitchMin")))
            self.pwmPitchMax_ = int(get_text(gimbal.find("PWMPitchMax")))
            self.pwmYawMin_ = int(get_text(gimbal.find("PWMYawMin")))
            self.pwmYawMax_ = int(get_text(gimbal.find("PWMYawMax")))
            
            # RCChannels configuration
            rc = root.find("RCChannels")
            self.channelPitch_ = int(get_text(rc.find("ChannelPitch")))
            self.channelYaw_ = int(get_text(rc.find("ChannelYaw")))
            self.channelCam_ = int(get_text(rc.find("ChannelCam")))
            self.channelDeploy1_ = int(get_text(rc.find("ChannelDeploy1")))
            self.channelDeploy2_ = int(get_text(rc.find("ChannelDeploy2")))
            
            # Drone configuration
            drone = root.find("Drone")
            self.id_ = int(get_text(drone.find("ID")))
            
            # Token
            self.token_ = get_text(root.find("Token"))
            
            # JoystickAdjustment
            ja = root.find("JoystickAdjustment")
            self.exponentialFactor_ = float(get_text(ja.find("ExponentialFactor")))
            self.deadZone = float(get_text(ja.find("DeadZone")))

        except Exception as e:
            print("Error loading XML configuration:", e)
            sys.exit(1)
        
        logging.info("Configuration loaded successfully.")

