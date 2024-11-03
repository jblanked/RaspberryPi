import json
import network
import socket
import time
from EasyServer import (
    EasyServer,
)  # https://github.com/jblanked/RaspberryPi/blob/main/Pico%20W/Libraries/Python/EasyServer.py


def write_to_file(data, filename) -> bool:
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
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return True
    except Exception as e:
        print(f"Failed to write to file '{filename}': {e}")
        return False


def read_from_file(filename) -> dict:
    """
    Read a JSON file and return its content as a dictionary.

    :param filename: Name of the file.
    :return: Dictionary containing the file data.
    """
    try:
        with open(filename, "r") as f:
            content = f.read()
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


def handle_get_weather():
    """
    Handler for GET /weather.
    Fetches weather data and returns the HTML dashboard.
    """
    filename = "weather.json"
    data = read_from_file(filename)
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


def handle_post_weather(data, max_values: int = 50):
    """
    Handler for POST /weather.
    Receives weather data and stores it.

    :param data: Raw POST data (URL-encoded).
    :return: HTML response string.
    """
    filename = "weather.json"
    try:
        # Parse URL-encoded data
        parsed_data = {}
        for pair in data.split("&"):
            if "=" in pair:
                key, value = pair.split("=", 1)
                parsed_data[key] = value.replace("+", " ")  # Replace '+' with space

        temperature = parsed_data.get("temperature")
        time_entry = parsed_data.get("time")

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
        existing_data = read_from_file(filename)
        if not isinstance(existing_data, dict):
            print(f"Malformed data structure in '{filename}'. Resetting data.")
            existing_data = {"weather": []}

        weather_array = existing_data.get("weather", [])
        if not isinstance(weather_array, list):
            print(f"Malformed weather data in '{filename}'. Resetting weather list.")
            weather_array = []

        # Append new entry with consistent data types
        new_entry = {
            "temperature": temperature,  # Stored as float
            "time": str(time_entry),  # Stored as string
        }
        weather_array.append(new_entry)

        # Ensure only the most recent 50 entries are kept
        if len(weather_array) > max_values:
            # Remove the oldest entries (from the beginning of the list)
            # This keeps the last 50 entries
            weather_array = weather_array[-max_values:]
            print(f"Trimmed weather list to the most recent {max_values} entries.")

        # Update the existing data
        existing_data["weather"] = weather_array

        # Write back to file
        if write_to_file(existing_data, filename):
            # Redirect back to GET /weather with a success message
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
        return f"<h1>500 Internal Server Error</h1><p>{e}</p>"


def redirect_to_weather():
    """
    Handler to redirect root ("/") to /weather.
    """
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


"""
# Usage Example
if __name__ == "__main__":
    # Initialize the server with your WiFi credentials and mode
    # Replace "Your_STA_SSID" and "Your_STA_Password" with your actual credentials
    server = EasyServer("your_ssid", "your_pass", mode=network.STA_IF)

    # Start the server
    if not server.start(port=80):
        print("Failed to start the server. Exiting.")
        server.close()

    # Register GET route for /weather
    server.add_route("/weather", handle_get_weather, method="GET")

    # Register POST route for /weather
    server.add_route("/weather", handle_post_weather, method="POST")

    # Register root ("/") route to redirect to /weather
    server.add_route("/", redirect_to_weather, method="GET")

    # Run the server
    try:
        server.run()
    except KeyboardInterrupt:
        server.close()
    except OSError as e:
        print(e)
        server.close()
    except Exception as e:
        print(e)
"""
