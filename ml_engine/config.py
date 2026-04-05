CAMERA_SOURCE = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FRAME_SKIP = 2
ZONES = {
    "ZONE_1": {
        "id": "ZONE_1",
        "name": "GREEN ZONE (TOP)",
        "x_start": 0.0,
        "x_end": 1.0,
        "y_start": 0.0,
        "y_end": 0.333,
        "color_bgr": (0, 200, 0),
        "threat_multiplier": 1.0,
        "alert_threshold": 0.65,
        "cooldown_sec": 30,
        "monitored_classes": ["person"],
    },
    "ZONE_2": {
        "id": "ZONE_2",
        "name": "YELLOW ZONE (MID)",
        "x_start": 0.0,
        "x_end": 1.0,
        "y_start": 0.333,
        "y_end": 0.666,
        "color_bgr": (0, 200, 255),
        "threat_multiplier": 1.5,
        "alert_threshold": 0.40,
        "cooldown_sec": 15,
        "monitored_classes": ["person", "motorcycle", "bicycle", "car"],
    },
    "ZONE_3": {
        "id": "ZONE_3",
        "name": "RED ZONE (BTM)",
        "x_start": 0.0,
        "x_end": 1.0,
        "y_start": 0.666,
        "y_end": 1.0,
        "color_bgr": (0, 0, 255),
        "threat_multiplier": 2.5,
        "alert_threshold": 0.15,
        "cooldown_sec": 5,
        "monitored_classes": ["person", "motorcycle", "bicycle", "car", "truck", "bus", "dog", "cat"],
    },
}
BASE_MODEL_PATH = "weights/base/yolov8n.pt"
WEAPON_MODEL_PATH = "weights/trained/weapon_model.pt"
THERMAL_MODEL_PATH = "weights/trained/thermal_model.pt"
USE_CUSTOM_MODELS = True
CONFIDENCE_THRESHOLD = 0.45
IOU_THRESHOLD = 0.50

# Class Mappings for Custom Models
WEAPON_CLASSES = {0: "Grenade", 1: "Knife", 2: "Missile", 3: "Pistol", 4: "Rifle"}
THERMAL_CLASSES = {0: "person"}

# Standard COCO classes for fallback/standard mode
TARGET_CLASSES = [0, 1, 2, 3, 5, 7, 15, 16] 
CLASS_NAMES = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
    15: "cat",
    16: "dog",
}
# Night Vision & Thermal Settings
NIGHT_BRIGHTNESS_THRESHOLD = 50
INFRARED_MODE = True
THERMAL_COLORMAP = 10 # cv2.COLORMAP_INFERNO
IOU_MATCH_THRESHOLD = 0.25
MAX_LOST_FRAMES = 30
HISTORY_MAXLEN = 90
LOITER_FRAMES = 45
LOITER_SPEED_PX = 2.5
NIGHT_HOUR_START = 20
NIGHT_HOUR_END = 6
SPEED_THRESHOLD_PX = 12.0
ERRATIC_MIN_CHANGES = 3
NIGHT_BRIGHTNESS_THRESHOLD = 50
CLAHE_CLIP_LIMIT = 3.0
CLAHE_TILE_GRID = (8, 8)
GAMMA_VALUE = 1.8
EPOCHS = 60
BATCH_SIZE = 8
IMG_SIZE = 640
FRAME_EXTRACT_EVERY = 15
TRAIN_VAL_SPLIT = 0.8
DATASET_YAML = "training/dataset.yaml"
TRAIN_PROJECT = "weights/trained"
TRAIN_NAME = "border_surveillance"
SNAPSHOT_DIR = "data/snapshots"
REPORTS_DIR = "data/reports"
RAW_VIDEO_DIR = "data/raw_videos"
TRAIN_IMG_DIR = "data/images/train"
VAL_IMG_DIR = "data/images/val"
TRAIN_LBL_DIR = "data/labels/train"
VAL_LBL_DIR = "data/labels/val"
