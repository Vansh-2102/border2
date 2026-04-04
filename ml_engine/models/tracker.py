from collections import defaultdict, deque
import math
import time

import numpy as np

from config import *


class MultiObjectTracker:
    def __init__(self):
        self.history = defaultdict(lambda: deque(maxlen=HISTORY_MAXLEN))
        self.prev_bboxes = {}
        self.lost_count = {}
        self.next_id = 1
        self.alert_times = {}

    def _iou(self, boxA, boxB) -> float:
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        inter = max(0, xB - xA) * max(0, yB - yA)
        aA = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        aB = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        return inter / (aA + aB - inter + 1e-6)

    def update(self, detections, frame_num) -> list:
        if not detections:
            expired_ids = []
            for track_id in list(self.lost_count.keys()):
                self.lost_count[track_id] = self.lost_count.get(track_id, 0) + 1
                if self.lost_count[track_id] > MAX_LOST_FRAMES:
                    expired_ids.append(track_id)
            for track_id in expired_ids:
                self.prev_bboxes.pop(track_id, None)
                self.lost_count.pop(track_id, None)
                self.history.pop(track_id, None)
            return []

        matched_track_ids = set()
        for det in detections:
            bbox = det["bbox"]
            best_track_id = None
            best_iou = 0.0
            for track_id, prev_bbox in self.prev_bboxes.items():
                if track_id in matched_track_ids:
                    continue
                iou = self._iou(bbox, prev_bbox)
                if iou >= IOU_MATCH_THRESHOLD and iou > best_iou:
                    best_iou = iou
                    best_track_id = track_id

            if best_track_id is None:
                track_id = self.next_id
                self.next_id += 1
            else:
                track_id = best_track_id

            x1, y1, x2, y2 = bbox
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0
            self.history[track_id].append((cx, cy, frame_num))
            self.prev_bboxes[track_id] = bbox
            self.lost_count[track_id] = 0
            det["track_id"] = track_id
            matched_track_ids.add(track_id)

        expired_ids = []
        for track_id in list(self.lost_count.keys()):
            if track_id not in matched_track_ids:
                self.lost_count[track_id] = self.lost_count.get(track_id, 0) + 1
                if self.lost_count[track_id] > MAX_LOST_FRAMES:
                    expired_ids.append(track_id)
        for track_id in expired_ids:
            self.prev_bboxes.pop(track_id, None)
            self.lost_count.pop(track_id, None)
            self.history.pop(track_id, None)

        return detections

    def get_speed(self, tid) -> float:
        history = list(self.history[tid])
        if len(history) < 2:
            return 0.0
        recent = history[-10:]
        dists = [
            math.hypot(recent[i][0] - recent[i - 1][0], recent[i][1] - recent[i - 1][1])
            for i in range(1, len(recent))
        ]
        return float(np.mean(dists)) if dists else 0.0

    def get_dwell_frames(self, tid) -> int:
        return len(self.history[tid])

    def get_trajectory(self, tid, n=30) -> list:
        return [(x, y) for x, y, _ in list(self.history[tid])[-n:]]

    def get_direction_vector(self, tid) -> tuple:
        traj = self.get_trajectory(tid, 10)
        if len(traj) < 2:
            return (0.0, 0.0)
        return (traj[-1][0] - traj[0][0], traj[-1][1] - traj[0][1])

    def can_alert(self, tid, zone_id) -> bool:
        key = (tid, zone_id)
        cooldown = ZONES[zone_id]["cooldown_sec"]
        return (time.time() - self.alert_times.get(key, 0)) >= cooldown

    def record_alert(self, tid, zone_id):
        self.alert_times[(tid, zone_id)] = time.time()
