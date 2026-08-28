@echo off
REM Lab 3 - Create YOLO dataset folder structure
cd /d "%~dp0\.."

mkdir dataset\images\train 2>nul
mkdir dataset\images\val 2>nul
mkdir dataset\labels\train 2>nul
mkdir dataset\labels\val 2>nul
mkdir raw_images 2>nul

if not exist dataset\data.yaml (
    > dataset\data.yaml (
        echo path: ../dataset
        echo train: images/train
        echo val: images/val
        echo.
        echo nc: 1
        echo names: ['object']
    )
)

echo Dataset structure created under Lab3_CustomDataset\dataset
pause
