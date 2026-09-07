#!/bin/bash
# Lab 9 - คอมไพล์ firmware แล้วอัปโหลดลง Arduino Uno จากบนตัว Raspberry Pi
#
# ทั้ง build และ upload ทำบน Pi ทั้งหมด ไม่ต้องย้ายไฟล์ไปเครื่อง Windows
# ครั้งแรกจะนานหน่อยเพราะ PlatformIO ต้องโหลด toolchain ของ AVR มาก่อน
set -euo pipefail
cd "$(dirname "$0")/../arduino"

PIO="$HOME/.platformio/penv/bin/pio"
if [ ! -x "$PIO" ]; then
    echo "PlatformIO not found at $PIO"
    echo "Run ./setup_link.sh first"
    exit 1
fi

if [ ! -e /dev/ttyACM0 ]; then
    echo "/dev/ttyACM0 not found - plug in the Arduino Uno first"
    exit 1
fi

# ถ้ามีโปรแกรมอื่นเปิดพอร์ตค้างอยู่ avrdude จะอัปโหลดไม่ได้
# บอกให้ชัดตรงนี้ ดีกว่าปล่อยให้ไปงงกับข้อความของ avrdude
if command -v fuser > /dev/null && fuser /dev/ttyACM0 > /dev/null 2>&1; then
    echo "Something else is holding /dev/ttyACM0:"
    fuser -v /dev/ttyACM0 || true
    echo "Close it (a serial monitor, or a running demo script) and try again."
    exit 1
fi

echo "Building and uploading..."
"$PIO" run --target upload

echo
echo "Done. Test the link with: ../scripts/test_link.py"
