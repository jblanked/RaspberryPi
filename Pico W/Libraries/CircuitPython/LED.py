import time
import board
import digitalio


class LED:
    """Class to control an LED on a Raspberry Pi Pico device."""

    def __init__(self, pin=board.LED):
        self.led = digitalio.DigitalInOut(pin)
        self.led.direction = digitalio.Direction.OUTPUT

    def on(self):
        """Turn the LED on."""
        self.led.value = True

    def off(self):
        """Turn the LED off."""
        self.led.value = False

    def blink(self, duration=0.5):
        """Blink the LED on and off for a specified duration."""
        self.on()
        time.sleep(duration)
        self.off()
        time.sleep(duration)
