import struct
import logging
from interfaces.UDPChannel import UDPChannel

class MetaInterface:
    """
    Manages communication with a Meta device via UDP.
    """
    def __init__(self, udpIpMeta, udpIpRec, portSendMeta, portRecMeta):
        self.logger = logging.getLogger("Meta Interface")
        self.senderChannel_ = UDPChannel(udpIpRec, portSendMeta, isReceiver=False)
        self.receiverChannel_ = UDPChannel(udpIpRec, portRecMeta, isReceiver=True)
        self.udpIpMeta_ = udpIpMeta
        self.portSendMeta_ = portSendMeta

    def ReceiveFromMeta(self):
        self.logger.info("Meta interface started.")
        while True:
            try:
                data, address = self.receiverChannel_.Receive(1024)
            except Exception as e:
                self.logger.error(f"Meta receive error: {e}")
    
    def GCSToMeta(self, state):
        while True:
            coordStruct = struct.pack('ifffffffffiiii',
                                       state.id_,
                                       state.telemetry_.roll_,
                                       state.telemetry_.pitch_,
                                       state.telemetry_.heading_,
                                       state.telemetry_.latitude_,
                                       state.telemetry_.longitude_,
                                       state.telemetry_.altitude_,
                                       state.telemetry_.groundspeed_,
                                       state.telemetry_.verticalSpeed_,
                                       state.battery_.voltageValue_,
                                       state.rc_channels_.deploy12Value_,
                                       state.rc_channels_.deploy34Value_,
                                       state.rc_channels_.safetyValue_,
                                       state.rc_channels_.cameraValue_)
            self.senderChannel_.Send(coordStruct, self.udpIpMeta_, self.portSendMeta_)