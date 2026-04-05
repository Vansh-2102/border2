from ultralytics import YOLO
import os
import torch

def train():
    # Check if GPU is available
    if torch.cuda.is_available():
        device = 0
        print(f"CUDA is available. Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = 'cpu'
        print("CUDA is NOT available. Using CPU instead.")

    # Load the base model
    # If weights/base/yolov8n.pt doesn't exist, it will download it
    model = YOLO('yolov8n.pt') 
    
    # Path to the data.yaml
    data_path = os.path.abspath('weapon_data/data.yaml')
    
    print(f"Starting training using data from: {data_path}")
    print("Epoch status will be shown below...")

    # Train the model
    model.train(
        data=data_path,
        epochs=50,
        imgsz=640,
        batch=16,
        project='runs/train',
        name='weapon_detection_rtx4050',
        device=device,
        verbose=True,   # Ensure detailed output
        plots=True,     # Save training plots
        exist_ok=True,
        save=True       # Save weights
    )
    
    print("\nTraining completed successfully.")

if __name__ == "__main__":
    train()
