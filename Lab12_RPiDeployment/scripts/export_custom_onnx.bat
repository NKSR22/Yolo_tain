@echo off
setlocal
cd /d "%~dp0\..\.."

set "MODEL=Lab12_RPiDeployment\best.pt"
if not exist "%MODEL%" (
    echo [ERROR] Model not found: %MODEL%
    echo         Copy best.pt from Lab 11 first.
    exit /b 1
)
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Project venv not found. Run Lab0_Setup\scripts\setup_env.bat first.
    exit /b 1
)
call venv\Scripts\activate.bat

yolo export "model=%MODEL%" format=onnx imgsz=640 simplify=True
if errorlevel 1 exit /b 1
if not exist "Lab12_RPiDeployment\best.onnx" (
    echo [ERROR] ONNX export did not create best.onnx.
    exit /b 1
)
echo Export complete: Lab12_RPiDeployment\best.onnx
pause
