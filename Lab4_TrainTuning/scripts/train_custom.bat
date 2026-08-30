@echo off
REM Lab 4 - Tuning runs. Change the values below, run again, compare.
cd /d "%~dp0\..\.."
call venv\Scripts\activate.bat

if "%DATA%"==""   set DATA=african-wildlife.yaml
if "%MODEL%"==""  set MODEL=yolo11n.pt
if "%EPOCHS%"=="" set EPOCHS=50
if "%IMGSZ%"==""  set IMGSZ=640
if "%BATCH%"==""  set BATCH=8
if "%NAME%"==""   set NAME=exp

echo Training data=%DATA% model=%MODEL% epochs=%EPOCHS% imgsz=%IMGSZ% batch=%BATCH%
yolo detect train data=%DATA% model=%MODEL% epochs=%EPOCHS% imgsz=%IMGSZ% batch=%BATCH% name=%NAME%
echo.
echo Done. Results in runs\detect\%NAME%\
pause
