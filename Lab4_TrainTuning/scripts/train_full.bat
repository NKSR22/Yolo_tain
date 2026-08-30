@echo off
REM Lab 4 - Round 2: same 4 classes, but the full dataset (~1,050 images)
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

REM african-wildlife.yaml is built into Ultralytics - it downloads on first use (~100 MB)
yolo detect train data=african-wildlife.yaml model=yolo11n.pt epochs=50 imgsz=640 batch=8 name=full
echo.
echo Done. Results in runs\detect\full\
echo Compare it against round 1 with compare_runs.bat
pause
