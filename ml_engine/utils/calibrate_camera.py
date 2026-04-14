import cv2
import numpy as np
import os
import glob

def calibrate_camera(image_dir, grid_size=(9, 6), square_size=0.025):
    """
    Calibrate camera using a chessboard pattern.
    grid_size: (columns, rows) of internal corners
    square_size: size of a square in meters (default 25mm)
    """
    # Termination criteria for corner sub-pixel accuracy
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Prepare object points (0,0,0), (1,0,0), (2,0,0) ....,(8,5,0)
    objp = np.zeros((grid_size[0] * grid_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:grid_size[0], 0:grid_size[1]].T.reshape(-1, 2)
    objp *= square_size

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    images = glob.glob(os.path.join(image_dir, '*.jpg')) + glob.glob(os.path.join(image_dir, '*.png'))

    if not images:
        print(f"No images found in {image_dir}")
        return None

    gray = None
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, grid_size, None)

        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

            # Draw and display the corners (optional)
            cv2.drawChessboardCorners(img, grid_size, corners2, ret)
            cv2.imshow('Calibration', img)
            cv2.waitKey(100)

    cv2.destroyAllWindows()

    if not objpoints:
        print("Could not find chessboard corners in any image.")
        return None

    # Calibrate
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    
    if ret:
        print("Calibration successful!")
        print("Camera Matrix:\n", mtx)
        print("Distortion Coefficients:\n", dist)
        return mtx, dist
    else:
        print("Calibration failed.")
        return None

def save_calibration(mtx, dist, filename='calibration.npz'):
    np.savez(filename, mtx=mtx, dist=dist)
    print(f"Calibration saved to {filename}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Camera Calibration')
    parser.add_argument('--dir', type=str, required=True, help='Directory containing calibration images')
    parser.add_argument('--cols', type=int, default=9, help='Number of internal corners in columns')
    parser.add_argument('--rows', type=int, default=6, help='Number of internal corners in rows')
    parser.add_argument('--size', type=float, default=0.025, help='Square size in meters')
    args = parser.parse_args()

    result = calibrate_camera(args.dir, (args.cols, args.rows), args.size)
    if result:
        save_calibration(result[0], result[1])
