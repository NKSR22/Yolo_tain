@echo off
REM Lab 4 - Round 1: train on the ~20 images you labelled yourself in Lab 3
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

set DATA=Lab3_CustomDataset\dataset\data.yaml
if not exist "%DATA%" (
    echo [ERROR] Not found: %DATA%
    echo         Finish Lab 3 first ^(get_practice_images / label / split_dataset^).
    pause
    exit /b 1
)

yolo detect train data=%DATA% model=yolo11n.pt epochs=50 imgsz=640 batch=8 name=baseline
echo.
echo Done. Results in runs\detect\baseline\
pause
