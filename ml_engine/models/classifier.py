from config import *


class ThreatClassifier:
    def __init__(self):
        self.stats = {"NORMAL": 0, "SUSPICIOUS": 0, "HIGH": 0}

    def classify(self, det, behavior_result) -> dict:
        zid = det.get("zone_id", "ZONE_1")
        behaviors = behavior_result["behaviors"]
        score = behavior_result["behavior_score"]
        threshold = ZONES[zid]["alert_threshold"]
        level = "NORMAL"
        reasons = []

        instant_high = ["DANGER_ZONE_PRESENCE", "ADVANCING_TO_DANGER"]
        if any(behavior in behaviors for behavior in instant_high):
            level = "HIGH"
            reasons.append("Critical zone activity")
        elif score >= 0.70:
            level = "HIGH"
            reasons.append(f"Score {score:.2f} exceeds HIGH threshold")
        elif score >= threshold:
            level = "SUSPICIOUS"
            reasons.append(f"Score {score:.2f} exceeds zone threshold")
        elif len(behaviors) >= 2:
            level = "SUSPICIOUS"
            reasons.append("Multiple behaviors detected")
        elif "NIGHT_MOVEMENT" in behaviors and zid != "ZONE_1":
            level = "SUSPICIOUS"
            reasons.append("Night movement in monitored zone")

        if behaviors:
            reasons.append("Behaviors: " + ", ".join(behaviors))

        self.stats[level] += 1
        colors = {"HIGH": (0, 0, 255), "SUSPICIOUS": (0, 165, 255), "NORMAL": (0, 200, 0)}
        prio_l = {"HIGH": 3, "SUSPICIOUS": 2, "NORMAL": 1}
        prio_z = {"ZONE_3": 3, "ZONE_2": 2, "ZONE_1": 1}
        return {
            "threat_level": level,
            "threat_score": score,
            "reasons": reasons,
            "color_bgr": colors[level],
            "alert_priority": prio_l[level] * prio_z.get(zid, 1),
        }

    def get_stats(self) -> dict:
        total = sum(self.stats.values())
        return {
            "counts": self.stats,
            "total": total,
            "high_rate": round(self.stats["HIGH"] / max(total, 1), 3),
        }
