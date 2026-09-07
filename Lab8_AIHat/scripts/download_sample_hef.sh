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
    echo "ไม่พบ $ZOO - ยังไม่ได้ติดตั้ง hailo-all ให้รัน ./setup_hailo.sh ก่อน"
    exit 1
fi

# Hailo-8 กับ Hailo-8L ใช้ไฟล์ .hef คนละตัว ใส่ผิดจะรันไม่ขึ้น
ARCH=$(hailortcli fw-control identify | awk -F': *' '/Device Architecture/{print $2}' | tr -d ' ')
echo "ชิปที่ตรวจพบ: $ARCH"
case "$ARCH" in
    HAILO8)  SUFFIX=h8  ;;
    HAILO8L) SUFFIX=h8l ;;
    *) echo "ไม่รู้จักสถาปัตยกรรม '$ARCH'"; exit 1 ;;
esac

copied=0
for name in yolov6n yolov8s; do
    src="$ZOO/${name}_${SUFFIX}.hef"
    if [ -f "$src" ]; then
        cp -f "$src" "model/${name}.hef"
        printf "  คัดลอกแล้ว  model/%-12s (%s MB)\n" "${name}.hef" \
               "$(du -m "$src" | cut -f1)"
        copied=$((copied + 1))
    fi
done

if [ "$copied" -eq 0 ]; then
    echo "ไม่พบไฟล์ .hef ที่ตรงกับ $ARCH ใน $ZOO"
    echo "ดูรายการที่มี:  ls $ZOO"
    exit 1
fi

echo
echo "เสร็จแล้ว รันวัดความเร็วต่อด้วย: ./run_detect_hailo.sh"
