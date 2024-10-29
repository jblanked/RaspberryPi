#include "EasyLCD.h"  // https://github.com/jblanked/RaspberryPi/blob/main/Pico%20W/Libraries/Arduino/EasyLCD.h
#include "EasyHTTP.h" // https://github.com/jblanked/RaspberryPi/blob/main/Pico%20W/Libraries/Arduino/EasyHTTP.h
#include "EasyPin.h"  // https://github.com/jblanked/RaspberryPi/blob/main/Pico%20W/Libraries/Arduino/EasyPin.h

bool isConnected = false;
EasyLCD lcd(0x27, 16, 2); // change 0x27 to 0x3F if your LCD address is 0x3F
EasyHTTP http("your_ssid", "your_password");
EasyPin LED(PICO_LED);
String weather;
String lastTime;
String ipAddress;
int weatherInterval = 0;

void setup()
{
  // Initialize LCD
  lcd.begin();

  // Connect to WiFi
  lcd.write(" Connecting to ", 0, true);
  lcd.write("  WiFi now....  ", 1, false);
  LED.on();
  if (http.connectToWifi())
  {
    LED.off();
    lcd.write("WiFi connected!", 0, true);
    isConnected = true;
  }
  else
  {
    LED.off();
    lcd.write("ERROR.", 0, true);
    lcd.write("Reboot device.", 1, false);
    delay(2000);
  }
}
void loop()
{
  if (!isConnected)
  {
    lcd.write("ERROR.", 0, false);
    lcd.write("Reboot device.", 1, false);
    delay(1000);
    return;
  }

  // if delay is over, get weather
  if (millis() > weatherInterval)
  {
    weather = get_weather();
    lastTime = get_time(false, true);
    if (weather.length() <= 7)
    {
      lcd.write("Temp: " + weather, 0, true);
      lcd.write("Time: " + lastTime, 1, false);
    }
    else
    {
      lcd.write("Failed:", 0, true);
      lcd.write(weather, 1, false);
    }
    weatherInterval = millis() + (60000 * 1); // 1 minute
  }
}

String get_weather()
{
  LED.on();

  // get lat and long
  String ip_info = http.get("https://ipwhois.app/json/");
  if (ip_info == "")
  {
    return "IP info is empty";
  }
  else if (ip_info == "Unable to connect to the server.")
  {
    LED.off();
    return "Server error.";
  }
  else if (ip_info.startsWith("GET Request Failed"))
  {
    LED.off();
    return "Request Failed 1";
  }

  // Parse JSON
  DynamicJsonDocument doc(2048);
  DeserializationError error = deserializeJson(doc, ip_info);
  if (error)
  {
    LED.off();
    return "JSON error 1";
  }
  if (!doc.containsKey("latitude") || !doc.containsKey("longitude"))
  {
    LED.off();
    return "Invalid JSON 1";
  }

  // Get lat and long
  String lat = doc["latitude"].as<String>();
  String lon = doc["longitude"].as<String>();
  ipAddress = doc["ip"].as<String>();

  if (lat == "" || lat == NULL)
  {
    LED.off();
    return "Lat is empty";
  }
  if (lon == "" || lon == NULL)
  {
    LED.off();
    return "Lon is empty";
  }

  // get weather
  String totalWeather = http.get(("https://api.open-meteo.com/v1/forecast?latitude=") + lat + ("&longitude=") + lon + ("&current=temperature_2m,precipitation,rain,showers,snowfall&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&forecast_days=1"));
  if (totalWeather == "")
  {
    LED.off();
    return "Weather is empty";
  }
  else if (totalWeather == "Unable to connect to the server.")
  {
    LED.off();
    return "Server error.";
  }
  else if (totalWeather.startsWith("GET Request Failed"))
  {
    LED.off();
    return "Request Failed 2";
  }

  // Parse JSON
  DynamicJsonDocument weatherDoc(1024);
  error = deserializeJson(weatherDoc, totalWeather);
  if (error)
  {
    LED.off();
    return "JSON error 2";
  }

  if (!weatherDoc.containsKey("current"))
  {
    LED.off();
    return "Invalid JSON 2";
  }

  // Get current temperature
  String returnedWeather = weatherDoc["current"]["temperature_2m"].as<String>();

  if (returnedWeather == "" || returnedWeather == NULL)
  {
    LED.off();
    return "Weather is empty";
  }

  LED.off();
  return returnedWeather + " F";
}

String get_time(bool dateOnly = false, bool timeOnly = false)
{
  String time = http.get("https://timeapi.io/api/time/current/ip?ipAddress=" + ipAddress);
  if (time == "")
  {
    return "Time is empty";
  }
  else if (time == "Unable to connect to the server.")
  {
    return "Server error.";
  }
  else if (time.startsWith("GET Request Failed"))
  {
    return "Request Failed";
  }

  // Parse JSON
  DynamicJsonDocument doc(1024);
  DeserializationError error = deserializeJson(doc, time);
  if (error)
  {
    return "JSON error";
  }
  if (!doc.containsKey("dateTime"))
  {
    return "Invalid JSON";
  }

  // Get time
  String returnedTime = doc["dateTime"].as<String>();

  if (returnedTime == "" || returnedTime == NULL)
  {
    return "Time is empty";
  }

  if (dateOnly)
  {
    return doc["date"].as<String>();
  }
  else if (timeOnly)
  {
    return doc["time"].as<String>();
  }
  return returnedTime;
}
