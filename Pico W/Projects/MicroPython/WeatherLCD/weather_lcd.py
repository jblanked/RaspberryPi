from EasyHTTP import (
    EasyHTTP,
)  # from https://github.com/jblanked/RaspberryPi/blob/main/Pico%20W/Libraries/Python/EasyHTTP.py
from EasyLCD import (
    EasyLCD,
)  # from https://github.com/jblanked/RaspberryPi/blob/main/Pico%20W/Libraries/Python/EasyLCD.py
from machine import Pin, RTC
from time import sleep, ticks_ms
import gc
import machine
import errno


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
        self.rtc = RTC()
        self.lat = None
        self.lon = None

    def start(self) -> bool:
        self.lcd.write(" Connecting to \n  WiFi now....  ", True)
        self.led.on()
        if self.http.connectToWiFi():
            self.led.off()
            self.lcd.write("WiFi connected!", True)
            self.is_connected = True
            self.led.on()
            sleep(2)
            if not self.get_ip():
                self.led.off()
                self.lcd.write("Failed to get\n  IP address.", True)
                sleep(1)
                return False
            if not self.set_time():
                self.led.off()
                self.lcd.write("Failed to set\n  time.", True)
                sleep(1)
                return False
            self.led.off()
            self.weather = self.get_weather()
            if not self.weather:
                return False
            self.weather_interval = ticks_ms() + (60000 * 1)  # 1 minute
            return True
        self.led.off()
        self.lcd.write("ERROR.\nReboot device.", True)
        sleep(2)
        return False

    def handle_os_error(self, e: OSError) -> str:
        try:
            if not e.args:
                return "Unknown error"
            if e.args[0] == errno.ECONNABORTED:
                return "Connection aborted"
            if e.args[0] == errno.ECONNREFUSED:
                return "Connection refused"
            if e.args[0] == errno.ECONNRESET:
                return "Connection reset"
            if e.args[0] == errno.EINVAL:
                return "Invalid argument"
            if e.args[0] == errno.ENOTCONN:
                return "Not connected"
            if e.args[0] == errno.ETIMEDOUT:
                return "Connection timed out"
            if e.args[0] == errno.EACCES:
                return "Permission denied"
            if e.args[0] == errno.ENOMEM:
                return "Out of memory"
            if e.args[0] == errno.ENOENT or e.args[0] == 2:
                return "No such file or directory"
            if e.args[0] == -2:
                return "Network error"
            return "Unknown error"
        except Exception as e:
            print(f"Error in handle_os_error: {e}")
            return "Unknown error"

    def run(self) -> bool:
        try:
            if not self.is_connected:
                self.lcd.write("ERROR.\nReboot device.", True)
                sleep(1)
                return False

            # If delay is over, get weather
            if ticks_ms() > self.weather_interval:

                # Make the GET request for weather data
                new_weather = self.get_weather()
                if not new_weather or not new_weather.endswith("F"):
                    return False

                self.weather = new_weather
                self.update_time()
                self.weather_interval = ticks_ms() + (60000 * 1)  # 1 minute

                # Write to LCD
                if len(self.weather) <= 7:
                    temperature = self.weather.split()[0]
                    self.get_time() # update self.last_time
                    data = {"temperature": temperature, "time": self.last_time}
                    headers = {
                        "User-Agent": "micropython-urequests/1.1",
                        "Content-Type": "application/json",
                    }
                    try:
                        res = self.http.post(
                            url="http://10.0.0.22/weather",
                            payload=data,
                            headers=headers,
                            timeout=3,
                        )
                    except Exception as e:
                        print(f"Failed to send request: {e}")

                    return True

                self.lcd.write("Failed: ", True, 0, 0)
                self.lcd.write(str(self.weather), False, 0, 1)
                return False
            self.update_time()
            sleep(1)
            return True
        except OSError as e:
            print(self.handle_os_error(e))
            return False
        except Exception as e:
            print(f"Error in run: {e}")
            return False

    def get_ip(self) -> bool:
        try:
            if self.ip_address:
                return True
            ip_info = self.http.get("https://ipwhois.app/json/")
            if ip_info is None or ip_info.text is None:
                print("IP is empty")
                return False
            if ip_info.text == "Unable to connect to the server.":
                print("Server error.")
                return False
            if ip_info.text.startswith("GET Request Failed"):
                print("Request Failed 1")
                return False

            ip_info = ip_info.json()
            lat = ip_info.get("latitude")
            lon = ip_info.get("longitude")
            ip_address = ip_info.get("ip")

            if not lat:
                print("Lat is empty")
                return False
            if not lon:
                print("Lon is empty")
                return False
            if not ip_address:
                print("IP is empty")
                return False

            self.lat = lat
            self.lon = lon
            self.ip_address = ip_address
            return True
        except OSError as e:
            print(self.handle_os_error(e))
            return False
        except Exception as e:
            print(f"Error getting ip: {e}")
            return False

    def get_weather(self) -> str:
        self.led.on()
        try:
            # Check WiFi connection
            if not self.is_connected:
                if not self.http.connectToWiFi():
                    self.led.off()
                    return "Failed to connect to WiFi"

            # Validate coordinates
            if not self.lon or self.lat is None:
                self.led.off()
                return "Lat or Lon is None"

            # Simplified URL without unnecessary parameters
            url = f"https://api.open-meteo.com/v1/forecast?latitude={self.lat}&longitude={self.lon}&current_weather=true&temperature_unit=fahrenheit"

            # Make request without custom headers
            total_weather = self.http.get(url)

            # Check if response exists
            if total_weather is None:
                self.led.off()
                return "No response from weather server"

            # Check status code
            if hasattr(total_weather, "status_code"):
                if total_weather.status_code != 200:
                    self.led.off()
                    return f"Weather API error: {total_weather.status_code}"

            # Check response text
            if not hasattr(total_weather, "text") or total_weather.text is None:
                self.led.off()
                return "Empty response from weather server"

            if total_weather.text == "Unable to connect to the server.":
                self.led.off()
                return "Server connection error"

            if total_weather.text.startswith("GET Request Failed"):
                self.led.off()
                return f"Request Failed: {total_weather.text}"

            # Parse JSON with error handling
            try:
                weather_data = total_weather.json()
            except Exception as e:
                self.led.off()
                return f"JSON parsing error: {str(e)}"

            # Validate response structure
            if not isinstance(weather_data, dict):
                self.led.off()
                return "Invalid response format"

            if "current_weather" not in weather_data:
                self.led.off()
                return "Missing weather data in response"

            current_weather = weather_data.get("current_weather", {})
            if not isinstance(current_weather, dict):
                self.led.off()
                return "Invalid weather data format"

            temperature = current_weather.get("temperature")
            if temperature is None:
                self.led.off()
                return "Temperature data missing"

            self.led.off()
            return f"{temperature} F"

        except OSError as e:
            self.led.off()
            return f"Network error: {self.handle_os_error(e)}"
        except Exception as e:
            self.led.off()
            return f"Error: {str(e)}"
        finally:
            self.led.off()

    def set_time(self) -> bool:
        try:
            time = self.http.get(
                f"https://timeapi.io/api/time/current/ip?ipAddress={self.ip_address}"
            )
            if time is None or time.text is None:
                print("Time is empty")
                return False
            if time.text == "Unable to connect to the server.":
                print("Server error.")
                return False
            if time.text.startswith("GET Request Failed"):
                print("Request Failed 3")
                return False
            if time.text == "Invalid ip address":
                print(f"Invalid ip address: {self.ip_address}")
                return False

            # Parse JSON response
            try:
                time_data = time.json()
                if not isinstance(time_data, dict):
                    raise ValueError("Response is not a valid JSON object")
            except Exception as e:
                print(f"JSON parsing error: {e}")
                return False

            # Check if all expected keys are present
            expected_keys = [
                "year",
                "month",
                "day",
                "hour",
                "minute",
                "seconds",
                "dayOfWeek",
            ]
            if not all(key in time_data for key in expected_keys):
                print(f"Missing keys in response: {time_data}")
                return False

            # Extract time data
            year = time_data["year"]
            month = time_data["month"]
            day = time_data["day"]
            hour = time_data["hour"]
            minute = time_data["minute"]
            second = time_data["seconds"]
            day_of_week = time_data["dayOfWeek"]

            # Set RTC time
            self.rtc.datetime((year, month, day, day_of_week, hour, minute, second, 0))
            return True
        except OSError as e:
            self.handle_os_error(e)
            return False
        except Exception as e:
            print(f"Error in set_time: {e}")
            return False

    def get_time(self, is_date=False, is_time=False) -> str:
        if is_date:
            date = self.rtc.datetime()
            return f"{date[1]}/{date[2]}/{date[0]}"
        if is_time:
            time = self.rtc.datetime()
            return f"{time[4]}:{time[5]}:{time[6]}"
        date = self.rtc.datetime()
        self.last_time = f"{date[1]}/{date[2]}/{date[0]} {date[4]}:{date[5]}:{date[6]}"
        return self.last_time

    def update_time(self):
        self.lcd.write(f"Temp: {self.weather}", True, 0, 0)
        self.lcd.write(f"Time: {self.get_time(False, True)}", False, 0, 1)

weather = None
    
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
except KeyboardInterrupt:
    if weather:
        weather.http.disconnectFromWiFi()
        weather.lcd.clear()
        weather.led.off()
except Exception as e:
    if weather:
        weather.lcd.write("Error occured", True, 0, 0)
    print(f"Error occured: {e}")
    sleep(2)
    machine.reset()

