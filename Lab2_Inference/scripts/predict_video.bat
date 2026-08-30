@echo off
REM Lab 2 - Detect objects in a video file
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

set MODEL=runs\detect\train\weights\best.pt
if not exist "%MODEL%" (
    echo [ERROR] Model not found: %MODEL%
    echo         Run Lab1_TrainReadyDataset\scripts\train.bat first.
    pause
    exit /b 1
)
if not exist "Lab2_Inference\samples\test.mp4" python "%~dp0get_samples.py"

yolo detect predict model=%MODEL% source=Lab2_Inference\samples\test.mp4 name=predict_video save=True
echo.
echo Result saved under runs\detect\predict_video\
pause
