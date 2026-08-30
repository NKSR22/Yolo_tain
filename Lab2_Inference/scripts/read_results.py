"""Lab 2 - อ่านค่า box / class / confidence จากผลลัพธ์ Detection ด้วย Python"""
from pathlib import Path

from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent.parent.parent  # โฟลเดอร์หลักของโปรเจกต์ (Yolo_tain)
MODEL_PATH = ROOT / "runs" / "detect" / "train" / "weights" / "best.pt"
IMAGE_PATH = ROOT / "Lab2_Inference" / "samples" / "test.jpg"

if not MODEL_PATH.exists():
    raise SystemExit(f"Model not found: {MODEL_PATH}\nRun train.bat in Lab1_TrainReadyDataset/scripts first.")
if not IMAGE_PATH.exists():
    raise SystemExit(f"Image not found: {IMAGE_PATH}\nRun get_samples.bat first.")

model = YOLO(str(MODEL_PATH))
results = model(str(IMAGE_PATH))

for r in results:
    for box in r.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        print(f"class={model.names[cls_id]} conf={conf:.2f} box=({x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f})")
