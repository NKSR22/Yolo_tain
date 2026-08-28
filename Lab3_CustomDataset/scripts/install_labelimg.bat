@echo off
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat
pip install labelImg
echo labelImg installed.
pause
