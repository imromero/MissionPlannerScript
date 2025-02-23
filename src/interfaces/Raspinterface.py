import struct
import logging
from interfaces.UDPChannel import UDPChannel

class RaspiInterface:

    def __init__(self, udpIpRec, portRecJoystick, portRecTemperature, exponentialFactor):
        self.logger = logging.getLogger("Rasberry Interface")
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
                state.joystick_.joystickX_ = rawX
                state.joystick_.joystickY_ = rawY
                state.joystick_.joystickZ_ = rawZ
                state.joystick_.joystickButton_ = rawButton
                self.joystickMessageCount_ += 1
                self.logger.info( f"Reveived JOYSTICK: {data}")
            except Exception as e:
                self.logger.error(f"Raspberry interface joystick error: {e}")

    def ReceiveTemperature(self, state):
        while True:
            try:
                data, address = self.tempChannel_.Receive(1024)
                state.joystick_.temperature_ = struct.unpack('=f', data)[0]
                self.temperatureMessageCount_ += 1
                self.logger.info( f"Received TEMP: {data}")
            except Exception as e:
                self.logger.error(f"Raspi temperature error: {e}")