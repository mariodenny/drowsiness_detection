// main.cpp
#include <Arduino.h>
#include "camera_handler.h"
#include "tflite_model.h"
#include "wifi_client.h"

TFLiteModel ml_model;
WiFiClient wifi_client;

void setup() {
  Serial.begin(115200);
  setup_camera();
  ml_model.setup();
  wifi_client.connect();
}

void loop() {
  camera_fb_t* frame = capture_frame();
  if (!frame) return;
  
  float confidence;
  int prediction = ml_model.predict(frame->buf, confidence);
  
  process_prediction(prediction, confidence);
  release_frame(frame);
  
  delay(100); // 10 FPS
}