@echo off
REM Lab 7 - Copy the Lab 6 model and the Lab 7 scripts over to the Raspberry Pi
REM Usage:  .\copy_to_pi.bat admin@mIoT.local
setlocal
cd /d "%~dp0\..\.."

if "%~1"=="" (
    echo Usage:   .\copy_to_pi.bat ^<user^>@^<pi-hostname-or-ip^>
    echo Example: .\copy_to_pi.bat admin@mIoT.local
    echo.
    echo Run "hostname -I" on the Pi to find its address.
    pause
    exit /b 1
)
set TARGET=%~1

set MODEL=runs\detect\full\weights\best.onnx
if not exist "%MODEL%" (
    echo [ERROR] %MODEL% not found.
    echo Run Lab6_Export\scripts\export_onnx.bat first.
    pause
    exit /b 1
)

echo [1/3] Creating target folders on the Pi
ssh %TARGET% "mkdir -p ~/Lab7_RaspberryPi/model ~/Lab7_RaspberryPi/scripts"
if errorlevel 1 goto :sshfail

echo [2/3] Copying %MODEL%
scp "%MODEL%" %TARGET%:~/Lab7_RaspberryPi/model/best.onnx
if errorlevel 1 goto :sshfail

echo [3/3] Copying the Lab 7 scripts
scp Lab7_RaspberryPi\scripts\setup_pi.sh Lab7_RaspberryPi\scripts\run_detect_pi.sh Lab7_RaspberryPi\scripts\fps_test.py %TARGET%:~/Lab7_RaspberryPi/scripts/
if errorlevel 1 goto :sshfail

echo.
echo Done. Now SSH into the Pi and run:
echo     cd ~/Lab7_RaspberryPi/scripts
echo     chmod +x *.sh
echo     ./setup_pi.sh
pause
exit /b 0

:sshfail
echo.
echo [ERROR] Could not reach the Pi. Check that:
echo   - the Pi is powered on and on the same network as this PC
echo   - SSH is enabled on the Pi (sudo raspi-config ^> Interface Options ^> SSH)
echo   - your SSH key is installed, or you know the password
pause
exit /b 1
