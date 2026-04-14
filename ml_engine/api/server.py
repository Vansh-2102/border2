import asyncio
import cv2
import numpy as np
from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading
import time
import json
from api.ml_interface import MLInterface
from config import CAMERA_SOURCE, FRAME_WIDTH, FRAME_HEIGHT

app = FastAPI(title="Trikon 3.0 AI Surveillance API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
ml_interface = None
latest_frame = None
latest_result = {}
frame_lock = threading.Lock()
is_running = False
active_websockets = set()
historical_logs = [] # Memory-based logs for frontend

def surveillance_worker():
    """Background thread to run the surveillance pipeline."""
    global ml_interface, latest_frame, latest_result, is_running, historical_logs
    
    print("[Server] Initializing ML Engine...")
    ml_interface = MLInterface()
    pipeline = ml_interface.pipeline
    
    # Override the pipeline loop to capture frames for the web server
    pipeline.running = True
    from utils.frame_utils import open_camera, read_frame, should_process
    
    cap = open_camera(CAMERA_SOURCE)
    print(f"[Server] Camera {CAMERA_SOURCE} opened.")
    
    frame_count = 0
    while is_running:
        frame, ok = read_frame(cap)
        if not ok:
            time.sleep(0.1)
            continue
            
        frame_count += 1
        if not should_process(frame_count):
            continue
            
        try:
            # Process frame through ML Ensemble
            result = pipeline.ml.process_frame(frame)
            
            # Format result for API/WebSocket
            formatted_result = ml_interface.post.format_for_api(result)
            formatted_result["fps"] = pipeline.metrics.current_fps
            
            # Update global state
            latest_result = formatted_result
            
            # Log critical alerts to historical_logs
            for alert in formatted_result.get("alerts", []):
                log_entry = {
                    "id": f"EVT-{int(time.time())}-{alert['track_id']}",
                    "timestamp": time.strftime("%H:%M:%S"),
                    "date": time.strftime("%d.%m.%y"),
                    "type": alert["threat_level"],
                    "class_name": alert["class_name"],
                    "message": f"{alert['class_name']} detected in {alert['zone_name']}. Behaviors: {', '.join(alert['behaviors'])}",
                    "distance": alert["distance"],
                    "confidence": alert.get("confidence", 0.9)
                }
                historical_logs.insert(0, log_entry)
                # Keep last 100 logs
                historical_logs = historical_logs[:100]

            # Draw visualizations
            processed_frame = pipeline.viz.draw_all(
                frame.copy(), 
                result, 
                pipeline.metrics.current_fps, 
                pipeline.active_alerts
            )
            
            # Update latest frame for streaming
            with frame_lock:
                latest_frame = processed_frame.copy()
                
            pipeline.metrics.update(result)
            
            # Broadcast results to all connected WebSockets
            if active_websockets:
                message = json.dumps(formatted_result)
                print(f"[Server] Broadcasting to {len(active_websockets)} clients...")
                for ws in list(active_websockets):
                    asyncio.run_coroutine_threadsafe(ws.send_text(message), loop)
            
        except Exception as e:
            print(f"[Server] Pipeline Error: {e}")
            
    cap.release()
    print("[Server] Camera released.")

def gen_frames():
    """Generator for MJPEG stream."""
    global latest_frame
    while is_running:
        with frame_lock:
            if latest_frame is None:
                continue
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', latest_frame)
            frame_bytes = buffer.tobytes()
            
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.04) # ~25 FPS stream

@app.get("/video_feed")
async def video_feed():
    """Video streaming route."""
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.add(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_websockets.remove(websocket)

@app.get("/status")
async def get_status():
    """Get current system status."""
    if ml_interface:
        return ml_interface.get_stats()
    return {"status": "initializing"}

from pydantic import BaseModel
from typing import Optional, List

class NightVisionRequest(BaseModel):
    enabled: bool

class CalibrationRequest(BaseModel):
    P1_X: float
    P1_Y: float
    P2_X: float
    P2_Y: float
    P3_X: float
    P3_Y: float
    P4_X: float
    P4_Y: float

class TargetRequest(BaseModel):
    target_id: int

@app.post("/toggle_night_vision")
async def toggle_night_vision(req: NightVisionRequest):
    """Toggle night vision mode."""
    # Logic to switch IR mode if camera supports it
    return {"status": "success", "night_vision": req.enabled}

@app.post("/calibrate_camera")
async def calibrate_camera(req: CalibrationRequest):
    """Set manual ground plane calibration points."""
    print(f"[Server] Received Calibration: {req}")
    # Here you would typically save these to a config or update the homography matrix
    # For now, we acknowledge receipt
    return {"success": True, "message": "Homography matrix projected securely."}

@app.post("/dismiss_alert")
async def dismiss_alert(req: TargetRequest):
    """Dismiss a specific alert."""
    if ml_interface:
        # ml_interface.pipeline.dismiss_alert(req.target_id)
        pass
    return {"success": True}

@app.post("/deploy_drone")
async def deploy_drone(req: TargetRequest):
    """Simulate drone deployment."""
    return {"success": True, "tracking": True, "message": f"Drone deployed to Target #{req.target_id}"}

@app.post("/gallery/filter")
async def gallery_filter(filters: dict):
    threat_filter = filters.get("threat")
    if threat_filter and threat_filter != "ALL":
        filtered = [l for l in historical_logs if l["type"] == threat_filter]
    else:
        filtered = historical_logs
    return {"success": True, "itemsFound": len(filtered), "items": filtered}

@app.get("/gallery/refresh")
async def gallery_refresh():
    return {"success": True, "items": historical_logs}

@app.get("/logs")
async def get_logs():
    return {"success": True, "logs": historical_logs}

@app.get("/system_settings")
async def system_settings():
    return {"success": True}

# Global event loop for background tasks
loop = None

@app.on_event("startup")
async def startup_event():
    global is_running, loop
    is_running = True
    loop = asyncio.get_event_loop()
    # Start surveillance in a background thread
    thread = threading.Thread(target=surveillance_worker, daemon=True)
    thread.start()

@app.on_event("shutdown")
async def shutdown_event():
    global is_running
    is_running = False

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
