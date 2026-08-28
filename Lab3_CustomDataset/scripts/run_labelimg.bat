@echo off
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat
labelImg "%~dp0..\dataset\images\train"
