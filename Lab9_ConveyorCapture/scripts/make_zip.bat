@echo off
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Project venv not found. Run Lab 0 setup first.
    pause
    exit /b 1
)
python Lab9_ConveyorCapture\scripts\make_zip.py
pause
