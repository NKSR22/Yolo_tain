#!/bin/bash
# Lab 8 - ติดตั้ง/ตรวจซอฟต์แวร์ของ Hailo AI HAT บน Raspberry Pi OS
set -euo pipefail

echo "[1/3] Checking that the Pi can see the Hailo board on PCIe"
if lspci | grep -qi hailo; then
    lspci | grep -i hailo
else
    echo "  No Hailo board found on PCIe"
    echo "  - power off and check the HAT FPC cable is seated the right way round"
    echo "  - on a Pi 5 enable PCIe first: sudo raspi-config -> Advanced -> PCIe Speed"
    exit 1
fi

echo "[2/3] Installing the Hailo software stack"
sudo apt-get update
sudo apt-get install -y hailo-all

echo "[3/3] Talking to the chip"
# ถ้าเพิ่งติดตั้งครั้งแรก ไดรเวอร์ยังไม่ถูกโหลด คำสั่งนี้จะล้มเหลว -> ต้อง reboot ก่อน
if hailortcli fw-control identify; then
    echo
    echo "Ready. Next run ./download_sample_hef.sh"
else
    echo
    echo "Installed, but cannot reach the chip yet - reboot first:  sudo reboot"
    echo "After the reboot, run this script again"
    exit 1
fi
