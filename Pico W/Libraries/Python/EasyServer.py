import network
import socket
import time


class EasyServer:
    def __init__(self, ssid, password, mode=network.STA_IF, append_question_mark=True):
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

    def close(self, reason=None):
        if reason:
            print(reason)
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
            return True
        except Exception as e:
            print("Error:", e)
            return False

    def setupAccessPoint(self):
        """
        Configure the device as an Access Point.
        """
        if self.mode != network.AP_IF:
            print("setupAccessPoint is only available in Access Point mode.")
            return False

        try:
            self.wlan.config(ssid=self.ssid, password=self.password)
            self.wlan.active(True)
            self.local_ip = self.wlan.ifconfig()[0]
            print(f"Access Point '{self.ssid}' started.")
            return True
        except Exception as e:
            print("Failed to set up Access Point:", e)
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
            self.server.bind(address)
            self.server.listen(5)  # Increased backlog for multiple connections
            print(f"Server started at http://{self.local_ip}")
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
                client, addr = self.server.accept()
                try:
                    request = client.recv(1024)
                    if not request:
                        client.close()
                        continue
                    request = request.decode("utf-8", "ignore")

                    # Parse the request to get the path and method
                    try:
                        lines = request.split("\r\n")
                        request_line = lines[0]
                        method, path, protocol = request_line.split()
                    except ValueError:
                        client.close()
                        continue

                    # Remove query parameters if any
                    if "?" in path:
                        path = path.split("?")[0]

                    # Normalize path
                    path = path.rstrip("/") if path != "/" else path

                    # Initialize variables for response
                    response_content = ""
                    status_line = ""
                    content_type = "Content-Type: text/html\r\n\r\n"

                    # Check if the path exists in routes
                    if path in self.routes:
                        route_methods = self.routes[path]
                        if method in route_methods:
                            route_info = route_methods[method]
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
                                        status_line = "500 Internal Server Error\r\n"
                                else:
                                    response_content = "<h1>500 Internal Server Error</h1><p>No handler defined.</p>"
                                    status_line = "500 Internal Server Error\r\n"

                                if not status_line:
                                    status_line = "200 OK\r\n"

                            elif method == "POST":
                                # Extract the body data for POST
                                try:
                                    # Find the empty line separating headers and body
                                    header_end = request.find("\r\n\r\n")
                                    if header_end != -1:
                                        body = request[header_end + 4 :]
                                        # Optionally, handle URL-encoded or JSON data here
                                        # For simplicity, we'll pass the raw body
                                    else:
                                        body = ""
                                except Exception as e:
                                    print(f"Error parsing POST data: {e}")
                                    body = ""

                                # Execute the handler with the POST data
                                if handler:
                                    try:
                                        response_content = handler(body)
                                    except Exception as handler_e:
                                        print(
                                            f"Handler error for path '{path}': {handler_e}"
                                        )
                                        response_content = "<h1>500 Internal Server Error</h1><p>Handler execution failed.</p>"
                                        status_line = "500 Internal Server Error\r\n"
                                else:
                                    response_content = "<h1>500 Internal Server Error</h1><p>No handler defined.</p>"
                                    status_line = "500 Internal Server Error\r\n"

                                if not status_line:
                                    status_line = "200 OK\r\n"
                            else:
                                # Method not supported
                                status_line = "405 Method Not Allowed\r\n"
                                content_type = "Content-Type: text/html\r\n\r\n"
                                response_content = "<h1>405 Method Not Allowed</h1>"
                        else:
                            # Method not supported for this path
                            status_line = "405 Method Not Allowed\r\n"
                            content_type = "Content-Type: text/html\r\n\r\n"
                            response_content = "<h1>405 Method Not Allowed</h1>"
                    elif path == "/":
                        # Handle Home page (assuming GET)
                        if method == "GET":
                            response_content = self.webpage()
                            status_line = "200 OK\r\n"
                        else:
                            status_line = "405 Method Not Allowed\r\n"
                            content_type = "Content-Type: text/html\r\n\r\n"
                            response_content = "<h1>405 Method Not Allowed</h1>"
                    else:
                        # Handle 404 Not Found
                        status_line = "404 Not Found\r\n"
                        content_type = "Content-Type: text/html\r\n\r\n"
                        response_content = "<h1>404 Not Found</h1>"

                    # Server log
                    print(f'"{method} {path} {protocol}" {status_line.strip()}')

                    # Send the HTTP response
                    response = (
                        self.http_type
                        + " "
                        + status_line
                        + content_type
                        + response_content
                    )
                    client.sendall(response.encode("utf-8"))
                except OSError as e:
                    print(f"Connection error: {e}")
                except Exception as e:
                    print(f"Unexpected error while handling request: {e}")
                finally:
                    client.close()
            except KeyboardInterrupt:
                self.close("Server stopped by user")
                break
            except OSError as e:
                print(f"Server accept error: {e}")
                # Optionally, implement a short delay here
                time.sleep(1)
                continue
            except Exception as e:
                print(f"Unexpected error: {e}")
                continue
