@echo off
REM Lab 2 - Real-time detection from webcam (device 0)
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

set MODEL=runs\detect\train\weights\best.pt
if not exist "%MODEL%" (
    echo [ERROR] Model not found: %MODEL%
    echo         Run Lab1_TrainReadyDataset\scripts\train.bat first.
    pause
    exit /b 1
)

echo Press q in the video window to stop.
yolo detect predict model=%MODEL% source=0 show=True
pause
