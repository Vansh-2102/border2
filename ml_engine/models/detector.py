from pathlib import Path

from ultralytics import YOLO

from config import (
    BASE_MODEL_PATH,
    CLASS_NAMES,
    CONFIDENCE_THRESHOLD,
    IOU_THRESHOLD,
    TARGET_CLASSES,
    TRAINED_MODEL_PATH,
    USE_TRAINED_MODEL,
)


class ObjectDetector:
    def __init__(self):
        trained_model_exists = Path(TRAINED_MODEL_PATH).exists()
        if USE_TRAINED_MODEL and trained_model_exists:
            self.model_source = TRAINED_MODEL_PATH
        else:
            self.model_source = BASE_MODEL_PATH
        self.model = YOLO(self.model_source)
        self.frames_processed = 0
        print(f"Loaded model: {self.model_source}")

    def detect(self, frame) -> list[dict]:
        try:
            frame_h, frame_w = frame.shape[:2]
            results = self.model(
                frame,
                conf=CONFIDENCE_THRESHOLD,
                iou=IOU_THRESHOLD,
                classes=TARGET_CLASSES,
                verbose=False,
            )
            detections = []
            for result in results:
                boxes = getattr(result, "boxes", None)
                if boxes is None:
                    continue
                for box in boxes:
                    x1, y1, x2, y2 = [int(value) for value in box.xyxy[0].tolist()]
                    cx = float((x1 + x2) / 2.0)
                    cy = float((y1 + y2) / 2.0)
                    class_id = int(box.cls[0].item())
                    detections.append(
                        {
                            "bbox": [x1, y1, x2, y2],
                            "cx": cx,
                            "cy": cy,
                            "cx_norm": cx / float(frame_w),
                            "cy_norm": cy / float(frame_h),
                            "confidence": round(float(box.conf[0].item()), 3),
                            "class_id": class_id,
                            "class_name": CLASS_NAMES.get(class_id, str(class_id)),
                            "track_id": None,
                            "zone_id": None,
                            "zone_name": None,
                            "behaviors": [],
                            "behavior_score": 0.0,
                            "threat_level": "NORMAL",
                            "trajectory": [],
                        }
                    )
            self.frames_processed += 1
            return detections
        except Exception:
            return []

    def get_model_info(self) -> dict:
        return {
            "model_source": self.model_source,
            "frames_processed": self.frames_processed,
            "class_names": CLASS_NAMES,
        }
