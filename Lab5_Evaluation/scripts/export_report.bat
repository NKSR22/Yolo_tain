@echo off
cd /d "%~dp0\.."
mkdir report 2>nul
copy /Y runs\val\confusion_matrix.png report\ >nul
copy /Y runs\val\results.csv report\ >nul 2>nul
copy /Y runs\val\*curve.png report\ >nul 2>nul
echo Report files copied to Lab5_Evaluation\report\
pause
