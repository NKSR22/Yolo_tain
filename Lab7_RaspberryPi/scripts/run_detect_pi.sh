#!/bin/bash
# Lab 7 - ตรวจจับวัตถุแบบ real-time บน Raspberry Pi ด้วยโมเดล ONNX จาก Lab 6
# ต้องรันบนหน้าจอที่ต่อกับ Pi โดยตรง (ผ่าน SSH เปล่า ๆ จะเปิดหน้าต่างไม่ได้)
#
# ข้อความที่ echo ออกจอเป็น ASCII ทั้งหมดตามธรรมเนียมของรีโปนี้
# console ที่ไม่ใช่ codepage ไทยจะแสดงภาษาไทยเป็น ? และตัวเรนเดอร์ภาพประกอบ
# (docs/shoot.py) ก็วาดสระ/วรรณยุกต์ไทยไม่ได้
set -euo pipefail
cd "$(dirname "$0")/.."

MODEL="${1:-model/best.onnx}"
if [ ! -f "$MODEL" ]; then
    echo "Model not found at $MODEL"
    echo "Copy it from Windows first with Lab7_RaspberryPi\scripts\copy_to_pi.bat"
    exit 1
fi

if [ ! -e /dev/video0 ]; then
    echo "No camera at /dev/video0"
    echo "  - plug in a USB camera, then check:  lsusb"
    echo "  - for a Pi Camera check instead:     rpicam-hello --list-cameras"
    exit 1
fi

# ห้ามใส่ imgsz เอง: ไฟล์ ONNX จาก Lab 6 ถูก export มาเป็นขนาดตายตัว
# ถ้าสั่งขนาดอื่น onnxruntime จะปฏิเสธด้วย
#   INVALID_ARGUMENT : Got invalid dimensions for input: images
# ถ้าอยากได้ขนาดเล็กลงเพื่อความเร็ว ต้องกลับไป export ใหม่ที่ Lab 6
./venv/bin/yolo detect predict model="$MODEL" source=0 show=True
