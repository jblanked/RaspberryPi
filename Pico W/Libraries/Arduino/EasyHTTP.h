#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <Arduino.h>

class EasyHTTP
{
public:
    // Constructor
    EasyHTTP(const char *ssid, const char *pass)
    {
        this->ssid = ssid;
        this->pass = pass;
    }

    const char *ssid;
    const char *pass;

    //  Connect to Wifi
    bool connectToWifi()
    {
        if (String(ssid) == "" || String(pass) == "")
        {
            return false;
        }

        WiFi.disconnect(true); // Ensure WiFi is disconnected before reconnecting
        WiFi.begin(ssid, pass);

        int i = 0;
        while (!this->isConnectedToWifi() && i < 20)
        {
            delay(500);
            i++;
        }

        return this->isConnectedToWifi();
    }

    // Check if the Dev Board is connected to Wifi
    bool isConnectedToWifi() { return WiFi.status() == WL_CONNECTED; }

    String ip_address()
    {
        if (!this->isConnectedToWifi() && !this->connectToWifi())
        {
            return "Failed to conenct to WiFi.";
        }
        // Get Request
        String jsonData = this->get("https://httpbin.org/get");
        if (jsonData == "")
        {
            return "GET request failed or returned empty data.";
        }
        DynamicJsonDocument doc(1024);
        DeserializationError error = deserializeJson(doc, jsonData);
        if (error)
        {
            return "Failed to parse JSON.";
        }
        if (!doc.containsKey("origin"))
        {
            return "JSON does not contain origin.";
        }
        return doc["origin"].as<String>();
    }

    String get(String url)
    {
        if (!this->isConnectedToWifi() && !this->connectToWifi())
        {
            return "Failed to conenct to WiFi.";
        }

        WiFiClientSecure client;
        client.setInsecure(); // Bypass certificate validation

        HTTPClient http;
        String payload = "";

        if (http.begin(client, url))
        {
            int httpCode = http.GET();

            if (httpCode > 0)
            {
                payload = http.getString();
                http.end();
                return payload;
            }
            else
            {
                return "GET Request Failed, error: " + http.errorToString(httpCode);
            }
            http.end();
        }
        else
        {
            return "Unable to connect to the server.";
        }

        return payload;
    }

    String get(String url, const char *headerKeys[], const char *headerValues[], int headerSize)
    {
        if (!this->isConnectedToWifi() && !this->connectToWifi())
        {
            return "Failed to conenct to WiFi.";
        }

        WiFiClientSecure client;
        client.setInsecure(); // Bypass certificate

        HTTPClient http;
        String payload = "";

        http.collectHeaders(headerKeys, headerSize);

        if (http.begin(client, url))
        {

            for (int i = 0; i < headerSize; i++)
            {
                http.addHeader(headerKeys[i], headerValues[i]);
            }

            int httpCode = http.GET();

            if (httpCode > 0)
            {
                payload = http.getString();
                http.end();
                return payload;
            }
            else
            {
                return "GET Request Failed, error: " + http.errorToString(httpCode);
            }
            http.end();
        }
        else
        {
            return "Unable to connect to the server.";
        }

        return payload;
    }

    String delete_request(String url, String payload)
    {
        if (!this->isConnectedToWifi() && !this->connectToWifi())
        {
            return "Failed to conenct to WiFi.";
        }

        WiFiClientSecure client;
        client.setInsecure(); // Bypass certificate

        HTTPClient http;
        String response = "";

        if (http.begin(client, url))
        {
            int httpCode = http.sendRequest("DELETE", payload);

            if (httpCode > 0)
            {
                response = http.getString();
                http.end();
                return response;
            }
            else
            {
                return "DELETE Request Failed, error: " + http.errorToString(httpCode);
            }
            http.end();
        }

        else
        {
            return "Unable to connect to the server.";
        }

        return response;
    }

