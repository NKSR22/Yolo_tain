@echo off
REM Lab 1 - Train YOLO with a ready-made dataset (COCO8)
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

yolo detect train data=coco8.yaml model=yolo11n.pt epochs=20 imgsz=640 project=Lab1_TrainReadyDataset\runs name=train

echo.
echo Training finished. Check Lab1_TrainReadyDataset\runs\train\weights\best.pt
pause
