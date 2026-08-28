@echo off
REM Lab 2 - Detect objects in an image
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat
if not exist "Lab2_Inference\samples" mkdir "Lab2_Inference\samples"

yolo detect predict model=Lab1_TrainReadyDataset\runs\train\weights\best.pt source=Lab2_Inference\samples\test.jpg project=Lab2_Inference\runs name=predict_image save=True
pause
