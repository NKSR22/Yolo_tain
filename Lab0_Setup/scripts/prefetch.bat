@echo off
REM Lab 0 - Download everything the course needs. Run this at home before class.
cd /d "%~dp0\..\.."
if not exist venv\Scripts\activate.bat (
    echo [ERROR] venv not found. Run setup_env.bat first.
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
python "%~dp0prefetch.py"
pause
