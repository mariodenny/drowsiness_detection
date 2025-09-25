# 1_download_dataset.py
import os
import urllib.request
import zipfile

def setup_directories():
    """Create the complete directory structure"""
    directories = [
        '1_datasets/raw',
        '1_datasets/processed/train/awake',
        '1_datasets/processed/train/drowsy', 
        '1_datasets/processed/train/yawning',
        '1_datasets/processed/test/awake',
        '1_datasets/processed/test/drowsy',
        '1_datasets/processed/test/yawning',
        '2_training/models',
        '2_training/utils',
        '3_arduino_esp32/generated',
        '3_arduino_esp32/libraries',
        '4_flask_backend/data',
        '4_flask_backend/templates',
        '4_flask_backend/static/css',
        '4_flask_backend/static/js',
        '4_flask_backend/static/images',
        '5_documentation/images',
        '6_testing/test_data'
    ]
    
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created: {dir_path}")

def create_readme_files():
    """Create basic README files for each directory"""
    readme_content = {
        '1_datasets/README.txt': 'Dataset for drowsiness detection project',
        '2_training/README.txt': 'Model training scripts and utilities',
        '3_arduino_esp32/README.txt': 'ESP32 Arduino code for edge device',
        '4_flask_backend/README.txt': 'Flask backend API server',
        '5_documentation/README.txt': 'Project documentation and guides',
        '6_testing/README.txt': 'Testing scripts and test cases'
    }
    
    for file_path, content in readme_content.items():
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Created: {file_path}")

if __name__ == '__main__':
    print("Setting up project directory structure...")
    setup_directories()
    create_readme_files()
    print("✅ Project structure created successfully!")