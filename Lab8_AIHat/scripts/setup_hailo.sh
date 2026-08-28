#!/bin/bash
# Lab 8 - Install Hailo software suite for AI HAT on Raspberry Pi OS
set -e
sudo apt update
sudo apt install -y hailo-all
echo "Reboot required. Run: sudo reboot"
echo "After reboot, verify with: hailortcli fw-control identify"
