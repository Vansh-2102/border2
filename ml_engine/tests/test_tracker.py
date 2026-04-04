import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from models.tracker import MultiObjectTracker

def _make_det(x1=100, y1=100, x2=200, y2=200):
    return {
        "bbox": [x1, y1, x2, y2],
        "class_name": "person",
        "confidence": 0.9,
        "class_id": 0,
        "track_id": None,
        "zone_id": "ZONE_1",
        "zone_name": "GREEN ZONE",
        "behaviors": [],
        "behavior_score": 0.0,
        "threat_level": "NORMAL",
        "trajectory": [],
        "cx": 150.0,
        "cy": 150.0,
        "cx_norm": 0.15,
        "cy_norm": 0.2
    }

def test_assigns_id():
    t = MultiObjectTracker()
    r = t.update([_make_det()], 1)
    assert r[0]["track_id"] == 1

def test_same_object_same_id():
    t = MultiObjectTracker()
    for i in range(3):
        r = t.update([_make_det()], i + 1)
    assert r[0]["track_id"] == 1

def test_speed_stationary():
    t = MultiObjectTracker()
    for i in range(20):
        t.update([_make_det()], i + 1)
    assert t.get_speed(1) < 1.0

def test_trajectory_max():
    t = MultiObjectTracker()
    for i in range(50):
        t.update([_make_det()], i + 1)
    assert len(t.get_trajectory(1)) <= 30

def test_cooldown():
    t = MultiObjectTracker()
    t.update([_make_det()], 1)
    t.record_alert(1, "ZONE_1")
    assert t.can_alert(1, "ZONE_1") == False
