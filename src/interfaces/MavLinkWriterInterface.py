import time
import logging
from pymavlink import mavutil

class MavlinkWriterInterface:

    def __init__(self, state, ip, port):
        connection_string_ = f"udp:{ip}:{port}"
        self.state_ = state
        self.logger = logging.getLogger("MavLink Writer Interface")
        self.logger.info("Initializing MAVLink connection...")
        self.master_ = mavutil.mavlink_connection(connection_string_)

    
    def SendRCChannelPWM(self, deploy1, deploy2, camera, pitch, yaw):
        self.master_.mav.rc_channels_override_send(
            self.master_.target_system,
            self.master_.target_component,
            0, 0, 0, 0, 0,
            deploy1, deploy2, 0, pitch, 0, yaw, camera, 0, 0, 0, 0
        )
        self.logger.info( f"Sent MAVLink PWM: deploy1={deploy1}, deploy2={deploy2}, camera={camera}, pitch={pitch}, yaw={yaw}")
    
    def HandleVfrHud(self, msg):
        self.state_.telemetry_.groundspeed_ = msg.groundspeed
        self.state_.telemetry_.altitude_ = msg.alt
        self.state_.telemetry_.heading_ = msg.heading
        self.logger.info( f"Received MAVLink VFR_HUD: Altitude={msg.alt}, Heading={msg.heading}")

    
    def SetServoValue(self, channel, value):
        self.master_.mav.command_long_send(
            self.master_.target_system,
            self.master_.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
            channel, value, 0, 0, 0, 0, 0
        )
        self.logger.info( f"Sent MAVLink SET SERVO: channel={channel}, value={value}")
    
