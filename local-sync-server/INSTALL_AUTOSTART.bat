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

REM Get the full path to the start script
set "SCRIPT_DIR=%~dp0"
set "START_SCRIPT=%SCRIPT_DIR%START_KITCHEN_SYNC.bat"

if not exist "%START_SCRIPT%" (
    echo [ERROR] Start script not found at:
    echo %START_SCRIPT%
    echo.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed!
    echo.
    echo Please install Node.js first:
    echo   Download from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo [OK] Node.js is installed
echo.

REM Check if server.js exists
if not exist "%SCRIPT_DIR%server.js" (
    echo [ERROR] server.js not found!
    echo.
    pause
    exit /b 1
)

echo [OK] server.js found
echo.

REM Check if node_modules exists
if not exist "%SCRIPT_DIR%node_modules" (
    echo [WARNING] node_modules not found!
    echo Running npm install...
    echo.
    cd /d "%SCRIPT_DIR%"
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] npm install failed!
        pause
        exit /b 1
    )
)

echo Creating Windows Task Scheduler entry...
echo.

REM Create scheduled task to run at startup
schtasks /create /tn "Kitchen Sync Server" /tr "\"%START_SCRIPT%\"" /sc onlogon /rl highest /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo    AUTO-START INSTALLED SUCCESSFULLY!
    echo ========================================================
    echo.
    echo The Kitchen Sync Server will now start automatically
    echo when Windows boots.
    echo.
    echo To test, run: START_KITCHEN_SYNC.bat
    echo.
    echo To remove auto-start, run:
    echo   schtasks /delete /tn "Kitchen Sync Server" /f
    echo.
    echo To view scheduled task:
    echo   schtasks /query /tn "Kitchen Sync Server" /fo LIST /v
    echo.
) else (
    echo.
    echo [ERROR] Failed to create scheduled task!
    echo.
)

pause
