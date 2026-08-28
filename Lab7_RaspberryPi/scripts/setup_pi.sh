#!/bin/bash
# Lab 7 - Setup environment on Raspberry Pi OS
set -e
cd "$(dirname "$0")/.."

sudo apt update
sudo apt install -y python3-venv python3-pip libopencv-dev

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install ultralytics opencv-python onnxruntime

echo "Setup complete. Activate with: source venv/bin/activate"
