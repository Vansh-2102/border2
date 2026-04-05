import asyncio
import os
import cv2
import time
from models.ensemble import MLEnsemble
from utils.frame_utils import open_camera, read_frame, should_process, save_snapshot
from utils.visualization import Visualizer
from utils.metrics import MetricsTracker
from config import CAMERA_SOURCE


class InferencePipeline:
    def __init__(self, output_callback=None):
        self.ml = MLEnsemble()
        self.viz = Visualizer()
        self.metrics = MetricsTracker()
        self.callback = output_callback
        self.running = False
        self.cap = None
        self.latest_result = {}
        self.frame_count = 0
        self.active_alerts = []

    async def start(self, camera_source=CAMERA_SOURCE):
        self.running = True
        self.cap = open_camera(camera_source)
        print("[Pipeline] Started.")
        while self.running:
            frame, ok = read_frame(self.cap)
            if not ok:
                await asyncio.sleep(0.1)
                continue
            self.frame_count += 1
            if not should_process(self.frame_count):
                await asyncio.sleep(0.005)
                continue
            try:
                result = self.ml.process_frame(frame)
                result["fps"] = self.metrics.current_fps
                
                # Update active alerts list (remove expired, add new)
                now = time.time()
                self.active_alerts = [a for a in self.active_alerts if a["expiry"] > now]
                for alert in result.get("alerts", []):
                    self.active_alerts.append({"alert": alert, "expiry": now + 5.0})
                
                display = self.viz.draw_all(frame.copy(), result, self.metrics.current_fps, self.active_alerts)
                cv2.imshow("Border Surveillance", display)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.stop()
                for alert in result.get("alerts", []):
                    if alert["threat_level"] == "HIGH":
                        for det in result["detections"]:
                            if det["track_id"] == alert["track_id"]:
                                save_snapshot(display, det)
                                break
                self.metrics.update(result)
                self.latest_result = result
                if self.callback:
                    await self.callback(result)
            except Exception as e:
                print(f"[Pipeline] Error: {e}")
            await asyncio.sleep(0.01)

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    def get_latest(self) -> dict:
        return self.latest_result

    def get_stats(self) -> dict:
        s = self.metrics.get_summary()
        s["ml_stats"] = self.ml.get_all_stats()
        return s
