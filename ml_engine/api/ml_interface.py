"""
USAGE:
from api.ml_interface import MLInterface
import asyncio
ml = MLInterface()
async def on_result(r):
    for a in r["alerts"]: print(a["threat_level"],a["zone_name"])
asyncio.run(ml.start(camera_source=0, callback=on_result))
"""
from inference.pipeline import InferencePipeline
from inference.postprocessor import PostProcessor


class MLInterface:
    def __init__(self):
        self.pipeline = InferencePipeline()
        self.post = PostProcessor()
        print("[MLInterface] Ready.")

    async def start(self, camera_source=0, callback=None):
        if callback:
            self.pipeline.callback = callback
        await self.pipeline.start(camera_source)

    def stop(self):
        self.pipeline.stop()

    def get_latest_result(self) -> dict:
        raw = self.pipeline.get_latest()
        return self.post.format_for_api(raw) if raw else {}

    def get_stats(self) -> dict:
        return self.pipeline.get_stats()

    def process_single_frame(self, frame) -> dict:
        try:
            if frame is None:
                return {}
            raw = self.pipeline.ml.process_frame(frame)
            return self.post.format_for_api(raw)
        except Exception as e:
            print(f"[MLInterface] Error: {e}")
            return {}
