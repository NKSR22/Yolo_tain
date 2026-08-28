@echo off
REM Lab 4 - Baseline training with custom dataset from Lab 3
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

yolo detect train data=Lab3_CustomDataset\dataset\data.yaml model=yolo11n.pt epochs=50 imgsz=640 project=Lab4_TrainTuning\runs name=baseline
pause
