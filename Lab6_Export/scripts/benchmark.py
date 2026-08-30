"""Lab 6 - เทียบความเร็วและขนาดไฟล์ของแต่ละฟอร์แมต

วัด 3 แบบ:
  .pt  บน GPU   - แบบที่ใช้ตอนพัฒนาบนเครื่อง PC
  .pt  บน CPU   - จำลองเครื่องที่ไม่มีการ์ดจอ
  .onnx บน CPU  - แบบที่จะเอาไปรันบน Raspberry Pi ใน Lab 7

เทียบ .pt บน GPU กับ .onnx บน CPU ตรง ๆ ไม่ได้ (คนละฮาร์ดแวร์)
คู่ที่ตอบคำถาม "ONNX ช่วยจริงไหม" คือสองบรรทัดที่รันบน CPU เหมือนกัน
"""
import time
from pathlib import Path

import torch
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = ROOT / "runs" / "detect" / "full" / "weights"
IMAGE = str(ROOT / "Lab3_CustomDataset" / "raw_images" / "wild_01.jpg")
N_WARMUP = 5
N_RUNS = 20


def bench(label, path, device):
    if not path.exists():
        print(f"{label:22s} file not found ({path.name}) - skipping")
        return
    model = YOLO(str(path))
    for _ in range(N_WARMUP):          # อุ่นเครื่องก่อน เฟรมแรก ๆ ช้ากว่าปกติเสมอ
        model(IMAGE, device=device, verbose=False)

    t0 = time.perf_counter()
    for _ in range(N_RUNS):
        model(IMAGE, device=device, verbose=False)
    ms = (time.perf_counter() - t0) / N_RUNS * 1000

    size_mb = path.stat().st_size / 1e6
    # ข้อความ print เป็น ASCII - console ที่ไม่ใช่ codepage ไทยจะพังถ้าเจอภาษาไทย
    print(f"{label:22s} {ms:7.1f} ms/image  {1000 / ms:6.1f} FPS   file {size_mb:5.1f} MB")


def main():
    if not MODEL_DIR.exists():
        raise SystemExit(f"{MODEL_DIR} not found. Run Lab 4 train_full.bat first.")

    print(f"image  : {Path(IMAGE).name}")
    print(f"runs   : {N_RUNS} (warmup {N_WARMUP})")
    print(f"device : {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU only'}")
    print("-" * 70)

    if torch.cuda.is_available():
        bench(".pt  on GPU", MODEL_DIR / "best.pt", 0)
    bench(".pt  on CPU", MODEL_DIR / "best.pt", "cpu")
    bench(".onnx on CPU", MODEL_DIR / "best.onnx", "cpu")

    print("-" * 70)
    print("Compare the two CPU rows to see what ONNX actually buys you.")
    print("The GPU row is your PC speed - it is not what a Raspberry Pi will give.")


if __name__ == "__main__":
    main()
