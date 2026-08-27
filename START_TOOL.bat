@echo off
setlocal enabledelayedexpansion
title RotoDraft Suite - AI Stock Media Collector

echo ==============================================================================
echo       ROTODRAFT SUITE -- AI Stock Media & B-Roll Collector Studio
echo       Open-Source Video Asset Creation Pipeline by Ali Rasheed Bhatti
echo ==============================================================================
echo.

:: 1. Check Python
py --version >nul 2>&1
if %errorlevel% neq 0 (
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not installed! Please install Python 3.10+ from https://python.org
        pause
        exit /b 1
    ) else (
        set PY_CMD=python
    )
) else (
    set PY_CMD=py
)

echo [OK] Python found: %PY_CMD%

:: 2. Check & install requirements
echo [INFO] Verifying dependencies...
%PY_CMD% -m pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARN] Pip install had issues, attempting standard run...
)

:: 3. Launch application and open browser
echo [INFO] Starting RotoDraft Suite on http://127.0.0.1:8000 ...
start "" "http://127.0.0.1:8000"
%PY_CMD% app.py

pause
