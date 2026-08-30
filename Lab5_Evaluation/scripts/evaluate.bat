@echo off
REM Lab 5 - Evaluate the model trained in Lab 4 on the validation split
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

set MODEL=runs\detect\full\weights\best.pt
if not exist "%MODEL%" (
    echo [ERROR] Model not found: %MODEL%
    echo         Run Lab4_TrainTuning\scripts\train_full.bat first.
    pause
    exit /b 1
)

yolo detect val model=%MODEL% data=african-wildlife.yaml name=val
echo.
echo Done. Results in runs\detect\val\
pause
