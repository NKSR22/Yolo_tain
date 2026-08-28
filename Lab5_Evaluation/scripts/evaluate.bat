@echo off
REM Lab 5 - Evaluate a trained model
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

yolo detect val model=Lab4_TrainTuning\runs\exp\weights\best.pt data=Lab3_CustomDataset\dataset\data.yaml project=Lab5_Evaluation\runs name=val
pause
