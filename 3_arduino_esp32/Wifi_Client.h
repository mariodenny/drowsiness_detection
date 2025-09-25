// 3_arduino_esp32/wifi_client.h
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

class WiFiClient {
public:
    bool connect(const char* ssid, const char* password) {
        WiFi.begin(ssid, password);
        Serial.print("Connecting to WiFi");
        
        int attempts = 0;
        while (WiFi.status() != WL_CONNECTED && attempts < 20) {
            delay(500);
            Serial.print(".");
            attempts++;
        }
        
        if (WiFi.status() == WL_CONNECTED) {
            Serial.println("\n✅ WiFi connected");
            Serial.print("IP address: ");
            Serial.println(WiFi.localIP());
            return true;
        } else {
            Serial.println("\n❌ WiFi connection failed");
            return false;
        }
    }
    
    bool sendAlert(const char* serverUrl, const String& status, float confidence) {
        if (WiFi.status() != WL_CONNECTED) {
            return false;
        }
        
        HTTPClient http;
        String url = String(serverUrl) + "/api/alert";
        http.begin(url);
        http.addHeader("Content-Type", "application/json");
        
        DynamicJsonDocument doc(256);
        doc["device_id"] = WiFi.macAddress();
        doc["status"] = status;
        doc["confidence"] = confidence;
        
        String payload;
        serializeJson(doc, payload);
        
        Serial.println("Sending alert: " + payload);
        
        int httpCode = http.POST(payload);
        
        if (httpCode > 0) {
            if (httpCode == HTTP_CODE_OK) {
                Serial.println("✅ Alert sent successfully");
            } else {
                Serial.printf("❌ Failed to send alert, HTTP code: %d\n", httpCode);
            }
        } else {
            Serial.printf("❌ HTTP POST failed, error: %s\n", http.errorToString(httpCode).c_str());
        }

        http.end();
        return httpCode == HTTP_CODE_OK;
    }
};