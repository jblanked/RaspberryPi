from machine import Pin, ADC

# HW504 -> Pico
# SW -> GP17 (Pin 22 - TX)
# VRx -> GP27 (Pin 32 - ADC1)
# VRy -> GP26 (Pin 31 - ADC0)
# GND -> GND
# 5V -> VSYS (Pin 39)

HW_LEFT_BUTTON = 0
HW_RIGHT_BUTTON = 1
HW_UP_BUTTON = 2
HW_DOWN_BUTTON = 3
HW_CENTER_BUTTON = 4

HW_ORIENTATION_NORMAL = 0
HW_ORIENTATION_90 = 1
HW_ORIENTATION_180 = 2
HW_ORIENTATION_270 = 3


class HW504:
    def __init__(
        self, x_pin=27, y_pin=26, button_pin=17, orientation=HW_ORIENTATION_NORMAL
    ):
        self.x_axis = ADC(Pin(x_pin))
        self.y_axis = ADC(Pin(y_pin))
        self.button = Pin(button_pin, Pin.IN, Pin.PULL_UP)
        self.orientation = orientation

    def _button(self) -> int:
        """Read the button value from the joystick."""
        return self.button.value()

    def get_axes(self) -> (int, int):
        """
        Read the raw ADC values from both axes and transform them based on the
        current orientation.

        Transformations:
          - HW_ORIENTATION_NORMAL: no change.
          - HW_ORIENTATION_90 (90° left):
                new_x = raw_y
                new_y = 65535 - raw_x
          - HW_ORIENTATION_180 (180°):
                new_x = 65535 - raw_x
                new_y = 65535 - raw_y
          - HW_ORIENTATION_270 (270° left or 90° right):
                new_x = 65535 - raw_y
                new_y = raw_x
        """
        x_raw = self.x_axis.read_u16()
        y_raw = self.y_axis.read_u16()

        if self.orientation == HW_ORIENTATION_NORMAL:
            return x_raw, y_raw
        elif self.orientation == HW_ORIENTATION_90:
            return y_raw, 65535 - x_raw
        elif self.orientation == HW_ORIENTATION_180:
            return 65535 - x_raw, 65535 - y_raw
        elif self.orientation == HW_ORIENTATION_270:
            return 65535 - y_raw, x_raw
        else:
            return x_raw, y_raw

    def _x_axis(self) -> int:
        """Return the transformed x-axis value."""
        x, _ = self.get_axes()
        return x

    def _y_axis(self) -> int:
        """Return the transformed y-axis value."""
        _, y = self.get_axes()
        return y

    def value(self, button: int = HW_CENTER_BUTTON) -> bool:
        """
        Return the state of a button based on the transformed x,y axis values.

        Thresholds:
          - x-axis:
              0 - 10000: left
              20000 - 33000: middle
              40000 - 65000: right

          - y-axis:
              0 - 10000: up
              20000 - 33000: middle
              40000 - 65000: down
        """
        x, y = self.get_axes()

        if button == HW_LEFT_BUTTON:
            return x < 10000
        if button == HW_RIGHT_BUTTON:
            return x > 40000
        if button == HW_UP_BUTTON:
            return y < 10000
        if button == HW_DOWN_BUTTON:
            return y > 40000
        if button == HW_CENTER_BUTTON:
            return self._button() == 0

        return False

    def read(self, stringify=False) -> dict:
        """Read the x-axis, y-axis, and button values from the joystick as a dictionary."""
        x, y = self.get_axes()
        return {
            "x": x,
            "y": y,
            "button": (
                self._button()
                if not stringify
                else "on" if self._button() == 0 else "off"
            ),
        }
