"""
Module: RaspiInterface.py
Description: Handles UDP communication with a Raspberry Pi and applies exponential adjustment to joystick input.
"""

import struct
import logging
from interfaces.UDPChannel import UDPChannel
from utils.ExponentialAdjust import ExponentialAdjust

class RaspiInterface:
    """
    Manages communication with the Raspberry Pi via UDP.
    
    Attributes:
        message_queue: Queue for logging messages.
        exponential_factor_ (float): Factor for exponential adjustment.
    """
    def __init__(self, udpIpRec, portRecJoystick, portRecTemperature, exponentialFactor):
        self.joystickChannel_ = UDPChannel(udpIpRec, portRecJoystick, isReceiver=True)
        self.tempChannel_ = UDPChannel(udpIpRec, portRecTemperature, isReceiver=True)
        self.message_queue = None
        self.joystickMessageCount_ = 0
        self.temperatureMessageCount_ = 0
        self.exponential_factor_ = exponentialFactor

    def ReceiveJoystick(self, state):
        while True:
            try:
                data, address = self.joystickChannel_.Receive(1024)
                rawX, rawY, rawZ, rawButton = struct.unpack('ffff', data)
                state.joystick_.joystickX_ = ExponentialAdjust(rawX, self.exponential_factor_)
                state.joystick_.joystickY_ = ExponentialAdjust(rawY, self.exponential_factor_)
                state.joystick_.joystickZ_ = ExponentialAdjust(rawZ, self.exponential_factor_)
                state.joystick_.joystickButton_ = rawButton
                self.joystickMessageCount_ += 1
                if self.message_queue:
                    self.message_queue.put(("received", f"Raspi JOYSTICK: {data}"))
            except Exception as e:
                logging.error(f"Raspi joystick error: {e}")

    def ReceiveTemperature(self, state):
        while True:
            try:
                data, address = self.tempChannel_.Receive(1024)
                state.joystick_.temperature_ = struct.unpack('=f', data)[0]
                self.temperatureMessageCount_ += 1
                if self.message_queue:
                    self.message_queue.put(("received", f"Raspi TEMP: {data}"))
            except Exception as e:
                logging.error(f"Raspi temperature error: {e}")