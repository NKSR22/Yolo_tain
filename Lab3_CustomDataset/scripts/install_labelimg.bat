@echo off
REM Lab 3 - Install labelImg and patch it for modern PyQt5
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

pip install labelImg
if errorlevel 1 (
    echo.
    echo [ERROR] pip install failed. Use Roboflow ^(roboflow.com^) in the browser instead - see the manual.
    pause
    exit /b 1
)

python "%~dp0patch_labelimg.py"
echo.
echo labelImg installed. Run run_labelimg.bat to start labelling.
pause
