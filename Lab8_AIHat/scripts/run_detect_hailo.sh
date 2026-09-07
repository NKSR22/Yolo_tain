#!/bin/bash
# Lab 8 - วัดความเร็วโมเดลบนชิป Hailo แล้วพิมพ์ผลในรูปแบบเดียวกับ Lab 7
# ใช้:  ./run_detect_hailo.sh [ชื่อโมเดล]      เช่น  ./run_detect_hailo.sh yolov8s
set -euo pipefail
cd "$(dirname "$0")/.."

NAME="${1:-yolov6n}"
MODEL="model/${NAME}.hef"
if [ ! -f "$MODEL" ]; then
    echo "ไม่พบ $MODEL - รัน ./download_sample_hef.sh ก่อน"
    echo "โมเดลที่มีอยู่ตอนนี้:"
    ls model/*.hef 2>/dev/null || echo "  (ยังไม่มีเลย)"
    exit 1
fi

echo "กำลังวัดความเร็ว $MODEL บนชิป Hailo (ใช้เวลาประมาณ 30 วินาที)"
echo
LOG=$(mktemp)
trap 'rm -f "$LOG"' EXIT
hailortcli benchmark "$MODEL" > "$LOG" 2>&1 || { cat "$LOG"; exit 1; }

# ดึงเฉพาะตัวเลขสรุปออกมา (ตัวเต็มมี progress bar รกจอ)
FPS=$(awk -F'= *' '/FPS +\(hw_only\)/{print $2}' "$LOG")
LAT=$(awk -F'= *' '/Latency +\(hw\)/{print $2}' "$LOG" | awk '{print $1}')

printf '====================================================\n'
printf '  โมเดล            : %s\n' "$NAME"
printf '  latency ของชิป   : %7.2f ms   <-- จดตัวนี้ไปใช้ใน compare_speed.py\n' "$LAT"
printf '  FPS (เฉพาะชิป)   : %7.1f\n' "$FPS"
printf '====================================================\n'
echo
echo "หมายเหตุ: ตัวเลขนี้คือเวลาที่ใช้ในชิปอย่างเดียว ยังไม่รวมเวลาอ่านภาพจากกล้อง"
echo "และวาดผลลงจอ ซึ่งยังทำบน CPU อยู่ ระบบจริงจึงได้ FPS ต่ำกว่านี้"
