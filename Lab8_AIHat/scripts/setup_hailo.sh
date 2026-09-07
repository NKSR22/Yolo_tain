#!/bin/bash
# Lab 8 - ติดตั้ง/ตรวจซอฟต์แวร์ของ Hailo AI HAT บน Raspberry Pi OS
set -euo pipefail

echo "[1/3] ตรวจว่า Pi มองเห็นบอร์ด Hailo บน PCIe หรือยัง"
if lspci | grep -qi hailo; then
    lspci | grep -i hailo
else
    echo "  ไม่พบบอร์ด Hailo บน PCIe"
    echo "  - ปิดเครื่องแล้วเช็คสาย FPC ของ HAT ว่าเสียบแน่นและถูกด้าน"
    echo "  - Pi 5 ต้องเปิด PCIe ก่อน: sudo raspi-config -> Advanced -> PCIe Speed"
    exit 1
fi

echo "[2/3] ติดตั้งชุดซอฟต์แวร์ Hailo"
sudo apt-get update
sudo apt-get install -y hailo-all

echo "[3/3] ตรวจการเชื่อมต่อกับตัวชิป"
# ถ้าเพิ่งติดตั้งครั้งแรก ไดรเวอร์ยังไม่ถูกโหลด คำสั่งนี้จะล้มเหลว -> ต้อง reboot ก่อน
if hailortcli fw-control identify; then
    echo
    echo "พร้อมใช้งาน ไปต่อที่ ./download_sample_hef.sh ได้เลย"
else
    echo
    echo "ติดตั้งเสร็จแล้วแต่ยังคุยกับชิปไม่ได้ - ต้องรีบูตก่อน:  sudo reboot"
    echo "รีบูตเสร็จแล้วรันสคริปต์นี้ซ้ำอีกรอบ"
    exit 1
fi
