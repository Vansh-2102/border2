import cv2
import numpy as np

from config import *


class NightVisionEnhancer:
    def __init__(self):
        self.clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP_LIMIT, tileGridSize=CLAHE_TILE_GRID)
        self.frames_enhanced = 0
        self.frames_normal = 0

    def is_low_light(self, frame) -> bool:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return float(np.mean(gray)) < NIGHT_BRIGHTNESS_THRESHOLD

    def enhance(self, frame):
        if not self.is_low_light(frame):
            self.frames_normal += 1
            return frame, False
        
        # Apply Thermal/Infrared mapping if configured
        if INFRARED_MODE:
            frame = self.simulate_thermal(frame)
        else:
            frame = self._clahe(frame)
            frame = self._gamma(frame)
            frame = self._denoise(frame)
            
        self.frames_enhanced += 1
        return frame, True

    def _clahe(self, frame):
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l = self.clahe.apply(l)
        return cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)

    def _gamma(self, frame):
        table = np.array([((i / 255.0) ** (1.0 / GAMMA_VALUE)) * 255 for i in range(256)], dtype=np.uint8)
        return cv2.LUT(frame, table)

    def _denoise(self, frame):
        return cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)

    def simulate_thermal(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Apply configured thermal colormap (Inference, Plasma, etc)
        return cv2.applyColorMap(gray, THERMAL_COLORMAP)

    def get_stats(self) -> dict:
        total = self.frames_enhanced + self.frames_normal
        return {
            "enhanced": self.frames_enhanced,
            "normal": self.frames_normal,
            "rate": round(self.frames_enhanced / max(total, 1), 3),
        }
