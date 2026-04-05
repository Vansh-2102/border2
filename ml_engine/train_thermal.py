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

    # Load the base model (you can also use the trained weapon model as a starting point)
    # model = YOLO('runs/train/weapon_detection_rtx4050/weights/best.pt')
    model = YOLO('yolov8n.pt') 
    
    # Path to the thermal data.yaml
    data_path = os.path.abspath('thermal_data_new/data.yaml')
    
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Please run 'prepare_thermal_data.py' first.")
        return

    print(f"Starting Infrared/Thermal training using data from: {data_path}")
    print("Epoch status will be shown below...")

    # Train the model
    model.train(
        data=data_path,
        epochs=50,
        imgsz=640,
        batch=16,
        project='runs/train',
        name='thermal_detection_rtx4050',
        device=device,
        verbose=True,
        plots=True,
        exist_ok=True,
        save=True
    )
    
    print("\nInfrared/Thermal training completed successfully.")

if __name__ == "__main__":
    train()
