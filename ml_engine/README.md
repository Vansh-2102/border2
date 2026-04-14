# 🛡️ SENTINEL SPATIAL AI (TRIKON 3.0)
### Next-Gen 3D Surveillance & Spatial Intelligence Platform

Trikon 3.0 transforms standard 2D video feeds into a **3D Spatial Intelligence** platform. It utilizes Monocular Depth Estimation and Ground Plane Homography to track targets in real-world metric coordinates (meters) rather than just screen pixels.

---

## 🚀 Key Features

*   **3D Metric Tracking**: Real-time distance estimation using MiDaS Depth and Pinhole camera modeling.
*   **Ground Plane Mapping**: Projects 2D detections onto a 3D tactical radar map (10m x 40m corridor).
*   **Tri-Zone Security**:
    *   🔴 **RED ZONE (0-3m)**: Immediate threat, high-frequency alerts.
    *   🟡 **YELLOW ZONE (3-5m)**: Suspicious activity, medium-frequency alerts.
    *   🟢 **GREEN ZONE (5-40m)**: Routine monitoring, low-frequency alerts.
*   **Dual-Engine Detection**: YOLOv8 for standard objects and specialized models for weapon/thermal detection.
*   **Tactical Dashboard**: A high-tech React-based frontend with real-time WebSocket telemetry and MJPEG video streaming.
*   **Historical Data Lake**: Automated logging of all critical intercepts with distance and behavior metadata.

---

## 🏗️ System Architecture

*   **Backend**: Python, FastAPI, Uvicorn (REST API & WebSockets).
*   **ML Engine**: PyTorch, YOLOv8, MiDaS (Small/Large), OpenCV (CLAHE & Homography).
*   **Frontend**: React 19, Vite, Tailwind CSS, Lucide Icons.
*   **Communication**: 
    *   `MJPEG`: Live video streaming.
    *   `WebSockets`: Real-time telemetry (detections, alerts, stats).
    *   `REST API`: System control (calibration, night vision, logs).

---

## ⚙️ Quick Start Guide

### 1. Prerequisites
Ensure you have Python 3.9+ and Node.js 18+ installed.

### 2. Backend Setup
```bash
cd ml_engine
# Install dependencies
pip install -r requirements.txt
# Run the FastAPI server
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd ml_engine/frontend
# Install dependencies
npm install
# Run the development server
npm run dev
```
Access the dashboard at `http://localhost:5173`.

---

## 🛠️ Configuration

Central configuration is managed in `config.py`:
- **Zones**: Adjust `z_start` and `z_end` for metric boundaries.
- **Ground Plane**: Modify `GROUND_PLANE_POINTS_IMG` for camera-specific perspective.
- **Device**: Automatically targets `cuda` if a GPU is available, else `cpu`.

---

## 📁 Project Structure

- `api/`: FastAPI server and ML interface logic.
- `frontend/`: React source code and dashboard components.
- `models/`: ML ensemble (Detector, Depth, Behavior, Tracker).
- `utils/`: Camera calibration, spatial mapping, and visualization tools.
- `weights/`: Pre-trained YOLOv8 and custom surveillance models.

---

## ⚖️ Behavior Rules
The system evaluates 7 core behavior rules to calculate threat scores:
- **LOITERING**: Stationary for >45 frames.
- **NIGHT_MOVEMENT**: Human detected during night hours.
- **SPEEDING**: Vehicle speed exceeding baseline thresholds.
- **ERRATIC_MOVEMENT**: Multiple rapid direction changes.
- **DANGER_ZONE_PRESENCE**: Any entry into the RED zone.
- **ADVANCING_TO_DANGER**: Movement trajectory heading toward the camera.
- **GROUP_MOVEMENT**: Multiple humans moving in formation.
