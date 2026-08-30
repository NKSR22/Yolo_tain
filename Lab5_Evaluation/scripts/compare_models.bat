@echo off
REM Lab 5 - Evaluate the 20-image model too, so the two can be compared
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

if not exist "runs\detect\baseline\weights\best.pt" (
    echo [ERROR] runs\detect\baseline\weights\best.pt not found - run Lab 4 first.
    pause
    exit /b 1
)

echo === Model trained on 20 images, measured on the same 225-image val set ===
yolo detect val model=runs\detect\baseline\weights\best.pt data=african-wildlife.yaml name=val_baseline
echo.
echo Compare runs\detect\val_baseline\ against runs\detect\val\
pause
