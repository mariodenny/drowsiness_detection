# 2_training/1_download_dataset.py
import os
from PIL import Image, ImageDraw

def create_sample_dataset():
    """Create sample dataset for testing"""
    print("Creating sample dataset...")
    
    # Create sample images for each class
    for class_name in ['awake', 'drowsy', 'yawning']:
        class_dir = f'1_datasets/processed/train/{class_name}'
        os.makedirs(class_dir, exist_ok=True)
        
        for i in range(100):  # 100 sample images per class
            img = Image.new('L', (96, 96), color=128)  # Grayscale
            draw = ImageDraw.Draw(img)
            
            if class_name == 'awake':
                # Open eyes
                draw.ellipse([20, 30, 40, 50], outline=255, fill=255)  # Left eye
                draw.ellipse([56, 30, 76, 50], outline=255, fill=255)  # Right eye
            elif class_name == 'drowsy':
                # Half-closed eyes
                draw.rectangle([20, 35, 40, 45], outline=255, fill=255)
                draw.rectangle([56, 35, 76, 45], outline=255, fill=255)
            else:  # yawning
                # Open mouth + eyes
                draw.ellipse([20, 30, 40, 50], outline=255, fill=255)
                draw.ellipse([56, 30, 76, 50], outline=255, fill=255)
                draw.ellipse([35, 60, 61, 70], outline=255, fill=255)
            
            img.save(f'{class_dir}/sample_{i:03d}.jpg')
    
    print("Sample dataset created!")

if __name__ == '__main__':
    create_sample_dataset()