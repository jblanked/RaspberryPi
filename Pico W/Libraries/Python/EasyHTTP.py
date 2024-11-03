import network
import urequests_2 as requests
import json
import time


class EasyHTTP:
    def __init__(self, ssid, password) -> EasyHTTP:
        self.local_ip = None
        self.wifi_ip = None
        self.wlan = network.WLAN(network.STA_IF)
        self.ssid = ssid
        self.password = password

    def connectToWiFi(self) -> bool:
        if self.ssid is None or self.password is None:
            print("Neither the SSID or Password can be empty")
            return False
        try:
            self.wlan.active(True)
            if not self.wlan.isconnected():
                self.wlan.connect(self.ssid, self.password)
                while not self.wlan.isconnected():
                    time.sleep(1)
                    pass
            self.local_ip = self.wlan.ifconfig()[0]
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def disconnectFromWiFi(self):
        if self.isConnectedToWiFi():
            self.wlan.disconnect()

    def isConnectedToWiFi(self) -> bool:
        return self.wlan.isconnected()

    def get(self, url, headers=None) -> Response:
        if not self.isConnectedToWiFi() and not self.connectToWiFi():
            return None
        if headers:
            return requests.get(url=url, headers=headers)
        else:
            return requests.get(url=url)

    def post(self, url, data, headers=None) -> Response:
        if not self.isConnectedToWiFi() and not self.connectToWiFi():
            return None
        if data is None:
            return None
        if isinstance(data, (str, bytes)):
            if headers:
                return requests.post(url, headers=headers, data=data)
            return requests.post(url, data=data)
        if headers:
            return requests.post(url, headers=headers, data=json.dumps(data))
        return requests.post(url, data=json.dumps(data))

    def put(self, url, data, headers=None) -> Response:
        if not self.isConnectedToWiFi() and not self.connectToWiFi():
            return None
        if data is None:
            return None
        if isinstance(data, (str, bytes)):
            return requests.put(url, headers=headers, data=data)
        return requests.put(url, headers=headers, data=json.dumps(data))

    def delete(self, url, headers=None) -> Response:
        if not self.isConnectedToWiFi() and not self.connectToWiFi():
            return None
        return requests.delete(url, headers=headers)

    def head(self, url, data, headers=None) -> Response:
        if not self.isConnectedToWiFi() and not self.connectToWiFi():
            return None
        if data is None:
            return None
        if isinstance(data, (str, bytes)):
            return requests.head(url, headers=headers, data=data)
        return requests.head(url, headers=headers, data=json.dumps(data))

    def patch(self, url, data, headers=None) -> Response:
        if not self.isConnectedToWiFi() and not self.connectToWiFi():
            return None
        if data is None:
            return None
        if isinstance(data, (str, bytes)):
            return requests.patch(url, headers=headers, data=data)
        return requests.patch(url, headers=headers, data=json.dumps(data))
