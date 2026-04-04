import cv2
import os
import sys
import yaml
import random
import numpy as np
from ultralytics import YOLO
from config import *

# Create all dirs
for d in [TRAIN_IMG_DIR, VAL_IMG_DIR, TRAIN_LBL_DIR, VAL_LBL_DIR, RAW_VIDEO_DIR]:
    os.makedirs(d, exist_ok=True)

# Load model
model = YOLO(BASE_MODEL_PATH)

# Find videos
videos = [f for f in os.listdir(RAW_VIDEO_DIR) if f.endswith(".mp4")]
if not videos:
    print("Add .mp4 files to data/raw_videos/ then retry.")
    sys.exit(0)

frame_list = []
print(f"Extracting frames from {len(videos)} videos...")

for vid_name in videos:
    cap = cv2.VideoCapture(os.path.join(RAW_VIDEO_DIR, vid_name))
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if count % FRAME_EXTRACT_EVERY == 0:
            frame = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
            frame_list.append(frame)
        count += 1
    cap.release()

print(f"Extracted {len(frame_list)} frames. Auto-labeling...")

labeled_frames = []
for frame in frame_list:
    results = model(frame, conf=0.30, verbose=False, classes=TARGET_CLASSES)
    labels = []
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            # YOLO format: cls cx cy w h (normalized)
            xywhn = box.xywhn[0].tolist()
            labels.append(f"{cls} {' '.join(map(str, xywhn))}")
    
    if labels:
        labeled_frames.append((frame, labels))

print(f"Labeled {len(labeled_frames)} frames. Augmenting...")

# Augment
final_labeled_frames = []
for frame, labels in labeled_frames:
    final_labeled_frames.append((frame, labels))
    # Brighten
    bright = cv2.convertScaleAbs(frame, alpha=1.3, beta=20)
    final_labeled_frames.append((bright, labels))
    # Darken
    dark = cv2.convertScaleAbs(frame, alpha=0.4, beta=-30)
    final_labeled_frames.append((dark, labels))

random.shuffle(final_labeled_frames)
split = int(len(final_labeled_frames) * TRAIN_VAL_SPLIT)
train_set = final_labeled_frames[:split]
val_set = final_labeled_frames[split:]

def save_set(dataset, img_dir, lbl_dir):
    for i, (frame, labels) in enumerate(dataset):
        img_path = os.path.join(img_dir, f"frame_{i}.jpg")
        lbl_path = os.path.join(lbl_dir, f"frame_{i}.txt")
        cv2.imwrite(img_path, frame)
        with open(lbl_path, "w") as f:
            f.write("\n".join(labels))

print("Saving train set...")
save_set(train_set, TRAIN_IMG_DIR, TRAIN_LBL_DIR)
print("Saving val set...")
save_set(val_set, VAL_IMG_DIR, VAL_LBL_DIR)

# Write dataset.yaml
data = {
    "path": os.path.abspath("data"),
    "train": "images/train",
    "val": "images/val",
    "nc": len(CLASS_NAMES),
    "names": [CLASS_NAMES[k] for k in sorted(CLASS_NAMES.keys())]
}
with open(DATASET_YAML, "w") as f:
    yaml.dump(data, f)

print(f"\nSummary:")
print(f"Extracted: {len(frame_list)}")
print(f"Labeled:   {len(labeled_frames)}")
print(f"Augmented: {len(final_labeled_frames)}")
print(f"Train:     {len(train_set)}")
print(f"Val:       {len(val_set)}")
