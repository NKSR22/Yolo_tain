@echo off
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

yolo detect predict model=Lab4_TrainTuning\runs\exp\weights\best.onnx source=Lab2_Inference\samples\test.jpg project=Lab6_Export\runs name=test_onnx save=True
pause
