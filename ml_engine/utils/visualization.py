import cv2
import numpy as np
from config import ZONES


class Visualizer:
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def draw_zones(self, frame) -> np.ndarray:
        overlay = frame.copy()
        h, w = frame.shape[:2]
        
        # We define full-width horizontal zones to cover the entire camera feed
        # ZONE_1 (FAR): Top part
        z1_pts = np.array([
            [0, 0], 
            [w, 0],
            [w, int(h * 0.33)],
            [0, int(h * 0.33)]
        ], np.int32)
        
        # ZONE_2 (MID): Middle part
        z2_pts = np.array([
            [0, int(h * 0.33)],
            [w, int(h * 0.33)],
            [w, int(h * 0.66)],
            [0, int(h * 0.66)]
        ], np.int32)
        
        # ZONE_3 (CLOSE): Bottom part
        z3_pts = np.array([
            [0, int(h * 0.66)],
            [w, int(h * 0.66)],
            [w, h],
            [0, h]
        ], np.int32)
        
        zone_polys = {
            "ZONE_1": z1_pts,
            "ZONE_2": z2_pts,
            "ZONE_3": z3_pts
        }
        
        for zid, pts in zone_polys.items():
            z = ZONES[zid]
            cv2.fillPoly(overlay, [pts], z["color_bgr"])
            
            # Label at the left side of the zone
            label_x = 20
            label_y = pts[0][1] + 30
            z_range = f" ({z['z_start']}-{z['z_end']}m)"
            cv2.putText(overlay, z["name"] + z_range, (label_x, label_y), self.font, 0.6, (255, 255, 255), 2)
        
        frame = cv2.addWeighted(overlay, 0.12, frame, 0.88, 0)
        
        # Draw explicit horizontal grid lines to separate the three stacked zones
        cv2.line(frame, (0, int(h * 0.33)), (w, int(h * 0.33)), (255, 255, 255), 1)
        cv2.line(frame, (0, int(h * 0.66)), (w, int(h * 0.66)), (255, 255, 255), 1)
            
        return frame

    def draw_detection(self, frame, det) -> np.ndarray:
        x1, y1, x2, y2 = det["bbox"]
        colors = {"HIGH": (0, 0, 255), "SUSPICIOUS": (0, 165, 255), "NORMAL": (0, 200, 0)}
        c = colors.get(det.get("threat_level", "NORMAL"), (200, 200, 200))
        th = 3 if det.get("threat_level") == "HIGH" else 2
        cv2.rectangle(frame, (x1, y1), (x2, y2), c, th)
        
        dist_str = f" {det.get('distance', 0):.1f}m" if "distance" in det else ""
        lbl = f"{det.get('class_name', '?')}#{det.get('track_id', 0)}{dist_str}"
        
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
                    2,
                )
        return frame

    def draw_alerts_list(self, frame, active_alerts) -> np.ndarray:
        h, w = frame.shape[:2]
        # Draw top-left alert notifications
        for i, alert_data in enumerate(active_alerts[:5]):
            alert = alert_data["alert"]
            msg = f"ALERT: {alert['threat_level']} - {alert['class_name']} in {alert['zone_name']}"
            color = (0, 0, 255) if alert["threat_level"] == "HIGH" else (0, 165, 255)
            
            # Draw semi-transparent background for alert
            (tw, th), _ = cv2.getTextSize(msg, self.font, 0.6, 2)
            cv2.rectangle(frame, (10, 40 + i * 35), (10 + tw + 10, 40 + i * 35 + th + 10), (0, 0, 0), -1)
            cv2.putText(frame, msg, (15, 60 + i * 35), self.font, 0.6, color, 2)
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

    def draw_3d_view(self, frame, detections) -> np.ndarray:
        h, w = frame.shape[:2]
        # Top-down radar view size
        view_w, view_h = 250, 250
        view_x, view_y = w - view_w - 10, h - view_h - 10
        
        # Radar center and scale
        # Assume we show 10m x 10m area
        max_dist = 10.0
        scale = view_w / max_dist
        
        # Background
        cv2.rectangle(frame, (view_x, view_y), (view_x + view_w, view_y + view_h), (20, 20, 20), -1)
        cv2.rectangle(frame, (view_x, view_y), (view_x + view_w, view_y + view_h), (100, 100, 100), 1)
        cv2.putText(frame, "REAL-WORLD MAP (METERS)", (view_x + 5, view_y + 15), self.font, 0.4, (255, 255, 255), 1)
        
        # Draw Distance Circles
        for r in [2, 5, 8]:
            radius = int(r * scale)
            cv2.circle(frame, (view_x + view_w // 2, view_y + view_h), radius, (50, 50, 50), 1)
            cv2.putText(frame, f"{r}m", (view_x + view_w // 2 + radius, view_y + view_h), self.font, 0.3, (100, 100, 100), 1)

        # Draw zones in the 3D radar view
        for zid, z in ZONES.items():
            z1, z2 = z.get("z_start", 0), z.get("z_end", 100)
            y1 = view_y + view_h - int((z1 / max_dist) * view_h)
            y2 = view_y + view_h - int((z2 / max_dist) * view_h)
            y1, y2 = max(view_y, min(view_y + view_h, y1)), max(view_y, min(view_y + view_h, y2))
            
            overlay = frame.copy()
            cv2.rectangle(overlay, (view_x, y2), (view_x + view_w, y1), z["color_bgr"], -1)
            frame = cv2.addWeighted(overlay, 0.15, frame, 0.85, 0)
            
        # Draw camera position (origin)
        cv2.circle(frame, (view_x + view_w // 2, view_y + view_h), 6, (0, 255, 255), -1)
        
        # Draw detections in 3D radar view using world_pos
        for det in detections:
            world_pos = det.get("world_pos", (0, 0))
            wx, wy = world_pos # X is horizontal distance from center, Y is depth
            
            # Map world X, Y to radar view pixels
            # Radar center-bottom is (0,0) in world
            dx = view_x + view_w // 2 + int(wx * scale)
            dy = view_y + view_h - int(wy * scale)
            
            if view_x < dx < view_x + view_w and view_y < dy < view_y + view_h:
                colors = {"HIGH": (0, 0, 255), "SUSPICIOUS": (0, 165, 255), "NORMAL": (0, 200, 0)}
                c = colors.get(det.get("threat_level", "NORMAL"), (200, 200, 200))
                cv2.circle(frame, (dx, dy), 5, c, -1)
                cv2.putText(frame, f"ID:{det.get('track_id', '')}", (dx + 7, dy), self.font, 0.35, (255, 255, 255), 1)
            
        return frame

    def draw_all(self, frame, result, fps=0, active_alerts=None) -> np.ndarray:
        frame = self.draw_zones(frame)
        for d in result.get("detections", []):
            frame = self.draw_detection(frame, d)
        
        if active_alerts:
            frame = self.draw_alerts_list(frame, active_alerts)
        return self.draw_stats_overlay(frame, result.get("threat_counts", {}), fps)
