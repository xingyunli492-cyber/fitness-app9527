@echo off
title Fitness Calorie Manager

echo ============================================
echo   Fitness Calorie Manager - Starting...
echo ============================================
echo.

cd /d "%~dp0"

set PY=D:\Python\python.exe
if not exist "%PY%" set PY=python

echo Starting server...
echo Browser will open http://127.0.0.1:5000
echo Close this window to stop the server.
echo.

start "" http://127.0.0.1:5000

"%PY%" app.py

pause
