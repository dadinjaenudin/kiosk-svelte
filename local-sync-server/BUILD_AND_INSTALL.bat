@echo off
title Build and Install Kitchen Sync Server
color 0B

echo.
echo ========================================================
echo    BUILD AND INSTALL KITCHEN SYNC SERVER
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

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Step 1: Check Node.js
echo [STEP 1/4] Checking Node.js installation...
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

REM Step 2: Install dependencies
echo [STEP 2/4] Installing dependencies...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Step 3: Build executable
echo [STEP 3/4] Building Windows executable...
echo This may take a few minutes...
call npm run build:win
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to build executable!
    pause
    exit /b 1
)
echo [OK] Executable built successfully
echo.

REM Step 4: Install auto-start
echo [STEP 4/4] Installing auto-start...
echo.

set "EXE_PATH=%SCRIPT_DIR%dist\kitchen-sync-server-win.exe"

if not exist "%EXE_PATH%" (
    echo [ERROR] Executable not found after build!
    pause
    exit /b 1
)

REM Create scheduled task
schtasks /create /tn "Kitchen Sync Server" /tr "\"%EXE_PATH%\"" /sc onlogon /rl highest /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo    BUILD AND INSTALL COMPLETED!
    echo ========================================================
    echo.
    echo [OK] Executable: %EXE_PATH%
    echo [OK] Size: 
    dir "%EXE_PATH%" | findstr kitchen-sync-server-win.exe
    echo.
    echo [OK] Auto-start configured
    echo [OK] Server will start automatically on Windows boot
    echo.
    echo To start server now without rebooting:
    echo   Double-click START_KITCHEN_SYNC.bat
    echo.
    echo Or run in background:
    schtasks /run /tn "Kitchen Sync Server"
    echo [INFO] Server started in background!
    echo.
    echo To stop:
    echo   taskkill /F /IM kitchen-sync-server-win.exe
    echo.
    echo To uninstall auto-start:
    echo   Run UNINSTALL_AUTOSTART.bat
    echo.
) else (
    echo.
    echo [ERROR] Failed to install auto-start!
    echo.
)

pause
