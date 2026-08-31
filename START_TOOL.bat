@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
TITLE AI B-Roll & Stock Media Collector Pro - Commercial Edition 2026
COLOR 0A

echo =======================================================================
echo    AI B-ROLL ^& STOCK MEDIA COLLECTOR PRO (2026 COMMERCIAL EDITION)
echo    Built by Ali Rasheed from Lahore, Pakistan
echo    Open Source ^& Free Forever (Alternative to Pictory ^& InVideo AI)
echo =======================================================================
echo.
echo Select an option:
echo [1] Launch Web Dashboard (Studio, Showcase, NLE Exporter ^& Settings)
echo [2] Launch Interactive Terminal CLI Wizard
echo [3] View Hermes Agent, OpenClaw ^& Claude Code Integration Guide
echo [4] View About ^& Open Source Manifesto
echo [5] View Contact ^& Hire Ali Rasheed
echo [6] Run Comprehensive Test Suite (10 Unit Tests)
echo [7] Exit
echo.

set /p choice="Enter choice [1-7]: "

if "%choice%"=="1" (
    echo.
    echo [*] Starting Web Studio on http://localhost:8001 ...
    py app.py
) else if "%choice%"=="2" (
    echo.
    echo [*] Launching Interactive Terminal Wizard...
    py cli.py --interactive
    pause
) else if "%choice%"=="3" (
    echo.
    py cli.py --agent-help
    pause
) else if "%choice%"=="4" (
    echo.
    py cli.py --about
    pause
) else if "%choice%"=="5" (
    echo.
    py cli.py --contact
    pause
) else if "%choice%"=="6" (
    echo.
    echo [*] Running Test Suite...
    py tests/test_suite.py
    pause
) else (
    exit
)
