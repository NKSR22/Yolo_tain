#!/bin/bash
# Lab 8 - วัดความเร็วโมเดลบนชิป Hailo แล้วพิมพ์ผลในรูปแบบเดียวกับ Lab 7
# ใช้:  ./run_detect_hailo.sh [ชื่อโมเดล]      เช่น  ./run_detect_hailo.sh yolov8s
set -euo pipefail
cd "$(dirname "$0")/.."

NAME="${1:-yolov6n}"
MODEL="model/${NAME}.hef"
if [ ! -f "$MODEL" ]; then
    echo "$MODEL not found - run ./download_sample_hef.sh first"
    echo "Models available right now:"
    ls model/*.hef 2>/dev/null || echo "  (none yet)"
    exit 1
fi

echo "Measuring $MODEL on the Hailo chip (takes about 30 seconds)"
echo
LOG=$(mktemp)
trap 'rm -f "$LOG"' EXIT
hailortcli benchmark "$MODEL" > "$LOG" 2>&1 || { cat "$LOG"; exit 1; }

# ดึงเฉพาะตัวเลขสรุปออกมา (ตัวเต็มมี progress bar รกจอ)
FPS=$(awk -F'= *' '/FPS +\(hw_only\)/{print $2}' "$LOG")
LAT=$(awk -F'= *' '/Latency +\(hw\)/{print $2}' "$LOG" | awk '{print $1}')

printf '====================================================\n'
printf '  model             : %s\n' "$NAME"
printf '  chip latency      : %7.2f ms   <-- note this for compare_speed.py\n' "$LAT"
printf '  FPS (chip only)   : %7.1f\n' "$FPS"
printf '====================================================\n'
echo
echo "Note: this is time inside the chip only. Reading frames from the camera"
echo "and drawing results still run on the CPU, so a real system gets fewer FPS."
