"""
Module: MavlinkInterface.py
Description: Manages MAVLink communications.
"""

import time
import logging
from pymavlink import mavutil

class MavlinkInterface:
    """
    Handles the MAVLink connection and processes messages.
    
    Attributes:
        state_ : DroneState instance.
        master_ : pymavlink connection.
        message_queue_ : Queue for logging messages.
    """
    def __init__(self, state, connectionString):
        self.state_ = state
        logging.info("Initializing MAVLink connection...")
        self.master_ = mavutil.mavlink_connection(connectionString)
        
        self.message_queue_ = None
        
    
    def ConfigureMount(self):
        mode = mavutil.mavlink.MAV_MOUNT_MODE_RETRACT
        self.master_.mav.mount_configure_send(self.master_.target_system,
                                              self.master_.target_component,
                                              mode, 1, 1, 1)
    
    def ConfigureMountNeutral(self):
        mode = mavutil.mavlink.MAV_MOUNT_MODE_NEUTRAL
        self.master_.mav.mount_configure_send(self.master_.target_system,
                                              self.master_.target_component,
                                              mode, 1, 1, 1)
    
    def ConfigureMountRCTargeting(self):
        mode = mavutil.mavlink.MAV_MOUNT_MODE_RC_TARGETING
        self.master_.mav.mount_configure_send(self.master_.target_system,
                                              self.master_.target_component,
                                              mode, 1, 1, 1)
    
    def ReadRCChannelsRaw(self, msg):
        self.state_.rc_channels_.deploy12Value_ = int(msg.chan6_raw)
        self.state_.rc_channels_.deploy34Value_ = int(msg.chan7_raw)
        self.state_.rc_channels_.safetyValue_ = int(msg.chan8_raw)
        self.state_.rc_channels_.cameraValue_ = int(msg.chan12_raw)
        if self.message_queue_:
            self.message_queue_.put(("received", f"MAVLink RC_CHANNELS: {msg.get_type()}"))
    
    def SendRCChannelPWM(self, deploy1, deploy2, camera, pitch, yaw):
        self.master_.mav.rc_channels_override_send(
            self.master_.target_system,
            self.master_.target_component,
            0, 0, 0, 0, 0,
            deploy1, deploy2, 0, pitch, 0, yaw, camera, 0, 0, 0, 0
        )
        if self.message_queue_:
            self.message_queue_.put(("sent", f"MAVLink SEND RC PWM: deploy1={deploy1}, deploy2={deploy2}, camera={camera}, pitch={pitch}, yaw={yaw}"))
    
    def HandleVfrHud(self, msg):
        self.state_.telemetry_.groundspeed_ = msg.groundspeed
        self.state_.telemetry_.altitude_ = msg.alt
        self.state_.telemetry_.heading_ = msg.heading
        if self.message_queue_:
            self.message_queue_.put(("received", f"MAVLink VFR_HUD: Altitude={msg.alt}, Heading={msg.heading}"))
    
    def HandleAttitude(self, msg):
        self.state_.telemetry_.pitch_ = msg.pitch
        self.state_.telemetry_.roll_ = msg.roll
        if self.message_queue_:
            self.message_queue_.put(("received", f"MAVLink ATTITUDE: Pitch={msg.pitch}, Roll={msg.roll}"))
    
    def HandleGlobalPosition(self, msg):
        self.state_.telemetry_.latitude_ = msg.lat / 1e7
        self.state_.telemetry_.longitude_ = msg.lon / 1e7
        self.state_.telemetry_.altitude_ = msg.alt
        if self.message_queue_:
            self.message_queue_.put(("received", f"MAVLink GLOBAL_POSITION_INT: Lat={self.state_.telemetry_.latitude_}, Lon={self.state_.telemetry_.longitude_}"))
    
    def HandleSysStatus(self, msg):
        self.state_.battery_.voltageValue_ = msg.voltage_battery / 1000.0
        self.state_.battery_.currentValue_ = msg.current_battery / 100.0
        if self.message_queue_:
            self.message_queue_.put(("received", f"MAVLink SYS_STATUS: Voltage={self.state_.battery_.voltageValue_}V"))
    
    def SetServoValue(self, channel, value):
        self.master_.mav.command_long_send(
            self.master_.target_system,
            self.master_.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
            channel, value, 0, 0, 0, 0, 0
        )
        if self.message_queue_:
            self.message_queue_.put(("sent", f"MAVLink SET SERVO: channel={channel}, value={value}"))
    
    def PymavlinkRead(self):
        logging.info("Initiating MAVLinkRead loop...")
        logging.info("Waiting for heartbeat...")
        aa=self.master_.recv_msg()
        self.master_.wait_heartbeat()
        logging.info("Heartbeat received. Starting MAVLink read loop.")
        self.ConfigureMount()
        logging.info("Mount configured.")
        time.sleep(5)
        self.ConfigureMountNeutral()
        logging.info("Mount neutral")
        time.sleep(10)
        self.ConfigureMountRCTargeting()
        logging.info("Mount RCTargeting")
        
        while True:
            msg = self.master_.recv_match(blocking=False)
            if msg is not None:
                try:
                    msgType = msg.get_type()
                    if msgType == 'RC_CHANNELS':
                        logging.debug("Received RC_CHANNELS message.")
                        self.ReadRCChannelsRaw(msg)
                    if msgType == 'VFR_HUD':
                        logging.debug("Received VFR_HUD message.")
                        self.HandleVfrHud(msg)
                    if msgType == 'ATTITUDE':
                        logging.debug("Received ATTITUDE message.")
                        self.HandleAttitude(msg)
                    if msgType == 'GLOBAL_POSITION_INT':
                        logging.debug("Received GLOBAL_POSITION_INT message.")
                        self.HandleGlobalPosition(msg)
                except Exception as e:
                    logging.error(f"Error in PymavlinkRead: {e}")