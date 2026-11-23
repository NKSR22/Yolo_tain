@echo off
REM Pack captured_images\<class>\*.jpg into conveyor_images.zip
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Run START_CAPTURE.bat first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" app\make_zip.py
pause
