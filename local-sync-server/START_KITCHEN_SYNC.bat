@echo off
title Kitchen Sync Server
color 0A

echo.
echo ========================================================
echo    KITCHEN SYNC SERVER - STARTING
echo ========================================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check if executable exists
if exist "%SCRIPT_DIR%dist\kitchen-sync-server-win.exe" (
    echo [INFO] Starting Kitchen Sync Server from executable...
    echo [INFO] Port: 3001
    echo [INFO] Press Ctrl+C to stop
    echo.
    "%SCRIPT_DIR%dist\kitchen-sync-server-win.exe"
) else (
    echo [WARNING] Executable not found. Using Node.js...
    
    REM Check if Node.js is installed
    node --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Node.js is not installed and no executable found!
        echo.
        echo Please either:
        echo   1. Install Node.js: https://nodejs.org/
        echo   2. Build executable: npm run build:win
        echo.
        pause
        exit /b 1
    )
    
    REM Check if node_modules exists
    if not exist "%SCRIPT_DIR%node_modules" (
        echo [INFO] Installing dependencies...
        call npm install
        if %ERRORLEVEL% NEQ 0 (
            echo [ERROR] Failed to install dependencies!
            pause
            exit /b 1
        )
    )
    
    echo [INFO] Starting Kitchen Sync Server from Node.js...
    echo [INFO] Port: 3001
    echo [INFO] Press Ctrl+C to stop
    echo.
    node server.js
)

echo.
echo Server stopped.
pause
