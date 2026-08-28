@echo off
REM Lab 1 - Train YOLO with a ready-made dataset (COCO8)
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

yolo detect train data=coco8.yaml model=yolo11n.pt epochs=20 imgsz=640

echo.
echo Training finished. Check runs\detect\train\weights\best.pt
pause
