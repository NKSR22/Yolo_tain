@echo off
REM Lab 12 - Rehearse the conveyor counter on Windows with the same ONNX file the Pi will use
REM Usage: .\Lab12_RPiDeployment\scripts\run_count.bat [camera-index-or-video] [extra options]
REM   .\Lab12_RPiDeployment\scripts\run_count.bat 0
REM   .\Lab12_RPiDeployment\scripts\run_count.bat "C:\data\belt clip.mp4" --line 0.4
setlocal
cd /d "%~dp0\..\.."

set "MODEL=Lab12_RPiDeployment\best.onnx"
if not exist "%MODEL%" (
    echo [ERROR] Model not found: %MODEL%
    echo         Run export_custom_onnx.bat first.
    exit /b 1
)
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Project venv not found. Run Lab0_Setup\scripts\setup_env.bat first.
    exit /b 1
)
call venv\Scripts\activate.bat

set "SOURCE=%~1"
if "%SOURCE%"=="" set "SOURCE=0"
python Lab12_RPiDeployment\scripts\conveyor_count.py --model "%MODEL%" --source "%SOURCE%" --log Lab12_RPiDeployment\counts_windows.csv %2 %3 %4 %5 %6 %7 %8
