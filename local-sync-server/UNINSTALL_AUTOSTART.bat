@echo off
title Uninstall Kitchen Sync Server Auto-Start
color 0C

echo.
echo ========================================================
echo    UNINSTALL AUTO-START FROM WINDOWS BOOT
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

echo Removing Windows Task Scheduler entry...
echo.

REM Delete scheduled task
schtasks /delete /tn "Kitchen Sync Server" /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo    AUTO-START UNINSTALLED SUCCESSFULLY!
    echo ========================================================
    echo.
    echo The Kitchen Sync Server will no longer start automatically
    echo when Windows boots.
    echo.
    echo You can still start it manually by running:
    echo   START_KITCHEN_SYNC.bat
    echo.
) else (
    echo.
    echo [WARNING] Task not found or already removed.
    echo.
)

pause
