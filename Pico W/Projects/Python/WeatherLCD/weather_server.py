"""
Companion script for the WeatherLCD project.
Use this script to create a simple web server that allows you to submit weather data and view it on a dashboard.
Use the weather_lcd.py script to display the weather data on an LCD screen and submit the data to the server.
"""

import json
import network
from EasyServer import EasyServer
from EasySD import EasySD


class WeatherServer:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.server = EasyServer(ssid, password, mode=network.STA_IF, use_led=True)
        self.sd = None

        try:
            self.sd = EasySD(auto_mount=True)
        except Exception as e:
            # No worries, save to SD card is optional
            self.sd = None

    def write_to_file(self, data, filename) -> bool:
        """
        Write a dictionary to a JSON file.

        :param data: Dictionary containing data to write.
        :param filename: Name of the file.
        :return: True if successful, False otherwise.
        """
        if data is None:
            print("Cannot write NULL data")
            return False
        try:
            if not self.sd:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f)
            else:
                self.sd.write(filename, json.dumps(data))
            return True
        except Exception as e:
            print(f"Failed to write to file '{filename}': {e}")
            return False

    def read_from_file(self, filename) -> dict:
        """
        Read a JSON file and return its content as a dictionary.

        :param filename: Name of the file.
        :return: Dictionary containing the file data.
        """
        try:
            if not self.sd:
                with open(filename, "r") as f:
                    content = f.read()
            else:
                content = self.sd.read(filename)
            if content and len(content) > 1:  # Corrected condition
                try:
                    data = json.loads(content)
                    return data
                except json.JSONDecodeError as jde:
                    print(f"JSON decoding error in '{filename}': {jde}")
                    return {"weather": []}
            return {"weather": []}
        except OSError as e:
            if len(e.args) > 0 and e.args[0] == 2:  # ENOENT: No such file or directory
                # File does not exist; return an empty weather list
                return {"weather": []}
            else:
                print(f"Error reading file '{filename}': {e}")
                return {"weather": []}
        except Exception as e:
            print(f"Unexpected error reading file '{filename}': {e}")
            return {"weather": []}

    def handle_get_weather(self):
        """
        Handler for GET /weather.
        Fetches weather data and returns the HTML dashboard.
        Also logs the access.
        """
        # Log the GET /weather access
        self.handle_logs("GET /weather accessed.")

        filename = "weather.json"
        data = self.read_from_file(filename)
        weather_entries = data.get("weather", [])

        # Generate HTML table rows
        table_rows = ""
        for entry in weather_entries:
            temperature = entry.get("temperature", "N/A")
            time_entry = entry.get("time", "N/A")
            table_rows += f"""
                <tr>
                    <td>{temperature}°C</td>
                    <td>{time_entry}</td>
                </tr>
            """

        # Enhanced HTML with styling
        weather_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Weather Dashboard</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f0f8ff;
                    margin: 0;
                    padding: 20px;
                }}
                h1 {{
                    text-align: center;
                    color: #333;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px;
                    border: 1px solid #ddd;
                    text-align: center;
                }}
                th {{
                    background-color: #4CAF50;
                    color: white;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                .form-container {{
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    max-width: 500px;
                    margin: 0 auto;
                }}
                .form-container input[type="number"],
                .form-container input[type="text"] {{
                    width: 100%;
                    padding: 10px;
                    margin: 5px 0 15px 0;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                }}
                .form-container input[type="submit"] {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }}
                .form-container input[type="submit"]:hover {{
                    background-color: #45a049;
                }}
                .message {{
                    display: inline-block;
                    padding: 20px;
                    background-color: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <h1>Weather Dashboard</h1>
            <table>
                <tr>
                    <th>Temperature</th>
                    <th>Time</th>
                </tr>
                {table_rows if table_rows else "<tr><td colspan='2'>No data available.</td></tr>"}
            </table>

            <div class="form-container">
                <h2>Add New Weather Data</h2>
                <form action="/weather" method="POST">
                    <label for="temperature">Temperature (°F):</label>
                    <input type="number" id="temperature" name="temperature" required>

                    <label for="time">Time:</label>
                    <input type="text" id="time" name="time" placeholder="e.g., 2024-04-27 14:00" required>

                    <input type="submit" value="Submit">
                </form>
            </div>
        </body>
        </html>
        """
        return weather_html

    def handle_post_weather(self, data, max_values: int = 50):
        """
        Handler for POST /weather.
        Receives weather data and stores it.
        Also logs the POST action.

        :param data: Parsed POST data (dict for JSON, dict for URL-encoded).
        :param max_values: Maximum number of weather entries to store.
        :return: HTML response string.
        """
        filename = "weather.json"

        # Log the POST /weather action
        log_message = f"POST /weather: {data}"
        self.handle_logs(log_message)

        try:
            # Determine the type of `data` and extract parameters accordingly
            if isinstance(data, dict):
                # Data is parsed JSON
                temperature = data.get("temperature")
                time_entry = data.get("time")
            elif isinstance(data, str):
                # Data is URL-encoded string; parse it into a dictionary
                parsed_data = {}
                for pair in data.split("&"):
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        parsed_data[key] = value.replace("+", " ")
                temperature = parsed_data.get("temperature")
                time_entry = parsed_data.get("time")
            else:
                # Unsupported data type
                print(f"Unsupported data type: {type(data)}")
                return "<h1>400 Bad Request</h1><p>Unsupported data format.</p>"

            # Validate received data
            if temperature is None or time_entry is None:
                print("Invalid POST data: Missing temperature or time.")
                return "<h1>400 Bad Request</h1><p>Missing temperature or time.</p>"

            # Convert temperature to float
            try:
                temperature = float(temperature)
            except ValueError:
                print("Invalid temperature value.")
                return "<h1>400 Bad Request</h1><p>Invalid temperature value.</p>"

            # Read existing data
            existing_data = self.read_from_file(filename)
            if not isinstance(existing_data, dict):
                print(f"Malformed data structure in '{filename}'. Resetting data.")
                existing_data = {"weather": []}

            weather_array = existing_data.get("weather", [])
            if not isinstance(weather_array, list):
                print(
                    f"Malformed weather data in '{filename}'. Resetting weather list."
                )
                weather_array = []

            # Append new entry with consistent data types
            new_entry = {
                "temperature": temperature,  # Stored as float
                "time": str(time_entry),  # Stored as string
            }
            weather_array.append(new_entry)

            # Ensure only the most recent `max_values` entries are kept
            if len(weather_array) > max_values:
                # Remove the oldest entries (from the beginning of the list)
                weather_array = weather_array[-max_values:]

            # Update the existing data
            existing_data["weather"] = weather_array

            # Write back to file
            if self.write_to_file(existing_data, filename):

                # Return success HTML with redirect
                success_html = """
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta http-equiv="refresh" content="2;url=/weather">
                        <title>Success</title>
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                background-color: #f0f8ff;
                                text-align: center;
                                padding-top: 50px;
                            }}
                            .message {{
                                display: inline-block;
                                padding: 20px;
                                background-color: #d4edda;
                                color: #155724;
                                border: 1px solid #c3e6cb;
                                border-radius: 5px;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="message">
                            <h2>Weather data submitted successfully!</h2>
                            <p>Redirecting to the dashboard...</p>
                        </div>
                    </body>
                    </html>
                """
                return success_html
            else:
                return "<h1>500 Internal Server Error</h1><p>Failed to write data.</p>"

        except Exception as e:
            print(f"Error handling POST data: {e}")
            # Log the error
            self.handle_logs(f"Error handling POST /weather: {e}")
            return f"<h1>500 Internal Server Error</h1><p>{e}</p>"

    def redirect_to_weather(self):
        """
        Handler to redirect root ("/") to /weather.
        Also logs the redirection.
        """
        # Log the redirection
        self.handle_logs("GET / accessed. Redirecting to /weather.")

        redirect_html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta http-equiv="refresh" content="0;url=/weather">
                <title>Redirecting...</title>
            </head>
            <body>
                <p>Redirecting to <a href="/weather">Weather Dashboard</a>...</p>
            </body>
            </html>
        """
        return redirect_html

    def handle_logs(self, last_log_message=None) -> str:
        """
        Handler to show logs.
        If `last_log_message` is provided, it adds it to the logs.
        Accessing /logs does not add a log entry.

        :param last_log_message: Optional log message to add.
        :return: HTML string displaying the logs.
        """
        filename = "logs.txt"
        content = ""

        # Add new log message if provided, limiting to the last 100 entries
        if last_log_message:
            try:
                # Read existing logs
                try:
                    if not self.sd:
                        with open(filename, "r") as f:
                            existing_logs = f.read().splitlines()
                    else:
                        existing_logs = self.sd.read(filename).splitlines()
                except OSError as e:
                    if (
                        len(e.args) > 0 and e.args[0] == 2
                    ):  # ENOENT: No such file or directory
                        existing_logs = []
                    else:
                        print(e)
                        existing_logs = []

                # append the new message and limit to 100 entries
                logs = [last_log_message] + existing_logs
                # keep only the last 100 entries
                logs = logs[:100]

                # Write back to file
                if not self.sd:
                    with open(filename, "w") as f:
                        f.write("\n".join(logs))
                else:
                    self.sd.write(filename, "\n".join(logs))

                content = "\n".join(logs)
            except Exception as e:
                print(f"Error updating logs: {e}")
                content = ""

        else:
            # Read existing logs from file
            try:
                if not self.sd:
                    with open(filename, "r") as f:
                        content = f.read()
                else:
                    content = self.sd.read(filename)
            except OSError as e:
                # File does not exist; create it
                if len(e.args) > 0 and e.args[0] == 2:  # ENOENT
                    if not self.sd:
                        with open(filename, "w") as f:
                            f.write("")
                    else:
                        self.sd.write(filename, "")
                    content = ""
                else:
                    print(e)
                    return """
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <title>Logs</title>
                    </head>
                    <body>
                        <h1>Logs</h1>
                        <p>Error reading logs.</p>
                    </body>
                    </html>
                    """
            except Exception as e:
                print(e)
                return """
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <title>Logs</title>
                </head>
                <body>
                    <h1>Logs</h1>
                    <p>No logs available.</p>
                </body>
                </html>
                """

        # Create log entries as table rows
        log_entries = "\n".join(
            f"<tr><td>{entry}</td></tr>" for entry in content.splitlines()
        )

        # Generate the HTML, injecting the pre-built table rows
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Logs</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f6f9;
                    color: #333;
                    padding: 20px;
                    margin: 0;
                }}
                h1 {{
                    text-align: center;
                    color: #444;
                }}
                .log-table {{
                    width: 100%;
                    max-width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background-color: #fff;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                .log-table th, .log-table td {{
                    padding: 12px;
                    border: 1px solid #ddd;
                    text-align: left;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }}
                .log-table th {{
                    background-color: #007bff;
                    color: white;
                }}
                .log-table tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <h1>Logs</h1>
            <table class="log-table">
                <tr>
                    <th>Log Entry</th>
                </tr>
                {log_entries if log_entries else "<tr><td>No logs available.</td></tr>"}
            </table>
        </body>
        </html>
        """

    def run(self):
        # Start the server
        if not self.server.start(port=80):
            print("Failed to start the server. Exiting.")
            self.server.close()

        # Register GET route for /weather
        self.server.add_route("/weather", self.handle_get_weather, method="GET")

        # Register POST route for /weather
        self.server.add_route("/weather", self.handle_post_weather, method="POST")

        # Register root ("/") route to redirect to /weather
        self.server.add_route("/", self.redirect_to_weather, method="GET")

        # Register GET route for /logs without logging the access
        self.server.add_route("/logs", self.handle_logs, method="GET")

        # Run the server
        try:
            self.server.run()
        except KeyboardInterrupt:
            self.server.close()
        except OSError as e:
            print(e)
            self.server.close()
        except Exception as e:
            print(e)
            self.server.close()


# Run the WeatherServer
if __name__ == "__main__":
    ws = WeatherServer("your_ssid", "your_password")
    ws.run()
