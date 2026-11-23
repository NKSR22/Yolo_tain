@echo off
REM Lab 12 - Copy the custom ONNX model and the counting scripts to the Raspberry Pi
REM Usage: .\Lab12_RPiDeployment\scripts\copy_to_pi.bat admin@mIoT.local
setlocal
cd /d "%~dp0\..\.."

if "%~1"=="" (
    echo Usage:   .\Lab12_RPiDeployment\scripts\copy_to_pi.bat ^<user^>@^<pi-hostname-or-ip^>
    echo Example: .\Lab12_RPiDeployment\scripts\copy_to_pi.bat admin@mIoT.local
    echo.
    echo Run "hostname -I" on the Pi to find its address.
    exit /b 1
)
set TARGET=%~1
set "MODEL=Lab12_RPiDeployment\best.onnx"
if not exist "%MODEL%" (
    echo [ERROR] %MODEL% not found. Run export_custom_onnx.bat first.
    exit /b 1
)

echo [1/3] Creating ~/Lab12_RPiDeployment on the Pi
ssh %TARGET% "mkdir -p ~/Lab12_RPiDeployment/scripts"
if errorlevel 1 goto :sshfail

echo [2/3] Copying %MODEL%
scp "%MODEL%" %TARGET%:~/Lab12_RPiDeployment/best.onnx
if errorlevel 1 goto :sshfail

echo [3/3] Copying the counting scripts
scp Lab12_RPiDeployment\scripts\conveyor_count.py Lab12_RPiDeployment\scripts\run_count_pi.sh %TARGET%:~/Lab12_RPiDeployment/scripts/
if errorlevel 1 goto :sshfail
REM Windows checkouts may have CRLF line endings; bash refuses "#!/bin/bash\r".
ssh %TARGET% "sed -i 's/\r$//' ~/Lab12_RPiDeployment/scripts/run_count_pi.sh && chmod +x ~/Lab12_RPiDeployment/scripts/run_count_pi.sh"
if errorlevel 1 goto :sshfail

echo.
echo Done. On the Pi desktop, open a terminal and run:
echo     ~/Lab12_RPiDeployment/scripts/run_count_pi.sh
exit /b 0

:sshfail
echo.
echo [ERROR] Could not reach the Pi. Check that:
echo   - the Pi is powered on and on the same network as this PC
echo   - SSH is enabled on the Pi (sudo raspi-config ^> Interface Options ^> SSH)
echo   - your SSH key is installed, or you know the password
exit /b 1
