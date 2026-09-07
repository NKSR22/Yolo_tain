#!/bin/bash
# Lab 7 - ติดตั้ง environment สำหรับรัน YOLO บน Raspberry Pi OS (64-bit)
# รันบนตัว Pi เท่านั้น:  cd ~/Lab7_RaspberryPi/scripts && ./setup_pi.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[1/4] ติดตั้งแพ็กเกจระบบ"
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip
# ไม่ต้องติดตั้ง libopencv-dev: ล้อ opencv-python สำหรับ aarch64 มี OpenCV
# มาให้ในตัวแล้ว (49.8 MB) การลง libopencv-dev เปลืองพื้นที่เกือบ 1 GB ฟรี ๆ

echo "[2/4] สร้าง virtual environment"
python3 -m venv venv
./venv/bin/pip install --quiet --upgrade pip

echo "[3/4] ติดตั้ง PyTorch รุ่น CPU"
# จุดที่พลาดกันบ่อยที่สุดของแล็บนี้
# torch สำหรับ aarch64 บน PyPI เป็นรุ่นที่ผูกกับ CUDA ถ้าปล่อยให้ pip เลือกเอง
# มันจะโหลด torch 454 MB พ่วงไลบรารี NVIDIA (cuBLAS, cuDNN, NCCL, triton ...)
# อีกหลาย GB ลงเครื่องที่ไม่มีการ์ดจอ NVIDIA ต้องชี้ไป index รุ่น CPU เสมอ
./venv/bin/pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

echo "[4/4] ติดตั้ง ultralytics + opencv + onnxruntime"
# ต้องมี onnx ด้วย ไม่งั้นตอนรัน fps_test.py ครั้งแรก ultralytics จะแอบติดตั้งให้เอง
# (ขึ้นข้อความ AutoUpdate) ซึ่งพังถ้าเน็ตไม่มีตอนนั้น
./venv/bin/pip install ultralytics opencv-python onnxruntime onnx

echo
echo "=================== ตรวจผลการติดตั้ง ==================="
./venv/bin/python - <<'PY'
import importlib, shutil, sys
from pathlib import Path

def check(label, fn):
    try:
        print(f"  [OK]   {label}: {fn()}")
        return True
    except Exception as e:
        print(f"  [FAIL] {label}: {type(e).__name__}: {e}")
        return False

ok = True
ok &= check("python", lambda: sys.version.split()[0])
ok &= check("torch", lambda: importlib.import_module("torch").__version__)
ok &= check("ultralytics", lambda: importlib.import_module("ultralytics").__version__)
ok &= check("opencv", lambda: importlib.import_module("cv2").__version__)
ok &= check("onnxruntime", lambda: importlib.import_module("onnxruntime").__version__)

# torch ต้องเป็นรุ่น CPU ถ้าลงท้ายด้วยเลข CUDA แสดงว่าดึงผิด index มา
import torch
if "+cpu" not in torch.__version__ and torch.version.cuda:
    print(f"  [WARN] torch รุ่นนี้ผูกกับ CUDA {torch.version.cuda} - Pi ใช้ไม่ได้")
    print("         ลบ venv แล้วรันสคริปต์นี้ใหม่")
    ok = False

model = Path("model/best.onnx")
if model.exists():
    print(f"  [OK]   model/best.onnx: {model.stat().st_size/1e6:.1f} MB")
else:
    print("  [ ]    model/best.onnx: ยังไม่มี - คัดลอกมาจาก Lab 6 ก่อนรัน detection")

cams = sorted(Path("/dev").glob("video[0-9]"))
print(f"  [{'OK' if cams else ' ' }]   กล้อง: {', '.join(p.name for p in cams) if cams else 'ไม่พบ /dev/video* - เสียบกล้องแล้วเช็คด้วย lsusb'}")

sys.exit(0 if ok else 1)
PY
echo "========================================================"
echo "เสร็จแล้ว ใช้งานด้วย: source venv/bin/activate"
