// tflite_model.h
#ifndef TFLITE_MODEL_H
#define TFLITE_MODEL_H

// TAMBAHKAN KEMBALI INCLUDE INI
// #include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/schema/schema_generated.h"

// Sertakan model yang sudah dibuat
#include "drowsiness_model.h"

class TFLiteModel {
private:
    const tflite::Model* model;
    tflite::MicroInterpreter* interpreter;
    TfLiteTensor* input;
    TfLiteTensor* output;
    
    const int tensorArenaSize = 80 * 1024; // 80KB
    uint8_t* tensorArena;
    // PERBAIKAN: Ubah MicroErrorReporter menjadi ErrorReporter
    tflite::ErrorReporter* errorReporter; 

public:
    bool setup() {
        // Alokasikan ErrorReporter
        static tflite::MicroErrorReporter staticErrorReporter;
        errorReporter = &staticErrorReporter;

        // Muat model
        model = tflite::GetModel(drowsiness_model);
        if (model->version() != TFLITE_SCHEMA_VERSION) {
            errorReporter->Report("Model version mismatch");
            return false;
        }
        
        // Alokasikan tensor arena
        tensorArena = (uint8_t*) malloc(tensorArenaSize);
        if (!tensorArena) {
            errorReporter->Report("Tensor arena allocation failed");
            return false;
        }
        
        // Atur operations resolver
        static tflite::MicroMutableOpResolver<8> resolver;
        resolver.AddConv2D();
        resolver.AddMaxPool2D();
        resolver.AddReshape();
        resolver.AddFullyConnected();
        resolver.AddSoftmax();
        resolver.AddDequantize();
        resolver.AddMean();
        resolver.AddQuantize();
        
        // Bangun interpreter
        static tflite::MicroInterpreter staticInterpreter(
            model, resolver, tensorArena, tensorArenaSize, errorReporter);
        
        interpreter = &staticInterpreter;
        
        // Alokasikan tensor
        if (interpreter->AllocateTensors() != kTfLiteOk) {
            errorReporter->Report("Tensor allocation failed");
            return false;
        }
        
        // Ambil tensor input dan output
        input = interpreter->input(0);
        output = interpreter->output(0);
        
        return true;
    }
    
    int predict(const uint8_t* imageData, int width, int height, float& confidence) {
        // Preprocess gambar
        for (int i = 0; i < 96 * 96; i++) {
            input->data.f[i] = imageData[i] / 255.0f;
        }
        
        // Jalankan inferensi
        if (interpreter->Invoke() != kTfLiteOk) {
            errorReporter->Report("Invoke failed");
            return -1;
        }
        
        // Ambil hasil
        float* outputData = output->data.f;
        int maxIndex = 0;
        confidence = outputData[0];
        
        for (int i = 1; i < 3; i++) {
            if (outputData[i] > confidence) {
                confidence = outputData[i];
                maxIndex = i;
            }
        }
        
        return maxIndex;
    }
};

#endif