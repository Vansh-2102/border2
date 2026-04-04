class PostProcessor:
    def format_for_api(self, result) -> dict:
        return {
            "type": "detections",
            "frame_number": result.get("frame_number"),
            "fps": result.get("fps", 0),
            "was_enhanced": result.get("was_enhanced", False),
            "zone_counts": result.get("zone_counts", {}),
            "threat_counts": result.get("threat_counts", {}),
            "detections": [self._fmt(d) for d in result.get("detections", [])],
            "alerts": result.get("alerts", []),
        }

    def _fmt(self, det) -> dict:
        return {
            "track_id": det["track_id"],
            "class_name": det["class_name"],
            "confidence": det["confidence"],
            "bbox": det["bbox"],
            "zone_id": det["zone_id"],
            "zone_name": det["zone_name"],
            "threat_level": det["threat_level"],
            "behaviors": det["behaviors"],
            "behavior_score": det["behavior_score"],
            "speed": det.get("speed", 0),
            "trajectory": det.get("trajectory", [])[-10:],
            "reasons": det.get("reasons", []),
        }

    def format_alert(self, alert) -> dict:
        msg = (
            f"[{alert['threat_level']}] {alert['class_name']} "
            f"in {alert['zone_name']}. "
            f"Behaviors: {', '.join(alert['behaviors'])}"
        )
        return {**alert, "message": msg}
