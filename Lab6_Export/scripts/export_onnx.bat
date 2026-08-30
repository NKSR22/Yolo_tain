@echo off
REM Lab 6 - Export trained model to ONNX
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

yolo export model=runs\detect\full\weights\best.pt format=onnx imgsz=640 simplify=True
echo.
echo ONNX file created next to best.pt (best.onnx)
pause
