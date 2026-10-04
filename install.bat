@echo off
title Install Dependencies

echo ============================================
echo   First run: install dependencies
echo ============================================
echo.

cd /d "%~dp0"

set PY=D:\Python\python.exe
if not exist "%PY%" set PY=python

echo Python: %PY%
echo Installing Flask...
echo.

"%PY%" -m pip install -r requirements.txt

echo.
echo ============================================
echo   Done! Double-click start.bat to run.
echo ============================================
pause
