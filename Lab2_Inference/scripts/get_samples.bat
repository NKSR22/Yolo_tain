@echo off
REM Lab 2 - Prepare sample image / video for the detection scripts
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat
python "%~dp0get_samples.py"
pause
