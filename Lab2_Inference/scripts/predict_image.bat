@echo off
REM Lab 2 - Detect objects in an image
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

set MODEL=runs\detect\train\weights\best.pt
if not exist "%MODEL%" (
    echo [ERROR] Model not found: %MODEL%
    echo         Run Lab1_TrainReadyDataset\scripts\train.bat first.
    pause
    exit /b 1
)
if not exist "Lab2_Inference\samples\test.jpg" python "%~dp0get_samples.py"

yolo detect predict model=%MODEL% source=Lab2_Inference\samples\test.jpg name=predict_image save=True
echo.
echo Result saved under runs\detect\predict_image\
pause
