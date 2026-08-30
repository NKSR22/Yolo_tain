@echo off
cd /d "%~dp0\.."
mkdir model 2>nul
set SRC=..\runs\detect\full\weights
if not exist "%SRC%\best.pt" (
    echo [ERROR] Not found: %SRC%\best.pt
    echo         Run Lab4_TrainTuning\scripts\train_full.bat first.
    pause
    exit /b 1
)
copy /Y "%SRC%\best.pt" model\ >nul
if exist "%SRC%\best.onnx" (
    copy /Y "%SRC%\best.onnx" model\ >nul
) else (
    echo [WARN] best.onnx not found - run Lab6_Export\scripts\export_onnx.bat if you need it
)
echo Copied model weights into Lab10_MiniProject\model\
pause
