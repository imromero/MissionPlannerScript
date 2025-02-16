"""
Module: ConfigLoader.py
Description: Loads configuration parameters from an XML file and can write them back.
The attribute names correspond directly to the XML tag names but are stored as camelCase
with a trailing underscore.
"""

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
            self.mavlinkConnection_ = get_text(network.find("MAVLinkConnection"))
            
            # Ports configuration
            ports = root.find("Ports")
            self.portSendMeta_ = int(get_text(ports.find("PortSendMeta")))
            self.portRecMeta_ = int(get_text(ports.find("PortRecMeta")))
            self.portRecTouch_ = int(get_text(ports.find("PortRecTouch")))
            self.portRecJoystick_ = int(get_text(ports.find("PortRecJoystick")))
            self.portRecTemperature_ = int(get_text(ports.find("PortRecTemperature")))
            self.txPortVideoApp_ = int(get_text(ports.find("TxPortVideoApp")))
            
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
            
        except Exception as e:
            print("Error loading XML configuration:", e)
            sys.exit(1)
        
        logging.info("Configuration loaded successfully.")

    def write_config(self):
        """
        Writes the current configuration attributes to the XML file using the same structure,
        and formats (pretty-prints) the XML before saving.
        """
        import xml.dom.minidom  # Aseguramos la importación del módulo

        root = ET.Element("Configuration")
        
        # Network configuration
        network = ET.SubElement(root, "Network")
        ET.SubElement(network, "UDP_IP_REC").text = self.udpIpRec_
        ET.SubElement(network, "UDP_IP_META").text = self.udpIpMeta_
        ET.SubElement(network, "MAVLinkConnection").text = self.mavlinkConnection_
        
        # Ports configuration
        ports = ET.SubElement(root, "Ports")
        ET.SubElement(ports, "PortSendMeta").text = str(self.portSendMeta_)
        ET.SubElement(ports, "PortRecMeta").text = str(self.portRecMeta_)
        ET.SubElement(ports, "PortRecTouch").text = str(self.portRecTouch_)
        ET.SubElement(ports, "PortRecJoystick").text = str(self.portRecJoystick_)
        ET.SubElement(ports, "PortRecTemperature").text = str(self.portRecTemperature_)
        ET.SubElement(ports, "TxPortVideoApp").text = str(self.txPortVideoApp_)
        
        # Joystick configuration
        joystick = ET.SubElement(root, "Joystick")
        ET.SubElement(joystick, "Mode").text = self.joysticMode_
        
        # Gimbal configuration
        gimbal = ET.SubElement(root, "Gimbal")
        ET.SubElement(gimbal, "Gain").text = str(self.gain_)
        ET.SubElement(gimbal, "PitchNeutral").text = str(self.pitchNeutral_)
        ET.SubElement(gimbal, "YawNeutral").text = str(self.yawNeutral_)
        ET.SubElement(gimbal, "PWMPitchMin").text = str(self.pwmPitchMin_)
        ET.SubElement(gimbal, "PWMPitchMax").text = str(self.pwmPitchMax_)
        ET.SubElement(gimbal, "PWMYawMin").text = str(self.pwmYawMin_)
        ET.SubElement(gimbal, "PWMYawMax").text = str(self.pwmYawMax_)
        
        # RCChannels configuration
        rc = ET.SubElement(root, "RCChannels")
        ET.SubElement(rc, "ChannelPitch").text = str(self.channelPitch_)
        ET.SubElement(rc, "ChannelYaw").text = str(self.channelYaw_)
        ET.SubElement(rc, "ChannelCam").text = str(self.channelCam_)
        ET.SubElement(rc, "ChannelDeploy1").text = str(self.channelDeploy1_)
        ET.SubElement(rc, "ChannelDeploy2").text = str(self.channelDeploy2_)
        
        # Drone configuration
        drone = ET.SubElement(root, "Drone")
        ET.SubElement(drone, "ID").text = str(self.id_)
        
        # Token
        ET.SubElement(root, "Token").text = self.token_
        
        # JoystickAdjustment
        ja = ET.SubElement(root, "JoystickAdjustment")
        ET.SubElement(ja, "ExponentialFactor").text = str(self.exponentialFactor_)
        
        # Convert to a pretty XML string.
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = xml.dom.minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        with open(self.filePath, "w", encoding="utf-8") as f:
            f.write(pretty_xml)
