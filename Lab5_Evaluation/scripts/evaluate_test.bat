@echo off
REM Lab 5 - Evaluate on the test split: images the model never saw during training
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

set MODEL=runs\detect\full\weights\best.pt
if not exist "%MODEL%" (
    echo [ERROR] Model not found: %MODEL%
    echo         Run Lab4_TrainTuning\scripts\train_full.bat first.
    pause
    exit /b 1
)

yolo detect val model=%MODEL% data=african-wildlife.yaml split=test name=val_test
echo.
echo Done. Results in runs\detect\val_test\
pause
