import cv2
import numpy as np
import os
import datetime
from config import *


def open_camera(source=CAMERA_SOURCE):
    cap = cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    if not cap.isOpened():
        print(f"[WARN] Cannot open {source}")
    return cap


def read_frame(cap):
    ret, frame = cap.read()
    if not ret or frame is None:
        return np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8), False
    return frame, True


def should_process(n):
    return n % FRAME_SKIP == 0


def compute_brightness(frame):
    return float(np.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)))


def save_snapshot(frame, det, suffix=""):
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    lvl = det.get("threat_level", "UNK")
    zid = det.get("zone_id", "UNK")
    tid = det.get("track_id", 0)
    fname = f"{lvl}_{zid}_track{tid}_{ts}.jpg"
    path = os.path.join(SNAPSHOT_DIR, fname)
    fc = frame.copy()
    x1, y1, x2, y2 = det["bbox"]
    c = (0, 0, 255) if lvl == "HIGH" else (0, 165, 255)
    cv2.rectangle(fc, (x1, y1), (x2, y2), c, 3)
    cv2.imwrite(path, fc)
    return path
