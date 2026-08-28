@echo off
REM Lab 2 - Detect objects in a video file
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

yolo detect predict model=Lab1_TrainReadyDataset\runs\train\weights\best.pt source=Lab2_Inference\samples\test.mp4 project=Lab2_Inference\runs name=predict_video save=True
pause
