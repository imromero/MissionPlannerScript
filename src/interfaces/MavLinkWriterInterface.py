import time
import logging
from pymavlink import mavutil
import threading

class MavlinkWriterInterface:

    def __init__(self, state, ip, port):
        self.lockSend = threading.Lock()
        connection_string_ = f"udp:{ip}:{port}"
        self.state_ = state
        self.logger = logging.getLogger("MavLink Writer Interface")
        self.logger.info("Initializing MAVLink connection...")
        self.master_ = mavutil.mavlink_connection(connection_string_)

    def set_gimbal_speed(self, joystick_azimuth, joystick_elevation):
        with self.lockSend:
            flags=0
            gimbal_device_id=0
            yaw_rate = max(-1.0, min(1.0, joystick_azimuth))
            pitch_rate = max(-1.0, min(1.0, joystick_elevation))

            # Set the pitch and yaw angles to NaN so that only the angular rates are used.
            pitch_angle = float('nan')
            yaw_angle = float('nan')

            # Send the MAVLink message using the gimbal_manager_set_manual_control_send method.
            self.master_.mav.gimbal_manager_set_manual_control_send(
                self.master_.target_system,  # Target system ID
                self.master_.target_component,  # Target component ID
                flags,  # High-level flags
                gimbal_device_id,  # Gimbal device ID
                pitch_angle,  # Pitch angle (NaN to ignore)
                yaw_angle,  # Yaw angle (NaN to ignore)
                pitch_rate,  # Pitch angular rate (unitless, -1 to 1)
                yaw_rate  # Yaw angular rate (unitless, -1 to 1)
            )

    def SendRCChannelPWM(self, deploy1, deploy2, camera, pitch, yaw):
        with self.lockSend:
            self.master_.mav.rc_channels_override_send(
                self.master_.target_system,
                self.master_.target_component,
                0, 0, 0, 0, 0,
                deploy1, deploy2, 0, pitch, 0, yaw, camera, 0, 0, 0, 0
            )
            self.logger.info( f"Sent MAVLink PWM: deploy1={deploy1}, deploy2={deploy2}, camera={camera}, pitch={pitch}, yaw={yaw}")
    
    def HandleVfrHud(self, msg):
        with self.lockSend:
            self.state_.telemetry_.groundspeed_ = msg.groundspeed
            self.state_.telemetry_.altitude_ = msg.alt
            self.state_.telemetry_.heading_ = msg.heading
            self.logger.info( f"Received MAVLink VFR_HUD: Altitude={msg.alt}, Heading={msg.heading}")

    
    def SetServoValue(self, channel, value):
        with self.lockSend:
            self.master_.mav.command_long_send(
                self.master_.target_system,
                self.master_.target_component,
                mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
                channel, value, 0, 0, 0, 0, 0
            )
            self.logger.info( f"Sent MAVLink SET SERVO: channel={channel}, value={value}")

