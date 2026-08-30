@echo off
REM Lab 3 - Fetch practice images (answer key is hidden in answer_key\)
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat
python "%~dp0get_practice_images.py"
pause
