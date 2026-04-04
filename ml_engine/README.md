# Border Surveillance ML Engine

## Zone System
+----------+----------+----------+
| ZONE 1   | ZONE 2   | ZONE 3   |
| GREEN    | YELLOW   | RED      |
| x1.0     | x1.5     | x2.5     |
| thr:0.65 | thr:0.40 | thr:0.15 |
+----------+----------+----------+

## Install
pip install -r requirements.txt

## Run Tests
pytest tests/ -v

## Training Steps
1. Put .mp4 files in data/raw_videos/
2. python training/dataset_builder.py
3. python training/trainer.py
4. python training/evaluator.py
5. Set USE_TRAINED_MODEL=True in config.py

## Teammate Integration (5 lines)
from api.ml_interface import MLInterface
import asyncio
ml = MLInterface()
async def on_result(r): print(r["alerts"])
asyncio.run(ml.start(camera_source=0, callback=on_result))

## 7 Behavior Rules
- LOITERING: stationary >45 frames, score+0.40
- NIGHT_MOVEMENT: person after 8pm, score+0.30
- SPEEDING: vehicle >12px/frame, score+0.30
- ERRATIC_MOVEMENT: 3+ direction changes, score+0.25
- DANGER_ZONE_PRESENCE: any object in ZONE_3, score+0.45
- ADVANCING_TO_DANGER: moving toward RED zone, score+0.35
- GROUP_MOVEMENT: person running fast, score+0.20
