from EasyHTTP import (
    EasyHTTP,
)  # from https://github.com/jblanked/RaspberryPi/blob/main/Pico%20W/Libraries/Python/EasyHTTP.py
from EasyLCD import (
    EasyLCD,
)  # from https://github.com/jblanked/RaspberryPi/blob/main/Pico%20W/Libraries/Python/EasyLCD.py
from machine import Pin
from time import sleep, ticks_ms
import json
import gc


class WeatherLCD:
    def __init__(self, ssid, password) -> WeatherLCD:
        self.is_connected = False
        self.lcd = EasyLCD()
        self.http = EasyHTTP(ssid, password)
        self.weather = None
        self.last_time = None
        self.ip_address = None
        self.weather_interval = 0
        self.led = Pin(21, Pin.OUT)
        self.led.off()

    def start(self) -> bool:
        self.lcd.write(" Connecting to \n  WiFi now....  ", True)
        self.led.on()
        if self.http.connectToWiFi():
            self.led.off()
            self.lcd.write("WiFi connected!", True)
            self.is_connected = True
            return True
        self.led.off()
        self.lcd.write("ERROR.\nReboot device.", True)
        sleep(2)
        return False

    def run(self):
        if not self.is_connected:
            self.lcd.write("ERROR.\nReboot device.", True)
            sleep(1)
            return

        # if delay is over, get weather
        if ticks_ms() > self.weather_interval:
            self.weather = self.get_weather()
            self.last_time = self.get_time(False, True)
            self.weather_interval = ticks_ms() + (60000 * 1)  # 1 minute

            # write to LCD
            if len(self.weather) <= 7:
                self.lcd.write(f"Temp: {self.weather}", True, 0, 0)
                self.lcd.write(f"Time: {self.last_time}", False, 0, 1)
                temperature = self.weather.split()[0]
                data = {"temperature": temperature, "time": self.last_time}
                headers = {
                    "User-Agent": "micropython-urequests/1.1",
                    "Content-Type": "application/json",
                }
                try:
                    res = self.http.post(
                        url="http://10.0.0.25/weather", payload=data, headers=headers
                    )
                except Exception as e:
                    print(f"Failed to send request: {e}")
            else:
                self.lcd.write("Failed: ", True, 0, 0)
                self.lcd.write(str(self.weather), False, 0, 1)

    def get_weather(self) -> str:
        self.led.on()
        # get lat and long
        ip_info = self.http.get("https://ipwhois.app/json/")

        if ip_info is None or ip_info.text is None:
            self.led.off()
            return "IP info is empty"
        if ip_info.text == "Unable to connect to the server.":
            self.led.off()
            return "Server error."
        if ip_info.text.startswith("GET Request Failed"):
            self.led.off()
            return "Request Failed 1"

        ip_info = ip_info.json()
        lat = ip_info["latitude"]
        lon = ip_info["longitude"]
        self.ip_address = ip_info["ip"]

        if not lat:
            return "Lat is empty"
        if not lon:
            return "Lon is empty"

        # get weather
        total_weather = self.http.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,precipitation,rain,showers,snowfall&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&forecast_days=1"
        )

        if total_weather is None or total_weather.text is None:
            self.led.off()
            return "Weather info is empty"
        if total_weather.text == "Unable to connect to the server.":
            self.led.off()
            return "Server error."
        if total_weather.text.startswith("GET Request Failed"):
            self.led.off()
            return "Request Failed 2"

        weather_data = total_weather.json()

        returned_weather = weather_data["current"]["temperature_2m"]

        if returned_weather is None:
            self.led.off()
            return "Weather is empty"

        self.led.off()
        return f"{returned_weather} F"

    def get_time(self, date_only: bool = False, time_only: bool = False) -> str:
        time = self.http.get(
            f"https://timeapi.io/api/time/current/ip?ipAddress={self.ip_address}"
        )
        if time is None or time.text is None:
            return "Time is empty"
        if time.text == "Unable to connect to the server.":
            return "Server error."
        if time.text.startswith("GET Request Failed"):
            return "Request Failed 3"

        time_data = time.json()

        if date_only:
            return time_data["date"]
        if time_only:
            return time_data["time"]

        return time_data["dateTime"]


try:
    weather = WeatherLCD("your_ssid", "your_pass")
    weather.start()
    while True:
        gc.collect()  # refresh memory
        try:
            weather.run()
        except Exception as e:
            weather.lcd.write("Error occured", True, 0, 0)
            weather.lcd.write(str(e), False, 0, 1)
            print(f"Error occured: {e}")
            weather.led.off()
            weather.http.disconnectFromWiFi()
            break
except Exception as e:
    weather.lcd.write("Error occured", True, 0, 0)
    print(f"Error occured: {e}")
    weather.lcd.write(str(e), False, 0, 1)
    weather.led.off()
    weather.http.disconnectFromWiFi()
