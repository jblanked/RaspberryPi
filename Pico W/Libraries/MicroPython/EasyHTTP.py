import network
import urequests_2 as requests
import ujson as json
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

    def get(self, url, headers=None, timeout: float = None) -> Response:
        if not self.isConnectedToWiFi() and not self.connectToWiFi():
            return None
        if headers:
            return requests.get(url=url, headers=headers, timeout=timeout)
        else:
            return requests.get(url=url, timeout=timeout)

    def post(self, url, payload, headers=None, timeout: float = None) -> Response:
        if not self.isConnectedToWiFi() and not self.connectToWiFi():
            return None
        if payload is None:
            return None
        if isinstance(payload, (str, bytes)):
            if headers:
                return requests.post(
                    url, headers=headers, data=payload, timeout=timeout
                )
            return requests.post(url, data=payload, timeout=timeout)
        if headers:
            return requests.post(
                url, headers=headers, data=json.dumps(payload), timeout=timeout
            )
        return requests.post(url, json_data=json.dumps(payload), timeout=timeout)

    def put(self, url, payload, headers=None, timeout: float = None) -> Response:
        if not self.isConnectedToWiFi() and not self.connectToWiFi():
            return None
        if payload is None:
            return None
        if isinstance(payload, (str, bytes)):
            if headers:
                return requests.put(url, headers=headers, data=payload, timeout=timeout)
            return requests.put(url, data=payload, timeout=timeout)
        if headers:
            return requests.put(
                url, headers=headers, json_data=json.dumps(payload), timeout=timeout
            )
        return requests.put(url, json_data=json.dumps(payload), timeout=timeout)

    def delete(self, url, headers=None, timeout: float = None) -> Response:
        if not self.isConnectedToWiFi() and not self.connectToWiFi():
            return None
        if headers:
            return requests.delete(url, headers=headers, timeout=timeout)
        return requests.delete(url, timeout=timeout)

    def head(self, url, payload, headers=None, timeout: float = None) -> Response:
        if not self.isConnectedToWiFi() and not self.connectToWiFi():
            return None
        if payload is None:
            return None
        if isinstance(payload, (str, bytes)):
            if headers:
                return requests.head(
                    url, headers=headers, data=payload, timeout=timeout
                )
            return requests.head(url, data=payload, timeout=timeout)
        if headers:
            return requests.head(
                url, headers=headers, json_data=json.dumps(payload), timeout=timeout
            )
        return requests.head(url, json_data=json.dumps(payload), timeout=timeout)

    def patch(self, url, payload, headers=None, timeout: float = None) -> Response:
        if not self.isConnectedToWiFi() and not self.connectToWiFi():
            return None
        if payload is None:
            return None
        if isinstance(payload, (str, bytes)):
            if headers:
                return requests.patch(
                    url, headers=headers, data=payload, timeout=timeout
                )
            return requests.patch(url, data=payload, timeout=timeout)
        if headers:
            return requests.patch(
                url, headers=headers, json_data=json.dumps(payload), timeout=timeout
            )
        return requests.patch(url, json_data=json.dumps(payload), timeout=timeout)
