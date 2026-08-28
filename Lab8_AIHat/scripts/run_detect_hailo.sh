#!/bin/bash
# Lab 8 - Run detection accelerated by the AI HAT (Hailo NPU)
cd "$(dirname "$0")/.."
source ../Lab7_RaspberryPi/venv/bin/activate 2>/dev/null || true

MODEL="model/best.hef"
if [ ! -f "$MODEL" ]; then
    echo "model/best.hef not found - run download_sample_hef.sh or compile your own model first."
    exit 1
fi

hailortcli run "$MODEL"
echo "For a full camera pipeline, adapt the hailo-rpi5-examples detection app with this .hef file."
