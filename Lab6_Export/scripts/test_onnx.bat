@echo off
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

yolo detect predict model=runs\detect\full\weights\best.onnx source=Lab2_Inference\samples\test.jpg name=test_onnx save=True
pause
