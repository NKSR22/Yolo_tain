#!/bin/bash
# Lab 7 - ตรวจจับวัตถุแบบ real-time บน Raspberry Pi ด้วยโมเดล ONNX จาก Lab 6
# ต้องรันบนหน้าจอที่ต่อกับ Pi โดยตรง (ผ่าน SSH เปล่า ๆ จะเปิดหน้าต่างไม่ได้)
set -euo pipefail
cd "$(dirname "$0")/.."

MODEL="${1:-model/best.onnx}"
if [ ! -f "$MODEL" ]; then
    echo "ไม่พบโมเดลที่ $MODEL"
    echo "คัดลอกมาจากเครื่อง Windows ด้วย Lab7_RaspberryPi\scripts\copy_to_pi.bat ก่อน"
    exit 1
fi

if [ ! -e /dev/video0 ]; then
    echo "ไม่พบกล้องที่ /dev/video0"
    echo "  - เสียบกล้อง USB แล้วเช็คด้วย:  lsusb"
    echo "  - ถ้าใช้ Pi Camera ให้เช็คด้วย:   rpicam-hello --list-cameras"
    exit 1
fi

# ห้ามใส่ imgsz เอง: ไฟล์ ONNX จาก Lab 6 ถูก export มาเป็นขนาดตายตัว
# ถ้าสั่งขนาดอื่น onnxruntime จะปฏิเสธด้วย
#   INVALID_ARGUMENT : Got invalid dimensions for input: images
# ถ้าอยากได้ขนาดเล็กลงเพื่อความเร็ว ต้องกลับไป export ใหม่ที่ Lab 6
./venv/bin/yolo detect predict model="$MODEL" source=0 show=True
