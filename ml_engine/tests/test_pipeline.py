import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from api.ml_interface import MLInterface

def test_creates():
    ml = MLInterface()
    assert ml is not None

def test_single_frame():
    ml = MLInterface()
    r = ml.process_single_frame(np.zeros((720, 1280, 3), dtype=np.uint8))
    assert isinstance(r, dict)

def test_required_keys():
    ml = MLInterface()
    r = ml.process_single_frame(np.zeros((720, 1280, 3), dtype=np.uint8))
    for k in ["detections", "alerts", "zone_counts", "threat_counts", "frame_number", "was_enhanced"]:
        assert k in r

def test_no_crash_none():
    ml = MLInterface()
    try:
        ml.process_single_frame(None)
    except Exception:
        pytest.fail("process_single_frame(None) crashed")