    String delete_request(String url, String payload, const char *headerKeys[], const char *headerValues[], int headerSize)
    {
        if (!this->isConnectedToWifi() && !this->connectToWifi())
        {
            return "Failed to conenct to WiFi.";
        }

        WiFiClientSecure client;
        client.setInsecure(); // Bypass certificate

        HTTPClient http;
        String response = "";

        http.collectHeaders(headerKeys, headerSize);

        if (http.begin(client, url))
        {

            for (int i = 0; i < headerSize; i++)
            {
                http.addHeader(headerKeys[i], headerValues[i]);
            }

            int httpCode = http.sendRequest("DELETE", payload);

            if (httpCode > 0)
            {
                response = http.getString();
                http.end();
                return response;
            }
            else
            {
                return "DELETE Request Failed, error: " + http.errorToString(httpCode);
            }
            http.end();
        }

        else
        {
            return "Unable to connect to the server.";
        }

        return response;
    }

    String post(String url, String payload, const char *headerKeys[], const char *headerValues[], int headerSize)
    {
        if (!this->isConnectedToWifi() && !this->connectToWifi())
        {
            return "Failed to conenct to WiFi.";
        }

        WiFiClientSecure client;
        client.setInsecure(); // Bypass certificate

        HTTPClient http;
        String response = "";

        http.collectHeaders(headerKeys, headerSize);

        if (http.begin(client, url))
        {

            for (int i = 0; i < headerSize; i++)
            {
                http.addHeader(headerKeys[i], headerValues[i]);
            }

            int httpCode = http.POST(payload);

            if (httpCode > 0)
            {
                response = http.getString();
                http.end();
                return response;
            }
            else
            {
                return "POST Request Failed, error: " + http.errorToString(httpCode);
            }
            http.end();
        }

        else
        {
            return "Unable to connect to the server.";
        }
        return response;
    }

    String post(String url, String payload)
    {
        if (!this->isConnectedToWifi() && !this->connectToWifi())
        {
            return "Failed to conenct to WiFi.";
        }

        WiFiClientSecure client;
        client.setInsecure(); // Bypass certificate

        HTTPClient http;
        String response = "";

        if (http.begin(client, url))
        {

            int httpCode = http.POST(payload);

            if (httpCode > 0)
            {
                response = http.getString();
                http.end();
                return response;
            }
            else
            {
                return "POST Request Failed, error: " + http.errorToString(httpCode);
            }
            http.end();
        }

        else
        {
            return "Unable to connect to the server.";
        }

        return response;
    }

    String put(String url, String payload, const char *headerKeys[], const char *headerValues[], int headerSize)
    {
        if (!this->isConnectedToWifi() && !this->connectToWifi())
        {
            return "Failed to conenct to WiFi.";
        }

        WiFiClientSecure client;
        client.setInsecure(); // Bypass certificate

        HTTPClient http;
        String response = "";

        http.collectHeaders(headerKeys, headerSize);

        if (http.begin(client, url))
        {

            for (int i = 0; i < headerSize; i++)
            {
                http.addHeader(headerKeys[i], headerValues[i]);
            }

            int httpCode = http.PUT(payload);

            if (httpCode > 0)
            {
                response = http.getString();
                http.end();
                return response;
            }
            else
            {
                return "PUT Request Failed, error: " + http.errorToString(httpCode);
            }
            http.end();
        }

        else
        {
            return "Unable to connect to the server.";
        }

        return response;
    }

    String put(String url, String payload)
    {
        if (!this->isConnectedToWifi() && !this->connectToWifi())
        {
            return "Failed to conenct to WiFi.";
        }

        WiFiClientSecure client;
        client.setInsecure(); // Bypass certificate

        HTTPClient http;
        String response = "";

        if (http.begin(client, url))
        {
            int httpCode = http.PUT(payload);

            if (httpCode > 0)
            {
                response = http.getString();
                http.end();
                return response;
            }
            else
            {
                return "PUT Request Failed, error: " + http.errorToString(httpCode);
            }
            http.end();
        }

        else
        {
            return "Unable to connect to the server.";
        }

        return response;
    }
};