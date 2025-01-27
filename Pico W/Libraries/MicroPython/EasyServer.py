from machine import Pin
import network
import socket
import time
import json
import errno


class EasyServer:
    def __init__(
        self,
        ssid,
        password,
        mode=network.STA_IF,
        append_question_mark=True,
        use_led=False,
    ):
        """
        Initialize the EasyServer.

        :param ssid: SSID for STA mode or AP mode.
        :param password: Password for STA mode or AP mode.
        :param mode: network.STA_IF for Station mode or network.AP_IF for Access Point mode.
        :param append_question_mark: Whether to append '?' to URLs.
        """
        self.mode = mode
        self.wlan = network.WLAN(self.mode)
        self.ssid = ssid
        self.password = password
        self.local_ip = None
        self.server = None
        self.routes = {}  # Routing table as a dictionary
        self.http_type = "HTTP/1.1"
        self.append_question_mark = append_question_mark
        self.client = None
        self.last_response = None
        self.led = Pin("LED", Pin.OUT) if use_led else None  # LED on the Pico W

    def close(self, reason=None):
        if reason:
            print(reason)
        if self.client is not None:
            self.client.close()
        if self.server:
            self.server.close()
        if self.wlan and self.wlan.active():
            self.disconnectFromWiFi()
        print("Server closed.")

    def connectToWiFi(self):
        """
        Connect to Wi-Fi in Station mode.
        """
        if self.mode != network.STA_IF:
            print("connectToWiFi is only available in Station mode.")
            return False

        if not self.ssid or not self.password:
            print("Neither the SSID nor the Password can be empty")
            return False

        if self.led:
            self.led.on()
        try:
            self.wlan.active(True)
            if not self.wlan.isconnected():
                print("Connecting to WiFi...")
                self.wlan.connect(self.ssid, self.password)
                while not self.wlan.isconnected():
                    print(".", end="")
                    time.sleep(1)
            self.local_ip = self.wlan.ifconfig()[0]
            print(f"\nConnected to {self.ssid} successfully.")
            if self.led:
                self.led.off()
            return True
        except Exception as e:
            print("Error:", e)
            if self.led:
                self.led.off()
            return False

    def setupAccessPoint(self):
        """
        Configure the device as an Access Point.
        """
        if self.mode != network.AP_IF:
            print("setupAccessPoint is only available in Access Point mode.")
            return False
        if self.led:
            self.led.on()
        try:
            self.wlan.config(ssid=self.ssid, password=self.password)
            self.wlan.active(True)
            self.local_ip = self.wlan.ifconfig()[0]
            print(f"Access Point '{self.ssid}' started.")
            if not self.led:
                self.led.off()
            return True
        except Exception as e:
            print("Failed to set up Access Point:", e)
            if not self.led:
                self.led.off()
            return False

    def disconnectFromWiFi(self):
        self.wlan.disconnect()

    def isConnectedToWiFi(self):
        return self.wlan.isconnected()

    def start(self, port=80):
        if self.mode == network.STA_IF:
            if not self.isConnectedToWiFi() and not self.connectToWiFi():
                return False
        elif self.mode == network.AP_IF:
            if not self.setupAccessPoint():
                return False
        else:
            print("Unsupported mode. Use network.STA_IF or network.AP_IF.")
            return False

        try:
            address = socket.getaddrinfo("0.0.0.0", port)[0][-1]
            self.server = socket.socket()
            self.server.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
            )  # Optional: Reuse address
            self.server.bind(address)
            self.server.listen(5)  # Increased backlog for multiple connections
            print(f"Server started at http://{self.local_ip}")
            if self.led:
                self.led.off()
                time.sleep(0.5)
                #
                self.led.on()
                time.sleep(0.5)
                self.led.off()
                time.sleep(0.5)
                self.led.on()
                time.sleep(0.5)
                self.led.off()
                time.sleep(0.5)
                self.led.on()
                time.sleep(0.5)
                self.led.off()
                time.sleep(0.5)
            return True
        except Exception as e:
            print("Failed to start server:", e)
            return False

    def add_route(self, path, handler, method="GET"):
        """
        Register a new route with its handler.

        :param path: URL path (e.g., "/custom")
        :param handler: Function to handle the route. It should return the HTML response as a string.
        :param method: HTTP method (e.g., "GET", "POST")
        """
        normalized_path = path.rstrip("/") if path != "/" else path
        method = method.upper()

        if normalized_path not in self.routes:
            self.routes[normalized_path] = {}

        self.routes[normalized_path][method] = {
            "handler": handler,
        }

    def accept_points(self):
        """
        Serve the acceptance page for users.
        """
        html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Accept Terms</title>
                <script type="text/javascript">
                    function acceptTerms() {
                        // Redirect to a success page or perform other actions
                        alert("Terms Accepted!");
                        window.location.href = "/";
                    }
                </script>
            </head>
            <body>
                <h1>Welcome!</h1>
                <p>Please accept the terms and conditions to continue.</p>
                <button onclick="acceptTerms()">Accept</button>
            </body>
            </html>
        """
        return html

    def webpage(self):
        """
        Generate a basic HTML page.
        """
        html = """ 
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>EasyServer</title>
            </head>
            <body>
                <h1>EasyServer</h1>
                <p>Welcome to the EasyServer.</p>
            </body>
            </html>
        """
        return html

    def run(self):
        if not self.server:
            print("Server is not started. Call start() before run().")
            return

        print("Server is running. Press Ctrl+C to stop.")
        while True:
            try:
                self.client, addr = self.server.accept()
                buffer = b""  # Initialize an empty buffer for the incoming data
                keep_alive = False  # Disable keep-alive
                if self.led:
                    self.led.off()
                while True:
                    try:
                        data = self.client.recv(1024)
                        if not data:
                            print(f"Client {addr} disconnected.")
                            break
                        buffer += data
                        if self.led:
                            self.led.on()
                        # Check if we've received all headers
                        header_end = buffer.find(b"\r\n\r\n")
                        if header_end == -1:
                            # Headers not fully received yet
                            continue

                        # Split headers and body
                        headers_part = buffer[:header_end].decode("utf-8", "ignore")
                        body_part = buffer[header_end + 4 :]

                        # Parse request line and headers
                        lines = headers_part.split("\r\n")
                        request_line = lines[0]
                        try:
                            method, path, protocol = request_line.split()
                        except ValueError:
                            self.client.close()
                            print(
                                f"Malformed request line from {addr}. Connection closed."
                            )
                            if self.led:
                                self.led.off()
                            break

                        headers = {}
                        for header_line in lines[1:]:
                            if not header_line:
                                continue
                            parts = header_line.split(": ", 1)
                            if len(parts) == 2:
                                headers[parts[0].lower()] = parts[1]

                        # Regardless of client headers, set keep_alive = False
                        keep_alive = False

                        # Determine content length
                        content_length = int(headers.get("content-length", "0"))

                        # Check if the entire body has been received
                        if len(body_part) < content_length:
                            # Need to read more data
                            while len(body_part) < content_length:
                                more_data = self.client.recv(1024)
                                if not more_data:
                                    break
                                body_part += more_data

                        body = body_part[:content_length]

                        # Normalize path (remove query parameters and trailing slash)
                        if "?" in path:
                            path = path.split("?")[0]
                        path = path.rstrip("/") if path != "/" else path

                        # Initialize response variables
                        response_content = ""
                        status_line = "200 OK\r\n"  # Default status
                        response_headers = {
                            "Content-Type": "text/html",
                            "Connection": "close",
                        }

                        # Handle the request based on the method and path
                        if path in self.routes:
                            route_methods = self.routes[path]
                            if method in route_methods:
                                route_info = self.routes[path][method]
                                handler = route_info["handler"]

                                if method == "GET":
                                    # Execute the handler for GET (no data)
                                    if handler:
                                        try:
                                            response_content = handler()
                                        except Exception as handler_e:
                                            print(
                                                f"Handler error for path '{path}': {handler_e}"
                                            )
                                            response_content = "<h1>500 Internal Server Error</h1><p>Handler execution failed.</p>"
                                            status_line = (
                                                "500 Internal Server Error\r\n"
                                            )

                                elif method == "POST":
                                    # Determine Content-Type
                                    content_type_header = headers.get(
                                        "content-type", ""
                                    )

                                    if "application/json" in content_type_header:
                                        # Parse JSON data
                                        try:
                                            parsed_body = json.loads(
                                                body.decode("utf-8")
                                            )
                                        except ValueError as ve:
                                            print(f"JSON decoding error: {ve}")
                                            response_content = "<h1>400 Bad Request</h1><p>Invalid JSON.</p>"
                                            status_line = "400 Bad Request\r\n"
                                            parsed_body = None
                                    else:
                                        # Assume URL-encoded
                                        try:
                                            parsed_body = {}
                                            for pair in body.decode("utf-8").split("&"):
                                                if "=" in pair:
                                                    key, value = pair.split("=", 1)
                                                    parsed_body[key] = value.replace(
                                                        "+", " "
                                                    )
                                        except Exception as e:
                                            print(f"Error parsing POST data: {e}")
                                            parsed_body = {}

                                    # Execute the handler with the parsed data
                                    try:
                                        handler_response = handler(parsed_body)
                                        # Determine if handler returned a tuple or single value
                                        if isinstance(handler_response, tuple):
                                            response_content, handler_status_line = (
                                                handler_response
                                            )
                                            status_line = handler_status_line
                                        else:
                                            response_content = handler_response
                                            # status_line remains "200 OK\r\n"
                                    except Exception as handler_e:
                                        print(
                                            f"Handler error for path '{path}': {handler_e}"
                                        )
                                        response_content = "<h1>500 Internal Server Error</h1><p>Handler execution failed.</p>"
                                        status_line = "500 Internal Server Error\r\n"
                        elif path == "/":
                            # Handle Home page (assuming GET)
                            if method == "GET":
                                response_content = self.webpage()
                            else:
                                status_line = "405 Method Not Allowed\r\n"
                                response_headers["Content-Type"] = "text/html"
                                response_content = "<h1>405 Method Not Allowed</h1>"
                        else:
                            # Path not found
                            status_line = "404 Not Found\r\n"
                            response_headers["Content-Type"] = "text/html"
                            response_content = "<h1>404 Not Found</h1>"

                        # Build the full HTTP response
                        response = f"HTTP/1.1 {status_line}"
                        for header, value in response_headers.items():
                            response += f"{header}: {value}\r\n"
                        response += "\r\n"
                        response += response_content

                        # Send the response
                        self.client.send(response.encode("utf-8"))
                        print(f'"{request_line}" {status_line.strip()}')

                        # Remove the processed request from the buffer
                        buffer = buffer[header_end + 4 + content_length :]
                        if self.led:
                            self.led.off()
                        break  # Close connection after response

                    except OSError as e:
                        if e.args and e.args[0] == errno.ETIMEDOUT:
                            print(f"Connection with {addr} timed out.")
                        else:
                            print(f"OS error: {e}")
                        if self.led:
                            self.led.off()
                        break
                    except Exception as e:
                        print(f"Unexpected error: {e}")
                        if self.led:
                            self.led.off()
                        break
                    finally:
                        if self.led:
                            self.led.off()

                # Close the client connection
                self.client.close()
            except KeyboardInterrupt:
                self.close("Server stopped by user")
                break
            except OSError as e:
                print(f"Server accept error: {e}")
                time.sleep(1)
                continue
            except Exception as e:
                print(f"Unexpected error: {e}")
                continue
            finally:
                if self.led:
                    self.led.off()
