import torch
import cv2
import numpy as np
from config import AVG_PERSON_HEIGHT_M, WEAPON_SIZES_M, DEFAULT_FOCAL_LENGTH_PX, DEVICE
from collections import deque

class DistanceSmoother:
    def __init__(self, window_size=5):
        self.history = deque(maxlen=window_size)

    def update(self, new_val):
        self.history.append(new_val)
        return sum(self.history) / len(self.history)

class DepthEstimator:
    def __init__(self, model_type="MiDaS_small", calibration=None):
        self.device = torch.device(DEVICE)
        self.model = torch.hub.load("intel-isl/MiDaS", model_type, trust_repo=True)
        self.model.to(self.device)
        self.model.eval()

        self.calibration = calibration
        midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms", trust_repo=True)
        if model_type == "DPT_Large" or model_type == "DPT_Hybrid":
            self.transform = midas_transforms.dpt_transform
        else:
            self.transform = midas_transforms.small_transform
        
        self.smoothers = {} # track_id -> DistanceSmoother

    def estimate(self, frame):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_batch = self.transform(img).to(self.device)

        with torch.no_grad():
            prediction = self.model(input_batch)
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=frame.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()

        depth_map = prediction.cpu().numpy()
        # MiDaS outputs relative inverse depth (disparity). Larger values are closer.
        # Normalize to 0-1 for easier handling.
        depth_min = depth_map.min()
        depth_max = depth_map.max()
        depth_map_norm = (depth_map - depth_min) / (depth_max - depth_min + 1e-6)
        return depth_map_norm

    def get_distance(self, depth_map, bbox, frame_shape, class_name="person", track_id=None):
        """
        Estimate distance for a bounding box using a combination of the pinhole 
        camera model and the MiDaS depth map.
        bbox: [x1, y1, x2, y2]
        """
        fh, fw = frame_shape[:2]
        x1, y1, x2, y2 = map(int, bbox)
        pixel_height = y2 - y1

        # 1. Pinhole Model: Z = (f * H) / h
        # Use calibration focal length if available
        f = self.calibration.get_focal_length() if self.calibration else None
        if f is None:
            f = DEFAULT_FOCAL_LENGTH_PX
        
        real_height = AVG_PERSON_HEIGHT_M if class_name == "person" else WEAPON_SIZES_M.get(class_name, 0.5)
        
        # Pinhole distance (absolute metric distance)
        pinhole_dist = (f * real_height) / max(pixel_height, 1)

        # 2. Depth Map Refinement (Relative depth)
        person_depth = depth_map[y1:y2, x1:x2]
        if person_depth.size == 0:
            raw_dist = float(pinhole_dist)
        else:
            # Median disparity from MiDaS (larger = closer)
            avg_depth_norm = np.median(person_depth)
            
            # 3. Fuse both estimates
            # Pinhole provides scale, MiDaS provides local precision.
            # We use a non-linear weight: as the person gets closer, we trust MiDaS more.
            # Depth maps are more accurate at close ranges.
            midas_weight = 0.4 + (0.3 * avg_depth_norm) # 0.4 to 0.7 weight
            
            # Convert disparity to a relative multiplier
            # 0.5 disparity is our "anchor" point
            dist_multiplier = 1.0 - (avg_depth_norm - 0.5) * 0.5
            
            raw_dist = pinhole_dist * dist_multiplier

        # 4. Temporal Smoothing
        if track_id is not None:
            if track_id not in self.smoothers:
                self.smoothers[track_id] = DistanceSmoother(window_size=7)
            dist = self.smoothers[track_id].update(raw_dist)
        else:
            dist = raw_dist
        
        return round(float(dist), 2)
