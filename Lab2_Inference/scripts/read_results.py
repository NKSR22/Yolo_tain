from ultralytics import YOLO

MODEL_PATH = "../Lab1_TrainReadyDataset/runs/train/weights/best.pt"
IMAGE_PATH = "../Lab2_Inference/samples/test.jpg"

model = YOLO(MODEL_PATH)
results = model(IMAGE_PATH)

for r in results:
    for box in r.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        print(f"class={model.names[cls_id]} conf={conf:.2f} box=({x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f})")
