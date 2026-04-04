import os
import json
from ultralytics import YOLO
from config import *

# Load model
model_path = TRAINED_MODEL_PATH if os.path.exists(TRAINED_MODEL_PATH) else BASE_MODEL_PATH
model = YOLO(model_path)

print(f"Evaluating model: {model_path}")

# Run validation
results = model.val(data=os.path.abspath(DATASET_YAML), imgsz=IMG_SIZE, conf=0.45)

# Extract metrics
mAP50 = results.results_dict["metrics/mAP50(B)"]
mAP50_95 = results.results_dict["metrics/mAP50-95(B)"]
precision = results.results_dict["metrics/precision(B)"]
recall = results.results_dict["metrics/recall(B)"]

# Verdict logic
if mAP50 >= 0.75:
    verdict = "EXCELLENT"
elif mAP50 >= 0.60:
    verdict = "GOOD"
elif mAP50 >= 0.45:
    verdict = "FAIR"
else:
    verdict = "POOR"

print("\n--- Evaluation Report ---")
print(f"mAP50:      {mAP50:.4f}")
print(f"mAP50-95:   {mAP50_95:.4f}")
print(f"Precision:  {precision:.4f}")
print(f"Recall:     {recall:.4f}")
print(f"Verdict:    {verdict}")

# Save report
os.makedirs(REPORTS_DIR, exist_ok=True)
report = {
    "model_path": model_path,
    "metrics": {
        "mAP50": mAP50,
        "mAP50-95": mAP50_95,
        "precision": precision,
        "recall": recall
    },
    "verdict": verdict
}

report_path = os.path.join(REPORTS_DIR, "eval_report.json")
with open(report_path, "w") as f:
    json.dump(report, f, indent=4)

print(f"\nReport saved to: {report_path}")
