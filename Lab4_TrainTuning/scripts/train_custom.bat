@echo off
REM Lab 4 - Train with configurable hyperparameters
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

if "%EPOCHS%"=="" set EPOCHS=50
if "%IMGSZ%"=="" set IMGSZ=640
if "%MODEL%"=="" set MODEL=yolo11n.pt
if "%BATCH%"=="" set BATCH=16

echo Training with model=%MODEL% epochs=%EPOCHS% imgsz=%IMGSZ% batch=%BATCH%
yolo detect train data=Lab3_CustomDataset\dataset\data.yaml model=%MODEL% epochs=%EPOCHS% imgsz=%IMGSZ% batch=%BATCH% project=Lab4_TrainTuning\runs name=exp
pause
