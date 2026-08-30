@echo off
REM Lab 5 - Collect the evaluation outputs into report\
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat
python "%~dp0export_report.py" %*
pause
