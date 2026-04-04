from models.behavior import BehaviorAnalyzer
from models.classifier import ThreatClassifier
from models.detector import ObjectDetector
from models.night_vision import NightVisionEnhancer
from models.tracker import MultiObjectTracker
from utils.zone_utils import assign_zone


class MLEnsemble:
    def __init__(self):
        print("[MLEnsemble] Loading...")
        self.detector = ObjectDetector()
        self.tracker = MultiObjectTracker()
        self.behavior = BehaviorAnalyzer()
        self.classifier = ThreatClassifier()
        self.night = NightVisionEnhancer()
        self.frame_num = 0
        print("[MLEnsemble] Ready.")

    def process_frame(self, frame) -> dict:
        self.frame_num += 1
        fh, fw = frame.shape[:2]
        enhanced, was_enhanced = self.night.enhance(frame)
        detections = self.detector.detect(enhanced)
        detections = self.tracker.update(detections, self.frame_num)
        for det in detections:
            zone = assign_zone(det["bbox"], fw, fh)
            det["zone_id"] = zone["id"]
            det["zone_name"] = zone["name"]

        alerts = []
        for det in detections:
            if not det["zone_id"]:
                continue
            behavior_result = self.behavior.analyze(det, self.tracker, (fh, fw))
            threat_result = self.classifier.classify(det, behavior_result)
            det.update(
                {
                    "behaviors": behavior_result["behaviors"],
                    "behavior_score": behavior_result["behavior_score"],
                    "threat_level": threat_result["threat_level"],
                    "threat_score": threat_result["threat_score"],
                    "reasons": threat_result["reasons"],
                    "alert_priority": threat_result["alert_priority"],
                    "trajectory": self.tracker.get_trajectory(det["track_id"]),
                    "speed": behavior_result["speed"],
                    "dwell_frames": behavior_result["dwell_frames"],
                }
            )
            tid = det["track_id"]
            zid = det["zone_id"]
            if det["threat_level"] != "NORMAL" and self.tracker.can_alert(tid, zid):
                self.tracker.record_alert(tid, zid)
                alerts.append(
                    {
                        "track_id": tid,
                        "class_name": det["class_name"],
                        "zone_id": zid,
                        "zone_name": det["zone_name"],
                        "threat_level": det["threat_level"],
                        "behaviors": det["behaviors"],
                        "score": det["behavior_score"],
                        "priority": det["alert_priority"],
                        "bbox": det["bbox"],
                        "confidence": det["confidence"],
                    }
                )

        zone_counts = {zone_id: sum(1 for det in detections if det["zone_id"] == zone_id) for zone_id in ["ZONE_1", "ZONE_2", "ZONE_3"]}
        threat_counts = {
            threat_level: sum(1 for det in detections if det["threat_level"] == threat_level)
            for threat_level in ["HIGH", "SUSPICIOUS", "NORMAL"]
        }
        return {
            "frame_number": self.frame_num,
            "was_enhanced": was_enhanced,
            "detections": detections,
            "alerts": alerts,
            "zone_counts": zone_counts,
            "threat_counts": threat_counts,
        }

    def get_all_stats(self) -> dict:
        return {
            "detector": self.detector.get_model_info(),
            "night": self.night.get_stats(),
            "classifier": self.classifier.get_stats(),
            "active_tracks": len(self.tracker.prev_bboxes),
            "frames": self.frame_num,
        }
