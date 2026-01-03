@echo off
title Install Kitchen Sync Server Auto-Start
color 0E

echo.
echo ========================================================
echo    INSTALL AUTO-START ON WINDOWS BOOT
echo ========================================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] This script requires Administrator privileges!
    echo.
    echo Please right-click this file and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

echo [OK] Running with Administrator privileges
echo.

REM Get the full path to the executable
set "SCRIPT_DIR=%~dp0"
set "EXE_PATH=%SCRIPT_DIR%dist\kitchen-sync-server-win.exe"

if not exist "%EXE_PATH%" (
    echo [ERROR] Executable not found at:
    echo %EXE_PATH%
    echo.
    echo Please build the executable first:
    echo   1. npm install
    echo   2. npm run build:win
    echo.
    pause
    exit /b 1
)

echo Creating Windows Task Scheduler entry...
echo.

REM Create scheduled task to run at startup
schtasks /create /tn "Kitchen Sync Server" /tr "%EXE_PATH%" /sc onlogon /rl highest /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo    AUTO-START INSTALLED SUCCESSFULLY!
    echo ========================================================
    echo.
    echo The Kitchen Sync Server will now start automatically
    echo when Windows boots.
    echo.
    echo To remove auto-start, run:
    echo   schtasks /delete /tn "Kitchen Sync Server" /f
    echo.
) else (
    echo.
    echo [ERROR] Failed to create scheduled task!
    echo.
)

pause
