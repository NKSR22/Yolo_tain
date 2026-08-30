@echo off
REM Lab 3 - Label the photos in raw_images (YOLO .txt files land next to them)
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

set RAW=Lab3_CustomDataset\raw_images
if not exist "%RAW%" (
    echo [ERROR] %RAW% not found. Run make_dataset_structure.bat first.
    pause
    exit /b 1
)

REM args: image_dir  class_file  save_dir
labelImg "%RAW%" "%RAW%\classes.txt" "%RAW%"
