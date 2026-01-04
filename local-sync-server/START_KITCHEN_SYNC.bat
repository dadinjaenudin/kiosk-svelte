@echo off
title Kitchen Sync Server
color 0A

echo.
echo ========================================================
echo    KITCHEN SYNC SERVER - STARTING...
echo ========================================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"

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
    echo.
    echo [OK] Dependencies installed
    echo.
)

echo Starting server with Node.js...
echo.

REM Change to script directory and run server
cd /d "%SCRIPT_DIR%"
node server.js

REM If server stops, pause to see error messages
pause
