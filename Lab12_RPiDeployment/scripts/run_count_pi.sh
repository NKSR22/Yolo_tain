#!/bin/bash
# Lab 12 - Count objects per class on the conveyor, on the Raspberry Pi
# Usage:  ~/Lab12_RPiDeployment/scripts/run_count_pi.sh [camera-index-or-video] [extra options]
#         ~/Lab12_RPiDeployment/scripts/run_count_pi.sh 0 --line 0.4 --conf 0.5
#
# Uses the Python environment built in Lab 7 (ultralytics + onnxruntime, CPU torch).
# Output is ASCII only: OpenCV cannot draw Thai and SSH consoles often show '?'.
set -euo pipefail
cd "$(dirname "$0")/.."

VENV="$HOME/Lab7_RaspberryPi/venv"
if [ ! -x "$VENV/bin/python" ]; then
    echo "Python environment not found at $VENV"
    echo "Do Lab 7 first:  cd ~/Lab7_RaspberryPi/scripts && ./setup_pi.sh"
    exit 1
fi
if [ ! -f best.onnx ]; then
    echo "best.onnx not found in $(pwd)"
    echo "Copy it from Windows: .\Lab12_RPiDeployment\scripts\copy_to_pi.bat <user>@<pi>"
    exit 1
fi

SOURCE="${1:-0}"
shift || true
if [[ "$SOURCE" =~ ^[0-9]+$ ]] && [ ! -e "/dev/video$SOURCE" ]; then
    echo "No camera at /dev/video$SOURCE - plug in the USB camera, then check: lsusb"
    exit 1
fi

# Over plain SSH there is no screen to open a window on; count in the terminal only.
SHOW=()
if [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; then
    echo "No display (SSH session?) - counting without a window. Stop with Ctrl+C."
    SHOW=(--no-show)
fi

exec "$VENV/bin/python" scripts/conveyor_count.py --model best.onnx --source "$SOURCE" \
    --log "counts_$(date +%Y%m%d_%H%M%S).csv" "${SHOW[@]}" "$@"
