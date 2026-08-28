#!/bin/bash
# Lab 9 - Install GPIO libraries on Raspberry Pi OS
set -e
cd "$(dirname "$0")/.."
source ../Lab7_RaspberryPi/venv/bin/activate 2>/dev/null || python3 -m venv ../Lab7_RaspberryPi/venv && source ../Lab7_RaspberryPi/venv/bin/activate
pip install gpiozero RPi.GPIO
echo "GPIO libraries installed."
