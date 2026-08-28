import time
from pathlib import Path
from ultralytics import YOLO

MODEL_DIR = Path("../../Lab4_TrainTuning/runs/exp/weights")
IMAGE = "../../Lab2_Inference/samples/test.jpg"
N_RUNS = 20

for fmt, path in [("PyTorch (.pt)", MODEL_DIR / "best.pt"), ("ONNX (.onnx)", MODEL_DIR / "best.onnx")]:
    if not path.exists():
        print(f"{fmt}: file not found ({path}), skipping")
        continue
    model = YOLO(str(path))
    model(IMAGE)  # warmup
    t0 = time.time()
    for _ in range(N_RUNS):
        model(IMAGE, verbose=False)
    dt = (time.time() - t0) / N_RUNS
    size_mb = path.stat().st_size / 1e6
    print(f"{fmt}: {dt*1000:.1f} ms/inference | size={size_mb:.1f} MB")
