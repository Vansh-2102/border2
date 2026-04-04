import cv2
import numpy as np
from config import ZONES


class Visualizer:
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def draw_zones(self, frame) -> np.ndarray:
        overlay = frame.copy()
        h, w = frame.shape[:2]
        for zid, z in ZONES.items():
            x1 = int(z["x_start"] * w)
            x2 = int(z["x_end"] * w)
            cv2.rectangle(overlay, (x1, 0), (x2, h), z["color_bgr"], -1)
            cv2.putText(overlay, z["name"], (x1 + 8, 28), self.font, 0.55, z["color_bgr"], 2)
        frame = cv2.addWeighted(overlay, 0.08, frame, 0.92, 0)
        cv2.line(frame, (int(w * 0.333), 0), (int(w * 0.333), h), (255, 255, 255), 2)
        cv2.line(frame, (int(w * 0.666), 0), (int(w * 0.666), h), (255, 255, 255), 2)
        return frame

    def draw_detection(self, frame, det) -> np.ndarray:
        x1, y1, x2, y2 = det["bbox"]
        colors = {"HIGH": (0, 0, 255), "SUSPICIOUS": (0, 165, 255), "NORMAL": (0, 200, 0)}
        c = colors.get(det.get("threat_level", "NORMAL"), (200, 200, 200))
        th = 3 if det.get("threat_level") == "HIGH" else 2
        cv2.rectangle(frame, (x1, y1), (x2, y2), c, th)
        lbl = f"{det.get('class_name', '?')}#{det.get('track_id', 0)} {det.get('behavior_score', 0):.2f}"
        (tw, tsh), _ = cv2.getTextSize(lbl, self.font, 0.52, 1)
        cv2.rectangle(frame, (x1, y1 - tsh - 8), (x1 + tw + 4, y1), c, -1)
        cv2.putText(frame, lbl, (x1 + 2, y1 - 4), self.font, 0.52, (255, 255, 255), 1)
        cv2.putText(frame, det.get("threat_level", ""), (x1, y2 + 16), self.font, 0.48, c, 2)
        for i, b in enumerate(det.get("behaviors", [])[:3]):
            cv2.putText(frame, b, (x1, y2 + 30 + i * 15), self.font, 0.37, c, 1)
        traj = det.get("trajectory", [])
        if len(traj) >= 2:
            for i in range(1, len(traj)):
                a = i / len(traj)
                cv2.line(
                    frame,
                    (int(traj[i - 1][0]), int(traj[i - 1][1])),
                    (int(traj[i][0]), int(traj[i][1])),
                    tuple(int(v * a) for v in c),
                    1,
                )
        return frame

    def draw_stats_overlay(self, frame, stats, fps) -> np.ndarray:
        h, w = frame.shape[:2]
        lines = [
            f"FPS:{fps}",
            f"HIGH:{stats.get('HIGH', 0)}",
            f"SUSP:{stats.get('SUSPICIOUS', 0)}",
            f"NORM:{stats.get('NORMAL', 0)}",
        ]
        for i, l in enumerate(lines):
            cv2.putText(frame, l, (w - 130, 22 + i * 18), self.font, 0.50, (255, 255, 255), 1)
        return frame

    def draw_all(self, frame, result, fps=0) -> np.ndarray:
        frame = self.draw_zones(frame)
        for d in result.get("detections", []):
            frame = self.draw_detection(frame, d)
        return self.draw_stats_overlay(frame, result.get("threat_counts", {}), fps)
