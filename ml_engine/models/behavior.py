import datetime
import math

import numpy as np

from config import *


class BehaviorAnalyzer:
    behavior_weights = {
        "LOITERING": 0.40,
        "NIGHT_MOVEMENT": 0.30,
        "SPEEDING": 0.30,
        "ERRATIC_MOVEMENT": 0.25,
        "DANGER_ZONE_PRESENCE": 0.45,
        "ADVANCING_TO_DANGER": 0.35,
        "GROUP_MOVEMENT": 0.20,
    }

    def _is_night(self) -> bool:
        h = datetime.datetime.now().hour
        return h >= NIGHT_HOUR_START or h < NIGHT_HOUR_END

    def _count_direction_changes(self, traj) -> int:
        changes = 0
        for i in range(2, len(traj)):
            v1 = (traj[i - 1][0] - traj[i - 2][0], traj[i - 1][1] - traj[i - 2][1])
            v2 = (traj[i][0] - traj[i - 1][0], traj[i][1] - traj[i - 1][1])
            m1 = math.hypot(*v1) + 1e-6
            m2 = math.hypot(*v2) + 1e-6
            cos_a = max(-1, min(1, (v1[0] * v2[0] + v1[1] * v2[1]) / (m1 * m2)))
            if math.degrees(math.acos(cos_a)) > 90:
                changes += 1
        return changes

    def analyze(self, det, tracker, frame_shape) -> dict:
        tid = det["track_id"]
        cls = det["class_name"]
        zid = det["zone_id"]
        fh, fw = frame_shape
        behaviors = []
        raw = 0.0
        speed = tracker.get_speed(tid)
        dwell = tracker.get_dwell_frames(tid)
        traj = tracker.get_trajectory(tid)
        dx, dy = tracker.get_direction_vector(tid)
        _ = (fh, fw, dx, dy)

        if speed < LOITER_SPEED_PX and dwell > LOITER_FRAMES:
            behaviors.append("LOITERING")
            raw += self.behavior_weights["LOITERING"]

        if cls == "person" and self._is_night():
            behaviors.append("NIGHT_MOVEMENT")
            raw += self.behavior_weights["NIGHT_MOVEMENT"]
            if zid in ["ZONE_2", "ZONE_3"]:
                raw += 0.10

        if speed > SPEED_THRESHOLD_PX and cls in ["motorcycle", "bicycle", "car", "truck", "bus"]:
            behaviors.append("SPEEDING")
            raw += self.behavior_weights["SPEEDING"]

        if len(traj) >= 10 and self._count_direction_changes(traj[-15:]) >= ERRATIC_MIN_CHANGES:
            behaviors.append("ERRATIC_MOVEMENT")
            raw += self.behavior_weights["ERRATIC_MOVEMENT"]

        if zid == "ZONE_3":
            behaviors.append("DANGER_ZONE_PRESENCE")
            raw += self.behavior_weights["DANGER_ZONE_PRESENCE"]

        if len(traj) >= 5 and (traj[-1][0] - traj[0][0]) > 60 and zid in ["ZONE_2", "ZONE_3"]:
            behaviors.append("ADVANCING_TO_DANGER")
            raw += self.behavior_weights["ADVANCING_TO_DANGER"]

        if speed > 8.0 and cls == "person":
            behaviors.append("GROUP_MOVEMENT")
            raw += self.behavior_weights["GROUP_MOVEMENT"]

        mult = ZONES[zid]["threat_multiplier"] if zid else 1.0
        final = min(raw * mult, 1.0)
        return {
            "behaviors": behaviors,
            "raw_score": round(raw, 3),
            "behavior_score": round(final, 3),
            "speed": round(speed, 2),
            "dwell_frames": dwell,
            "is_night": self._is_night(),
        }
