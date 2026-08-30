@echo off
REM Lab 3 - Score your labelling against the hidden answer key
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat
python "%~dp0compare_labels.py" %*
pause
