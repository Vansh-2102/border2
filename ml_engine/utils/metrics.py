import time
import collections


class MetricsTracker:
    def __init__(self):
        self.start = time.time()
        self.frame_count = 0
        self.detection_log = []
        self.alert_log = []
        self.fps_history = collections.deque(maxlen=30)
        self.zone_totals = {z: 0 for z in ["ZONE_1", "ZONE_2", "ZONE_3"]}
        self.threat_totals = {t: 0 for t in ["HIGH", "SUSPICIOUS", "NORMAL"]}
        self.last_fps = time.time()
        self.fps_frames = 0
        self.current_fps = 0

    def update(self, result):
        self.frame_count += 1
        self.fps_frames += 1
        now = time.time()
        if now - self.last_fps >= 1.0:
            self.current_fps = self.fps_frames
            self.fps_frames = 0
            self.last_fps = now
            self.fps_history.append(self.current_fps)

        self.detection_log.append((now, len(result.get("detections", []))))
        if len(self.detection_log) > 1000:
            self.detection_log.pop(0)

        for z, c in result.get("zone_counts", {}).items():
            self.zone_totals[z] = self.zone_totals.get(z, 0) + c
        for t, c in result.get("threat_counts", {}).items():
            self.threat_totals[t] = self.threat_totals.get(t, 0) + c

        self.alert_log.extend(result.get("alerts", []))
        if len(self.alert_log) > 500:
            self.alert_log = self.alert_log[-500:]

    def get_summary(self) -> dict:
        avg = sum(self.fps_history) / len(self.fps_history) if self.fps_history else 0
        return {
            "uptime": round(time.time() - self.start, 1),
            "frames": self.frame_count,
            "fps": self.current_fps,
            "avg_fps": round(avg, 1),
            "total_detections": sum(c for _, c in self.detection_log),
            "total_alerts": len(self.alert_log),
            "zone_totals": self.zone_totals,
            "threat_totals": self.threat_totals,
            "recent_alerts": self.alert_log[-20:],
        }
