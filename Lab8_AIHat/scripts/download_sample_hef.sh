#!/bin/bash
# Lab 8 - Fetch a sample compiled Hailo model (.hef) for object detection
cd "$(dirname "$0")/.."
mkdir -p model
echo "Download a YOLO .hef sample from the Hailo Model Zoo and place it at model/best.hef"
echo "Reference: https://github.com/hailo-ai/hailo_model_zoo"
