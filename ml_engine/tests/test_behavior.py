import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from models.tracker import MultiObjectTracker
from models.behavior import BehaviorAnalyzer

def _make_det(zid="ZONE_1", cls="person"):
    return {
        "bbox": [100, 100, 200, 200],
        "class_name": cls,
        "confidence": 0.9,
        "class_id": 0,
        "track_id": 1,
        "zone_id": zid,
        "zone_name": "TEST",
        "behaviors": [],
        "behavior_score": 0.0,
        "threat_level": "NORMAL",
        "trajectory": [],
        "cx": 150.0,
        "cy": 150.0,
        "cx_norm": 0.15,
        "cy_norm": 0.2
    }

def test_loitering():
    t = MultiObjectTracker()
    a = BehaviorAnalyzer()
    for i in range(60):
        t.update([_make_det()], i + 1)
    r = a.analyze(_make_det(), t, (720, 1280))
    assert "LOITERING" in r["behaviors"]

def test_zone3_presence():
    t = MultiObjectTracker()
    a = BehaviorAnalyzer()
    t.update([_make_det("ZONE_3")], 1)
    r = a.analyze(_make_det("ZONE_3"), t, (720, 1280))
    assert "DANGER_ZONE_PRESENCE" in r["behaviors"]

def test_multiplier():
    t = MultiObjectTracker()
    a = BehaviorAnalyzer()
    for i in range(60):
        t.update([_make_det("ZONE_1")], i + 1)
    r1 = a.analyze(_make_det("ZONE_1"), t, (720, 1280))
    
    t2 = MultiObjectTracker()
    for i in range(60):
        t2.update([_make_det("ZONE_3")], i + 1)
    r3 = a.analyze(_make_det("ZONE_3"), t2, (720, 1280))
    assert r3["behavior_score"] >= r1["behavior_score"]

def test_score_capped():
    t = MultiObjectTracker()
    a = BehaviorAnalyzer()
    for i in range(60):
        t.update([_make_det("ZONE_3")], i + 1)
    r = a.analyze(_make_det("ZONE_3"), t, (720, 1280))
    assert r["behavior_score"] <= 1.0
