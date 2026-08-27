@echo off
setlocal enabledelayedexpansion
title RotoDraft Suite - AI Stock Media & B-Roll Collector

echo.
echo  ==============================================================================
echo  [#] ROTODRAFT SUITE v2.0 PRO -- AI Stock Media & B-Roll Collector Studio
echo  [#] Open-Source Video Asset Creation Pipeline by Ali Rasheed Bhatti
echo  ==============================================================================
echo.

:: 1. Check Python
py --version >nul 2>&1
if %errorlevel% neq 0 (
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not installed!
        echo Please install Python 3.10 or higher from https://python.org
        pause
        exit /b 1
    ) else (
        set PY_CMD=python
    )
) else (
    set PY_CMD=py
)

echo [OK] Detected Python Environment: %PY_CMD%

:: 2. Verify requirements silently
echo [INFO] Checking dependencies (FastAPI, Edge-TTS, FFmpeg, Httpx)...
%PY_CMD% -m pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARN] Automatic pip install encountered warnings. Continuing standard startup...
)

:: 3. Launch application and open browser
echo.
echo [LAUNCH] Starting RotoDraft Suite Web Server on http://127.0.0.1:8000 ...
echo [LAUNCH] Opening your default browser...
echo.

start "" "http://127.0.0.1:8000"
%PY_CMD% app.py

pause
