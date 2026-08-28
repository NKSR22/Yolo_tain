#!/bin/bash
# Lab 7 - Real-time detection on Raspberry Pi using the exported ONNX model
cd "$(dirname "$0")/.."
source venv/bin/activate

MODEL="model/best.onnx"
if [ ! -f "$MODEL" ]; then
    echo "Model not found at $MODEL - copy best.onnx from Lab 6 first."
    exit 1
fi

yolo detect predict model="$MODEL" source=0 show=True imgsz=320
