@echo off
REM Lab 6 - Run the exported ONNX model to confirm it still works
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

set MODEL=runs\detect\full\weights\best.onnx
if not exist "%MODEL%" (
    echo [ERROR] %MODEL% not found. Run export_onnx.bat first.
    pause
    exit /b 1
)

REM Use a wildlife image - the model only knows buffalo/elephant/rhino/zebra,
REM so Lab 2's bus photo would correctly return "no detections" and prove nothing.
set SOURCE=Lab3_CustomDataset\raw_images\wild_01.jpg
if not exist "%SOURCE%" (
    echo [ERROR] %SOURCE% not found. Run Lab3_CustomDataset\scripts\get_practice_images.bat first.
    pause
    exit /b 1
)

REM device=cpu is required: onnxruntime (the CPU build) sees the NVIDIA card,
REM tries the CUDA provider and fails on a missing cublas DLL. CPU is also the
REM realistic case - ONNX exists here for Raspberry Pi, which has no GPU.
yolo detect predict model=%MODEL% source=%SOURCE% device=cpu name=test_onnx save=True
echo.
echo Result saved under runs\detect\test_onnx\
pause
