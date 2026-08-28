@echo off
REM ==============================================
REM Lab 0 - Environment Setup (Windows)
REM สร้าง venv + ติดตั้ง PyTorch/CUDA + Ultralytics YOLO
REM ==============================================
cd /d "%~dp0\..\.."

echo [1/4] Creating virtual environment (venv) ...
python -m venv venv
if errorlevel 1 (
    echo ERROR: ไม่พบ python กรุณาติดตั้ง Python และเลือก "Add to PATH"
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo [2/4] Upgrading pip ...
python -m pip install --upgrade pip

echo [3/4] Detecting NVIDIA GPU ...
nvidia-smi >nul 2>&1
if %errorlevel%==0 (
    echo GPU found - installing PyTorch with CUDA 12.1 support
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
) else (
    echo No NVIDIA GPU detected - installing CPU-only PyTorch
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
)

echo [4/4] Installing Ultralytics YOLO ...
pip install ultralytics opencv-python

echo.
echo ================= Verifying environment =================
python "%~dp0check_env.py"

echo.
echo Setup complete. Use "venv\Scripts\activate" to start working.
pause
