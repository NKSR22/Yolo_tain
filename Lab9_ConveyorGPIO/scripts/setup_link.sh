#!/bin/bash
# Lab 9 - เตรียมเครื่อง Raspberry Pi ให้โปรแกรม Arduino และคุยกับมันได้
#
# แล็บนี้ไม่ได้ใช้ขา GPIO ของ Pi แล้ว เพราะ AI HAT ของ Lab 8 เสียบทับหัว GPIO ไป
# งานคุมมอเตอร์/เซ็นเซอร์เลยย้ายไปอยู่บน Arduino Uno ที่ต่อผ่านสาย USB
#
# ข้อความที่ echo ออกจอเป็น ASCII ทั้งหมดตามธรรมเนียมของรีโปนี้
set -euo pipefail
cd "$(dirname "$0")/.."

VENV=../Lab7_RaspberryPi/venv
PIO="$HOME/.platformio/penv/bin/pio"

echo "[1/4] Checking that the Arduino is plugged in"
if [ -e /dev/ttyACM0 ]; then
    ls -l /dev/ttyACM0
    lsusb | grep -i arduino || true
else
    echo "  /dev/ttyACM0 not found"
    echo "  - plug the Arduino Uno into a USB port on the Pi"
    echo "  - then check with: lsusb"
    exit 1
fi

echo "[2/4] Checking serial port permissions"
# ต้องอยู่ในกลุ่ม dialout ถึงจะเปิดพอร์ตได้โดยไม่ต้อง sudo
if groups | tr ' ' '\n' | grep -qx dialout; then
    echo "  OK: this user is in the dialout group"
else
    echo "  Adding this user to the dialout group"
    sudo usermod -aG dialout "$USER"
    echo "  Log out and back in for it to take effect, then run this script again"
    exit 1
fi

echo "[3/4] Installing PlatformIO if needed"
if [ -x "$PIO" ]; then
    echo "  OK: $("$PIO" --version)"
else
    # ตัวติดตั้งทางการสร้าง venv ของตัวเองที่ ~/.platformio/penv
    # จึงไม่ชนกับกฎ PEP 668 ของ Raspberry Pi OS ที่ห้ามลงแพ็กเกจลงระบบตรง ๆ
    curl -fsSL -o /tmp/get-platformio.py \
        https://raw.githubusercontent.com/platformio/platformio-core-installer/master/get-platformio.py
    python3 /tmp/get-platformio.py
    echo "  Installed: $("$PIO" --version)"
fi

echo "[4/4] Installing pyserial into the Lab 7 venv"
if [ ! -d "$VENV" ]; then
    echo "  Lab 7 venv not found at $VENV"
    echo "  Go back and run Lab7_RaspberryPi/scripts/setup_pi.sh first"
    exit 1
fi
"$VENV/bin/pip" install --quiet pyserial
"$VENV/bin/python" -c "import serial; print('  OK: pyserial', serial.__version__)"

echo
echo "Ready. Next upload the firmware with: ./upload_arduino.sh"
