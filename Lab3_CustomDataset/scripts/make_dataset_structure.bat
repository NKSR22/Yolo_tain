@echo off
REM Lab 3 - Create YOLO dataset folder structure
cd /d "%~dp0\.."

mkdir dataset\images\train 2>nul
mkdir dataset\images\val 2>nul
mkdir dataset\labels\train 2>nul
mkdir dataset\labels\val 2>nul
mkdir raw_images 2>nul

REM classes.txt = 1 class per line. labelImg reads it, and split_dataset.py
REM turns it into the nc/names fields of data.yaml.
if not exist raw_images\classes.txt (
    > raw_images\classes.txt echo object
)

REM NOTE: no "path:" key on purpose - Ultralytics resolves a relative path:
REM against its global datasets_dir, not against this file. Without it, train/val
REM are resolved relative to data.yaml itself, which is what we want.
if not exist dataset\data.yaml (
    > dataset\data.yaml (
        echo train: images/train
        echo val: images/val
        echo.
        echo nc: 1
        echo names: ['object']
    )
)

echo Dataset structure created under Lab3_CustomDataset\dataset
echo Images to label go in Lab3_CustomDataset\raw_images
echo (run get_practice_images.bat first, or drop your own photos there)
pause
