import cv2
import numpy as np
from config import GROUND_PLANE_POINTS_IMG, GROUND_PLANE_POINTS_WORLD, FRAME_WIDTH, FRAME_HEIGHT

class GroundPlaneTransformer:
    def __init__(self, width=FRAME_WIDTH, height=FRAME_HEIGHT):
        self.width = width
        self.height = height
        self.H = None
        self._compute_homography()

    def _compute_homography(self):
        """
        Compute the homography matrix mapping from image pixels to real-world meters.
        """
        # Source points: normalized 0-1 to pixel coordinates
        src_pts = np.array([
            [p[0] * self.width, p[1] * self.height] for p in GROUND_PLANE_POINTS_IMG
        ], dtype=np.float32)

        # Destination points: real-world coordinates in meters (X, Y)
        dst_pts = np.array(GROUND_PLANE_POINTS_WORLD, dtype=np.float32)

        # Compute the homography matrix
        self.H, _ = cv2.findHomography(src_pts, dst_pts)
        print("Homography computed.")

    def image_to_world(self, x, y):
        """
        Map a pixel coordinate (x, y) to a ground coordinate (X, Y) in meters.
        """
        if self.H is None:
            return 0.0, 0.0

        point = np.array([[[x, y]]], dtype=np.float32)
        world_point = cv2.perspectiveTransform(point, self.H)
        
        X, Y = world_point[0][0]
        return round(float(X), 2), round(float(Y), 2)

    def get_ground_position(self, bbox):
        """
        Given a bbox [x1, y1, x2, y2], return its ground position (X, Y).
        The ground position is the center-bottom of the bounding box.
        """
        x1, y1, x2, y2 = bbox
        cx = (x1 + x2) / 2
        y_bottom = y2
        return self.image_to_world(cx, y_bottom)
