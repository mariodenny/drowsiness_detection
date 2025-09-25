# 2_training/2_train_model.py
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks
import numpy as np
import os
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator

print("TensorFlow version:", tf.__version__)

def create_drowsiness_model():
    """Create lightweight model for ESP32"""
    model = models.Sequential([
        layers.Input(shape=(96, 96, 1)),
        
        layers.Conv2D(8, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.Conv2D(16, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(32, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(3, activation='softmax')
    ])
    
    return model

def setup_data_generators():
    """Setup data generators with augmentation"""
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        shear_range=0.1,
        zoom_range=0.1,
        horizontal_flip=True,
        brightness_range=[0.9, 1.1],
        validation_split=0.2
    )
    
    train_generator = train_datagen.flow_from_directory(
        '1_datasets/processed/train/',
        target_size=(96, 96),
        color_mode='grayscale',
        batch_size=16,
        class_mode='categorical',
        subset='training',
        shuffle=True
    )
    
    val_generator = train_datagen.flow_from_directory(
        '1_datasets/processed/train/',
        target_size=(96, 96),
        color_mode='grayscale',
        batch_size=16,
        class_mode='categorical',
        subset='validation',
        shuffle=False
    )
    
    return train_generator, val_generator

def train_model():
    """Main training function"""
    model = create_drowsiness_model()
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("Model architecture:")
    model.summary()
    
    train_gen, val_gen = setup_data_generators()
    
    callbacks_list = [
        callbacks.EarlyStopping(monitor='val_accuracy', patience=10, restore_best_weights=True),
        callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=0.00001),
        callbacks.ModelCheckpoint('2_training/models/best_model.h5', monitor='val_accuracy', save_best_only=True)
    ]
    
    print("Starting training...")
    history = model.fit(
        train_gen,
        epochs=30,
        validation_data=val_gen,
        callbacks=callbacks_list,
        verbose=1
    )
    
    return model, history

def convert_to_tflite(model):
    """Convert model to TensorFlow Lite"""
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_types = [tf.float16]
    
    tflite_model = converter.convert()
    
    with open('2_training/models/drowsiness_model.tflite', 'wb') as f:
        f.write(tflite_model)
    
    print(f"TFLite model saved: {len(tflite_model)} bytes")
    output_dir = '3_arduino_esp32/generated'
    os.makedirs(output_dir, exist_ok=True)
    # Convert to C array
    with open('3_arduino_esp32/generated/drowsiness_model.h', 'w') as f:
        f.write('const unsigned char drowsiness_model[] = {')
        for i, byte in enumerate(tflite_model):
            if i % 12 == 0:
                f.write('\n  ')
            f.write(f'0x{byte:02x}')
            if i < len(tflite_model) - 1:
                f.write(', ')
        f.write('\n};\n')
        f.write(f'const int drowsiness_model_len = {len(tflite_model)};\n')
    
    print("C header file generated at: 3_arduino_esp32/generated/drowsiness_model.h")
    return tflite_model

if __name__ == '__main__':
    if not os.path.exists('1_datasets/processed/train/awake'):
        print("Dataset not found. Please run '1_download_dataset.py' first!")
        exit(1)
    
    model, history = train_model()
    tflite_model = convert_to_tflite(model)
    
    print("\n✅ Training completed!")