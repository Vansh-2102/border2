from api.ml_interface import MLInterface
import asyncio
import os

async def main():
    # Ensure necessary directories exist
    os.makedirs("data/snapshots", exist_ok=True)
    os.makedirs("weights/base", exist_ok=True)
    
    ml = MLInterface()
    
    async def on_result(r):
        for a in r["alerts"]:
            print(f"--- ALERT: {a['threat_level']} in {a['zone_name']} ---")
            print(f"Behaviors: {', '.join(a['behaviors'])}")
            print("-" * 40)
    
    print("\n[INFO] Starting Border Surveillance System...")
    print("[INFO] Press 'q' in the video window to stop.\n")
    
    try:
        # source=0 for webcam, or path to a video file
        await ml.start(camera_source=0, callback=on_result)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\n[INFO] Stopping system...")
    except Exception as e:
        print(f"\n[ERROR] {e}")
    finally:
        ml.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
