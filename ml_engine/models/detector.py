from pathlib import Path
from ultralytics import YOLO
from config import (
    BASE_MODEL_PATH,
    CLASS_NAMES,
    CONFIDENCE_THRESHOLD,
    IOU_THRESHOLD,
    TARGET_CLASSES,
    WEAPON_MODEL_PATH,
    THERMAL_MODEL_PATH,
    USE_CUSTOM_MODELS,
    WEAPON_CLASSES,
    THERMAL_CLASSES
)

class ObjectDetector:
    def __init__(self, mode="standard"):
        self.mode = mode
        self.load_model(mode)
        self.frames_processed = 0

    def load_model(self, mode):
        if mode == "thermal" and Path(THERMAL_MODEL_PATH).exists():
            self.model_source = THERMAL_MODEL_PATH
            self.active_classes = None # Use all classes in custom model
            self.class_map = THERMAL_CLASSES
        elif mode == "weapon" and Path(WEAPON_MODEL_PATH).exists():
            self.model_source = WEAPON_MODEL_PATH
            self.active_classes = None
            self.class_map = WEAPON_CLASSES
        else:
            self.model_source = BASE_MODEL_PATH
            self.active_classes = TARGET_CLASSES
            self.class_map = CLASS_NAMES
            
        self.model = YOLO(self.model_source)
        print(f"Loaded {mode} model: {self.model_source}")

    def detect(self, frame) -> list[dict]:
        try:
            frame_h, frame_w = frame.shape[:2]
            # Use specific classes only for standard model
            kwargs = {"classes": self.active_classes} if self.active_classes else {}
            
            results = self.model(
                frame,
                conf=CONFIDENCE_THRESHOLD,
                iou=IOU_THRESHOLD,
                verbose=False,
                **kwargs
            )
            detections = []
            for result in results:
                boxes = getattr(result, "boxes", None)
                if boxes is None: continue
                for box in boxes:
                    x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                    cx, cy = float((x1 + x2) / 2.0), float((y1 + y2) / 2.0)
                    class_id = int(box.cls[0].item())
                    detections.append({
                        "bbox": [x1, y1, x2, y2],
                        "cx": cx, "cy": cy,
                        "cx_norm": cx / float(frame_w),
                        "cy_norm": cy / float(frame_h),
                        "confidence": round(float(box.conf[0].item()), 3),
                        "class_id": class_id,
                        "class_name": self.class_map.get(class_id, str(class_id)),
                        "track_id": None, "zone_id": None, "zone_name": None,
                        "behaviors": [], "behavior_score": 0.0,
                        "threat_level": "NORMAL", "trajectory": [],
                    })
            self.frames_processed += 1
            return detections
        except Exception: return []

    def get_model_info(self) -> dict:
        return {
            "model_source": self.model_source,
            "frames_processed": self.frames_processed,
            "class_names": CLASS_NAMES,
        }
