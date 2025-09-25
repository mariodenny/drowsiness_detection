#include "camera_handler.h"
#include "tflite_model.h"
#include "wifi_client.h"

TFLiteModel mlModel;
AlertClient wifiClient;

// GANTI DENGAN KREDENSIAL WIFI ANDA
const char* ssid = "Ternak Lele Camon";
const char* password = "AnimuS1903";

  // GANTI DENGAN ALAMAT IP KOMPUTER/LAPTOP ANDA
  const char* serverUrl = "http://10.108.72.125:5000"; 

unsigned long lastAlertTime = 0;
const unsigned long ALERT_COOLDOWN = 10000; // 10 detik

void setup() {
  Serial.begin(115200);
  Serial.println("🚗 Drowsiness Detection System Starting...");
  
  if (!setupCamera()) {
    Serial.println("❌ Camera initialization failed!");
    while(1) delay(1000);
  }
  Serial.println("✅ Camera initialized");
  
  if (!mlModel.setup()) {
    Serial.println("❌ ML model initialization failed!");
    while(1) delay(1000);
  }
  Serial.println("✅ ML model loaded");
  
  if (!wifiClient.connect(ssid, password)) {
    Serial.println("❌ WiFi connection failed!");
  } else {
    Serial.println("✅ WiFi connected");
  }
  
  // pinMode(12, OUTPUT); // Buzzer
  // pinMode(13, OUTPUT); // LED
  
  Serial.println("✅ System ready!");
}

void loop() {
  camera_fb_t* frame = captureFrame();
  if (!frame) {
    Serial.println("❌ Frame capture failed");
    return;
  }
  
  float confidence;
  int prediction = mlModel.predict(frame->buf, frame->width, frame->height, confidence);
  
  processPrediction(prediction, confidence);
  releaseFrame(frame);
  
  delay(100);
}

void processPrediction(int prediction, float confidence) {
  String states[] = {"AWAKE", "DROWSY", "YAWNING"};
  
  if (prediction == -1) {
    return; // Prediction failed
  }
  
  Serial.printf("Status: %s, Confidence: %.2f\n", states[prediction].c_str(), confidence);
  
  if (confidence < 0.6) {
    Serial.println("Low confidence, skipping...");
    return;
  }
  
  unsigned long currentTime = millis();
  if (currentTime - lastAlertTime < ALERT_COOLDOWN) {
    return; // Cooldown period
  }
  
  switch(prediction) {
    case 0: // AWAKE
      digitalWrite(13, LOW);
      break;
      
    case 1: // DROWSY
      if (confidence > 0.8) {
        triggerAlarm();
        sendAlert("DROWSY", confidence);
        lastAlertTime = currentTime;
      }
      break;
      
    case 2: // YAWNING  
      if (confidence > 0.7) {
        sendAlert("YAWNING", confidence);
        lastAlertTime = currentTime;
      }
      break;
  }
}

void triggerAlarm() {
  Serial.println("🚨 ALERT: Drowsy driver detected!");
  
  for (int i = 0; i < 3; i++) {
    digitalWrite(12, HIGH);
    digitalWrite(13, HIGH);
    delay(200);
    digitalWrite(12, LOW);
    digitalWrite(13, LOW);
    delay(200);
  }
}

void sendAlert(String status, float confidence) {
  if (WiFi.status() == WL_CONNECTED) {
    wifiClient.sendAlert(serverUrl, status, confidence);
  } else {
    Serial.println("WiFi not connected, alert not sent");
  }
}