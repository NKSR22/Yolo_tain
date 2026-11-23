@echo off
setlocal
cd /d "%~dp0\..\.."

set "MODEL=Lab11_WindowsTesting\best.pt"
if not exist "%MODEL%" (
    echo [ERROR] Model not found: %MODEL%
    echo         Download best.pt from the Lab 10 Google Drive output.
    exit /b 1
)
if "%~1"=="" (
    echo Usage: .\Lab11_WindowsTesting\scripts\run_test.bat ^<image-or-video-path ^| camera-index^>
    exit /b 1
)
set "SOURCE=%~1"
REM A bare number is a camera index: show the live view instead of saving files.
set "OUTPUT=save=True"
echo %SOURCE%| findstr /r "^[0-9][0-9]*$" >nul
if not errorlevel 1 (
    set "OUTPUT=show=True"
) else if not exist "%SOURCE%" (
    echo [ERROR] Source not found: %SOURCE%
    exit /b 1
)
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Project venv not found. Run Lab0_Setup\scripts\setup_env.bat first.
    exit /b 1
)
call venv\Scripts\activate.bat

yolo detect predict "model=%MODEL%" "source=%SOURCE%" %OUTPUT% name=lab11_custom_test
if errorlevel 1 exit /b 1
echo.
echo Result saved under runs\detect\lab11_custom_test\
pause
