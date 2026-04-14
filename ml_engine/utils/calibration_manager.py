import numpy as np
import cv2
import os

class CalibrationManager:
    def __init__(self, calibration_file='calibration.npz'):
        self.mtx = None
        self.dist = None
        self.focal_length = None
        self.cx = None
        self.cy = None
        self.load(calibration_file)

    def load(self, filename):
        if not os.path.exists(filename):
            print(f"Calibration file {filename} not found.")
            return False
        
        data = np.load(filename)
        self.mtx = data['mtx']
        self.dist = data['dist']
        
        # Focal length in pixels (assuming fx = fy for simplicity or taking average)
        self.fx = self.mtx[0, 0]
        self.fy = self.mtx[1, 1]
        self.focal_length = (self.fx + self.fy) / 2
        
        # Principal point (optical center)
        self.cx = self.mtx[0, 2]
        self.cy = self.mtx[1, 2]
        
        print(f"Calibration loaded. Focal length: {self.focal_length:.2f} px")
        return True

    def undistort(self, frame):
        if self.mtx is None:
            return frame
        return cv2.undistort(frame, self.mtx, self.dist)

    def get_focal_length(self):
        return self.focal_length
