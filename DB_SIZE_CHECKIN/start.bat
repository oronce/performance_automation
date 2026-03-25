@echo off
title DB Size Monitor
cd /d "%~dp0"

echo ==========================================
echo  DB Size Monitor — starting...
echo  Dashboard: http://localhost:8787
echo ==========================================

REM Try to find python in venv or system
if exist "..\..\..\venv3100\Scripts\python.exe" (
    set PYTHON=..\..\..\venv3100\Scripts\python.exe
) else if exist "venv\Scripts\python.exe" (
    set PYTHON=venv\Scripts\python.exe
) else (
    set PYTHON=python
)

echo Using Python: %PYTHON%
echo.

REM Install deps if needed
%PYTHON% -m pip install -q -r requirements.txt

REM Launch server (daemon is embedded)
%PYTHON% server.py

pause
