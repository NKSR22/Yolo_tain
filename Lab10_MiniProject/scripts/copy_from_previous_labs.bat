@echo off
cd /d "%~dp0\.."
mkdir model 2>nul
copy /Y ..\Lab4_TrainTuning\runs\exp\weights\best.pt model\ >nul 2>nul
copy /Y ..\Lab4_TrainTuning\runs\exp\weights\best.onnx model\ >nul 2>nul
echo Copied latest model weights into Lab10_MiniProject\model\
pause
