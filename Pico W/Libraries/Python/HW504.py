from machine import Pin, ADC

# HW504 -> Pico
# SW -> GP17 (Pin 22 - TX)
# VRx -> GP27 (Pin 32 - ADC1)
# VRy -> GP26 (Pin 31 - ADC0)
# GND -> GND
# 5V -> 3v3 (Pin 36)

# X-axis
# 0 - 10000: left
# 20000 - 33000: middle
# 40000 - 65000: right

# Y-axis
# 0 - 10000: up
# 20000 - 33000: middle
# 40000 - 65000: down


class HW504:
    def __init__(self, x_pin=27, y_pin=26, button_pin=17):
        self.x_axis = ADC(Pin(x_pin))
        self.y_axis = ADC(Pin(y_pin))
        self.button = Pin(button_pin, Pin.IN, Pin.PULL_UP)

    def _x_axis(self):
        """Read the x-axis value from the joystick."""
        return self.x_axis.read_u16()

    def _y_axis(self):
        """Read the y-axis value from the joystick."""
        return self.y_axis.read_u16()

    def _button(self):
        """Read the button value from the joystick."""
        return self.button.value()

    def read(self, stringify=False):
        """Read the x-axis, y-axis and button values from the joystick as a dictionary."""
        return {
            "x": self._x_axis(),
            "y": self._y_axis(),
            "button": (
                self._button()
                if not stringify
                else "on" if self._button() == 0 else "off"
            ),
        }
