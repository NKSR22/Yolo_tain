@echo off
REM Lab 4 - Tabulate the results of every training run side by side
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat
python "%~dp0compare_runs.py" %*
pause
