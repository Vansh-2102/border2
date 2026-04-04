import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from models.detector import ObjectDetector

def test_detector_loads():
    d = ObjectDetector()
    assert d is not None

def test_blank_frame():
    d = ObjectDetector()
    r = d.detect(np.zeros((720, 1280, 3), dtype=np.uint8))
    assert isinstance(r, list)

def test_required_keys():
    d = ObjectDetector()
    r = d.detect(np.zeros((640, 640, 3), dtype=np.uint8))
    if r:
        for k in ["bbox", "confidence", "class_name", "track_id"]:
            assert k in r[0]

def test_confidence_value():
    from config import CONFIDENCE_THRESHOLD
    assert 0.0 < CONFIDENCE_THRESHOLD < 1.0
