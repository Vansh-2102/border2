from models.behavior import BehaviorAnalyzer
from models.classifier import ThreatClassifier
from models.detector import ObjectDetector
from models.night_vision import NightVisionEnhancer
from models.tracker import MultiObjectTracker
from models.depth import DepthEstimator
from utils.zone_utils import assign_zone
from utils.calibration_manager import CalibrationManager
from utils.spatial_utils import GroundPlaneTransformer


from config import INFRARED_MODE, CALIBRATION_FILE

class MLEnsemble:
    def __init__(self):
        print("[MLEnsemble] Loading...")
        self.calibration = CalibrationManager(CALIBRATION_FILE)
        self.spatial = GroundPlaneTransformer()
        
        self.detector = ObjectDetector(mode="standard")
        self.weapon_detector = ObjectDetector(mode="weapon")
        self.thermal_detector = ObjectDetector(mode="thermal")
        self.depth_estimator = DepthEstimator(calibration=self.calibration)
        self.tracker = MultiObjectTracker()
        self.behavior = BehaviorAnalyzer()
        self.classifier = ThreatClassifier()
        self.night = NightVisionEnhancer()
        self.frame_num = 0
        print("[MLEnsemble] Ready.")

    def process_frame(self, frame) -> dict:
        self.frame_num += 1
        fh, fw = frame.shape[:2]
        
        # Undistort frame if calibration is loaded
        frame = self.calibration.undistort(frame)
        
        enhanced, was_enhanced = self.night.enhance(frame)
        
        # Get depth map
        depth_map = self.depth_estimator.estimate(enhanced)
        
        # Select detector based on mode
        if was_enhanced and INFRARED_MODE:
            detections = self.thermal_detector.detect(enhanced)
        else:
            # Run both standard and weapon detection in normal/enhanced-clahe mode
            detections = self.detector.detect(enhanced)
            weapon_dets = self.weapon_detector.detect(enhanced)
            detections.extend(weapon_dets)
            
        detections = self.tracker.update(detections, self.frame_num)
        
        # Cleanup distance smoothers for lost tracks
        active_ids = {det["track_id"] for det in detections if det["track_id"] is not None}
        self.depth_estimator.smoothers = {tid: sm for tid, sm in self.depth_estimator.smoothers.items() if tid in active_ids}

        for det in detections:
            # Metric Distance using Pinhole + MiDaS + Temporal Smoothing
            distance = self.depth_estimator.get_distance(
                depth_map, 
                det["bbox"], 
                enhanced.shape, 
                det["class_name"],
                track_id=det["track_id"]
            )
            det["distance"] = distance
            
            # Real-world Ground Plane coordinates (X, Y) in meters
            world_x, world_y = self.spatial.get_ground_position(det["bbox"])
            det["world_pos"] = (world_x, world_y)
            
            zone = assign_zone(det["bbox"], fw, fh, distance=distance)
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
                        "distance": det["distance"],
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
            "depth_map": depth_map,
        }

    def get_all_stats(self) -> dict:
        return {
            "detector": self.detector.get_model_info(),
            "night": self.night.get_stats(),
            "classifier": self.classifier.get_stats(),
            "depth": {"model": "MiDaS_small"},
            "active_tracks": len(self.tracker.prev_bboxes),
            "frames": self.frame_num,
        }
