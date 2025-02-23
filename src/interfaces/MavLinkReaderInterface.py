import logging
from pymavlink import mavutil

class MavlinkReaderInterface:

    def __init__(self, state, ip,port):
        self.state_ = state
        connection_string = f"udp:{ip}:{port}"
        self.logger = logging.getLogger("MavLink Reader Interface")
        self.logger.info("Initializing MAVLink connection...")
        self.master_ = mavutil.mavlink_connection(connection_string)

    def ReadRCChannelsRaw(self, msg):
        self.state_.rc_channels_.deploy12Value_ = int(msg.chan6_raw)
        self.state_.rc_channels_.deploy34Value_ = int(msg.chan7_raw)
        self.state_.rc_channels_.safetyValue_ = int(msg.chan8_raw)
        self.state_.rc_channels_.cameraValue_ = int(msg.chan12_raw)
        self.logger.info(f"Received MAVLink RC_CHANNELS: {msg.get_type()}")

    def HandleVfrHud(self, msg):
        self.state_.telemetry_.groundspeed_ = msg.groundspeed
        self.state_.telemetry_.altitude_ = msg.alt
        self.state_.telemetry_.heading_ = msg.heading
        self.logger.info( f"Received MAVLink VFR_HUD: Altitude={msg.alt}, Heading={msg.heading}")
    
    def HandleAttitude(self, msg):
        self.state_.telemetry_.pitch_ = msg.pitch
        self.state_.telemetry_.roll_ = msg.roll
        self.logger.info(f"Received MAVLink ATTITUDE: Pitch={msg.pitch}, Roll={msg.roll}")
    
    def HandleGlobalPosition(self, msg):
        self.state_.telemetry_.latitude_ = msg.lat / 1e7
        self.state_.telemetry_.longitude_ = msg.lon / 1e7
        self.state_.telemetry_.altitude_ = msg.alt
        self.logger.info( f"Received MAVLink GLOBAL_POSITION_INT: Lat={self.state_.telemetry_.latitude_}, Lon={self.state_.telemetry_.longitude_}")
    
    def HandleSysStatus(self, msg):
        self.state_.battery_.voltageValue_ = msg.voltage_battery / 1000.0
        self.state_.battery_.currentValue_ = msg.current_battery / 100.0
        self.logger.info( f"Received MAVLink SYS_STATUS: Voltage={self.state_.battery_.voltageValue_}V")
    
    def MavlinkReader(self):
        self.logger.info("Initiating MAVLink Read loop...")
        while True:
            msg = self.master_.recv_match(blocking=False)
            if msg is not None:
                try:
                    msgType = msg.get_type()
                    if msgType == 'RC_CHANNELS':
                        self.logger.debug("Received RC_CHANNELS message.")
                        self.ReadRCChannelsRaw(msg)
                    if msgType == 'VFR_HUD':
                        self.logger.debug("Received VFR_HUD message.")
                        self.HandleVfrHud(msg)
                    if msgType == 'ATTITUDE':
                        self.logger.debug("Received ATTITUDE message.")
                        self.HandleAttitude(msg)
                    if msgType == 'GLOBAL_POSITION_INT':
                        self.logger.debug("Received GLOBAL_POSITION_INT message.")
                        self.HandleGlobalPosition(msg)
                except Exception as e:
                    self.logger.error(f"Error in PymavlinkRead: {e}")