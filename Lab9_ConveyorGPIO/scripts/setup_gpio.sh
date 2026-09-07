#!/bin/bash
# Lab 9 - เตรียมไลบรารี GPIO สำหรับ Raspberry Pi 5
#
# ทำไมไม่ใช้ `pip install RPi.GPIO`:
# Pi 5 เปลี่ยนไปใช้ชิป RP1 คุม GPIO ไลบรารี RPi.GPIO ตัวเดิมอ่านที่อยู่ฮาร์ดแวร์
# แบบเก่าไม่เจอ จะพังตอนสร้างอุปกรณ์ด้วย
#     RuntimeError: Cannot determine SOC peripheral base address
# ของที่ใช้ได้บน Pi 5 คือ lgpio ซึ่ง Raspberry Pi OS ลงมาให้แล้วผ่าน apt
# (ลง lgpio ผ่าน pip ไม่ได้ตรง ๆ เพราะต้องคอมไพล์และต้องมี swig)
# ทางที่ง่ายและนิ่งที่สุดคือสร้าง venv แบบมองเห็นแพ็กเกจของระบบ
set -euo pipefail
cd "$(dirname "$0")/.."

VENV=../Lab7_RaspberryPi/venv

echo "[1/3] ติดตั้งไลบรารี GPIO จาก apt"
sudo apt-get update
sudo apt-get install -y python3-gpiozero python3-lgpio

echo "[2/3] เปิดให้ venv ของ Lab 7 มองเห็นแพ็กเกจของระบบ"
if [ ! -d "$VENV" ]; then
    echo "  ไม่พบ venv ของ Lab 7 ที่ $VENV"
    echo "  ให้กลับไปรัน Lab7_RaspberryPi/scripts/setup_pi.sh ก่อน"
    exit 1
fi
# venv ที่ Lab 7 สร้างไว้ถูกปิดกั้นจากแพ็กเกจของระบบ เปิดสวิตช์ใน pyvenv.cfg
# ได้เลย ไม่ต้องสร้าง venv ใหม่ (ไม่ต้องลง torch/ultralytics ซ้ำ)
sed -i 's/^include-system-site-packages *=.*/include-system-site-packages = true/' \
    "$VENV/pyvenv.cfg"
grep '^include-system-site-packages' "$VENV/pyvenv.cfg"

echo "[3/3] ตรวจว่า gpiozero จับ backend ได้ถูกตัว"
"$VENV/bin/python" - <<'PY'
from gpiozero import Device
Device.ensure_pin_factory()
name = type(Device.pin_factory).__name__
print(f"  pin factory ที่ใช้: {name}")
if name != "LGPIOFactory":
    raise SystemExit(
        f"  คาดว่าจะได้ LGPIOFactory แต่ได้ {name}\n"
        "  ถ้ามี RPi.GPIO ค้างอยู่ใน venv ให้ถอนออกก่อน: pip uninstall RPi.GPIO"
    )
print("  พร้อมใช้งาน GPIO แล้ว")
PY
