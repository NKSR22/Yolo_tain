#!/bin/bash
# Lab 8 - เตรียมโมเดล .hef ที่คอมไพล์มาแล้วสำหรับ Hailo
#
# ทำไมต้องใช้โมเดลสำเร็จรูป ไม่ใช่ best.pt ของเราเอง:
# ชิป Hailo รันได้เฉพาะไฟล์ .hef ที่คอมไพล์ด้วย Hailo Dataflow Compiler ซึ่งเป็น
# เครื่องมือแยกต่างหาก ทำงานได้บน x86 Linux เท่านั้น คอมไพล์บนตัว Pi ไม่ได้
# (บน Pi มีแค่ HailoRT สำหรับ "รัน" ไม่ใช่ "แปลง")
# Lab นี้จึงวัดความเร็วของตัวชิปด้วยโมเดลมาตรฐาน แล้วเทียบกับ CPU ใน Lab 7
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p model

ZOO=/usr/share/hailo-models
if [ ! -d "$ZOO" ]; then
    echo "$ZOO not found - hailo-all is not installed. Run ./setup_hailo.sh first."
    exit 1
fi

# Hailo-8 กับ Hailo-8L ใช้ไฟล์ .hef คนละตัว ใส่ผิดจะรันไม่ขึ้น
ARCH=$(hailortcli fw-control identify | awk -F': *' '/Device Architecture/{print $2}' | tr -d ' ')
echo "Detected chip: $ARCH"
case "$ARCH" in
    HAILO8)  SUFFIX=h8  ;;
    HAILO8L) SUFFIX=h8l ;;
    *) echo "Unknown architecture '$ARCH'"; exit 1 ;;
esac

copied=0
for name in yolov6n yolov8s; do
    src="$ZOO/${name}_${SUFFIX}.hef"
    if [ -f "$src" ]; then
        cp -f "$src" "model/${name}.hef"
        printf "  copied  model/%-14s (%s MB)\n" "${name}.hef" \
               "$(du -m "$src" | cut -f1)"
        copied=$((copied + 1))
    fi
done

if [ "$copied" -eq 0 ]; then
    echo "No .hef matching $ARCH found in $ZOO"
    echo "See what is available:  ls $ZOO"
    exit 1
fi

echo
echo "Done. Measure the speed next with: ./run_detect_hailo.sh"
