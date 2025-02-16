import pygame
import logging
import time

class USBJoystickInterface:
    """
    Handles USB joystick input using pygame. If no joystick is connected, 
    the system logs a warning and sets joystick values to zero continuously.
    
    Attributes:
        state (DroneState): The shared state of the drone.
        exponential_factor (float): Factor for exponential adjustment.
        joystick: The pygame joystick object (or None if not available).
    """
    def __init__(self, state, exponential_factor):
        pygame.init()
        pygame.joystick.init()
        self.state = state
        self.exponential_factor = exponential_factor
        
        if pygame.joystick.get_count() == 0:
            logging.warning("No USB joystick found. The system will continue without joystick input.")
            self.joystick = None
        else:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            logging.info(f"USB Joystick connected: {self.joystick.get_name()}")

    def Run(self):
        """
        Processes joystick input. If no joystick is connected, sets joystick values to zero.
        """
        if self.joystick is None:
            # If no joystick is available, keep updating the state with zeros.
            while True:
                self.state.joystick_.joystickX_ = 0.0
                self.state.joystick_.joystickY_ = 0.0
                self.state.joystick_.joystickZ_ = 0.0
                self.state.joystick_.joystickButton_ = 0
                time.sleep(0.05)
        else:
            while True:
                pygame.event.pump()
                try:
                    rawX = self.joystick.get_axis(0)
                    rawY = self.joystick.get_axis(1)
                    rawZ = self.joystick.get_axis(2) if self.joystick.get_numaxes() > 2 else 0.0
                    # Here you might want to apply the exponential factor:
                    self.state.joystick_.joystickX_ = rawX ** self.exponential_factor
                    self.state.joystick_.joystickY_ = rawY ** self.exponential_factor
                    self.state.joystick_.joystickZ_ = rawZ ** self.exponential_factor
                    # Assume the first button is used for some action:
                    if self.joystick.get_numbuttons() > 0:
                        self.state.joystick_.joystickButton_ = self.joystick.get_button(0)
                    else:
                        self.state.joystick_.joystickButton_ = 0
                except Exception as e:
                    logging.error("Error reading USB joystick: %s", e)
                time.sleep(0.05)
