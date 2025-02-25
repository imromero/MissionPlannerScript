import pygame
import logging
import time




class USBJoystickInterface:
    def __init__(self, state, exponential_factor,dead_zone,mavlinWriter):
        self.logger = logging.getLogger("USB Joystick Interface")
        self.mavlinkWriter = mavlinWriter
        self.state = state
        self.exponential_factor = exponential_factor
        self.deadzone = dead_zone

    def Run(self):
        delta_time = 0.05
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            self.logger.error("No joysticks connected.")
            return

        joystick = pygame.joystick.Joystick(0)
        joystick.init()

        num_axes = joystick.get_numaxes()
        num_buttons = joystick.get_numbuttons()


        while True:
            try:
                pygame.event.pump()  # Procesa eventos
                axes =  [self.apply_exponential_curve(joystick.get_axis(i)) for i in range(num_axes)]
                buttons = [joystick.get_button(i) for i in range(num_buttons)]
                #self.logger.debug(f"Ejes: {[round(a, 4) for a in axes]}, Botones: {buttons}")
                self.mavlinkWriter.set_gimbal_speed(axes[0], axes[1],delta_time)
            except Exception as e:
                self.logger.error("Error reading USB joystick: %s", e)
            time.sleep(delta_time)


    def apply_exponential_curve(self, value):
        if abs(value) < self.deadzone:
            return 0.0  # Elimina ruido en la zona muerta
        sign = 1 if value > 0 else -1
        return sign * (abs(value) ** self.exponential_factor)  # Aplica la curva exponencial manteniendo el signo