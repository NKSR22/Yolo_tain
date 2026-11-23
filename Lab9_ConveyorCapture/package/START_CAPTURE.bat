@echo off
REM Conveyor Image Capture - double-click to start.
REM First run creates .venv next to this file and installs opencv-python + Pillow.
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" goto :install

echo ============================================================
echo  First run: setting up (needs internet, about 1-3 minutes)
echo ============================================================
REM A Python counts only if it is 3.9+ AND can really open a Tk window.
REM "import tkinter" alone is not enough: a half-installed Python imports it
REM fine and then fails with "Can't find a usable init.tcl".
set "PY="
call :try py -3
if not defined PY call :try python
if not defined PY call :try py
if not defined PY (
    echo [ERROR] No working Python 3.9+ with tcl/tk was found.
    echo         Install Python from https://www.python.org/downloads/
    echo         and tick "Add python.exe to PATH". See Manual.html, step 1.
    pause
    exit /b 1
)
echo Using: %PY%
%PY% -m venv .venv
if errorlevel 1 goto :venvfail
".venv\Scripts\python.exe" -c "import tkinter; tkinter.Tk().destroy()" >nul 2>&1
if errorlevel 1 goto :venvfail

:install
if exist ".venv\installed.ok" goto :run
echo Installing opencv-python and Pillow ...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r app\requirements.txt
if errorlevel 1 (
    echo [ERROR] Installation failed. Check the internet connection and run again.
    pause
    exit /b 1
)
echo ok> ".venv\installed.ok"

:run
echo Starting Conveyor Image Capture ...
".venv\Scripts\python.exe" app\capture_gui.py
if errorlevel 1 (
    echo.
    echo [ERROR] The program stopped with an error, shown above.
    echo         If it mentions tcl, tk or init.tcl: delete the .venv folder and run again.
    pause
)
exit /b 0

:venvfail
echo [ERROR] Could not create a working Python environment in:
echo         %CD%
echo         Move the ConveyorCapture folder to C:\ConveyorCapture and run again.
if exist ".venv" rmdir /s /q ".venv"
pause
exit /b 1

:try
%* -c "import sys, tkinter; sys.exit(1) if sys.version_info < (3, 9) else tkinter.Tk().destroy()" >nul 2>&1
if not errorlevel 1 set "PY=%*"
exit /b 0
