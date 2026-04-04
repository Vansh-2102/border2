import os
import sys
import shutil
from ultralytics import YOLO
from config import *

# Check prerequisites
if not os.path.exists(DATASET_YAML):
    print(f"Error: {DATASET_YAML} not found.")
    sys.exit(1)

if not os.listdir(TRAIN_IMG_DIR):
    print("Run dataset_builder.py first.")
    sys.exit(1)

# Load model
model = YOLO(BASE_MODEL_PATH)

print(f"Starting training: {TRAIN_NAME}")
print(f"Epochs: {EPOCHS}, Batch: {BATCH_SIZE}, ImgSize: {IMG_SIZE}")

# Train
model.train(
    data=os.path.abspath(DATASET_YAML),
    epochs=EPOCHS,
    batch=BATCH_SIZE,
    imgsz=IMG_SIZE,
    project=TRAIN_PROJECT,
    name=TRAIN_NAME,
    exist_ok=True,
    patience=15,
    device="cpu",
    workers=2,
    optimizer="AdamW",
    lr0=0.001,
    lrf=0.01,
    momentum=0.937,
    weight_decay=0.0005,
    warmup_epochs=3,
    hsv_h=0.015,
    hsv_s=0.7,
    hsv_v=0.5,
    degrees=0.0,
    translate=0.1,
    scale=0.5,
    flipud=0.0,
    fliplr=0.5,
    mosaic=0.8,
    mixup=0.15
)

# Copy best weights
src = f"{TRAIN_PROJECT}/{TRAIN_NAME}/weights/best.pt"
if os.path.exists(src):
    os.makedirs(os.path.dirname(TRAINED_MODEL_PATH), exist_ok=True)
    shutil.copy(src, TRAINED_MODEL_PATH)
    print(f"Done. Weights saved to {TRAINED_MODEL_PATH}")
    print("Set USE_TRAINED_MODEL=True in config.py")
else:
    print("Training failed to produce best.pt")
