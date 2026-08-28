@echo off
REM Lab 2 - Real-time detection from webcam (device 0)
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

yolo detect predict model=Lab1_TrainReadyDataset\runs\train\weights\best.pt source=0 show=True
pause
