@echo off
title Kitchen Sync Server
color 0A

echo.
echo ========================================================
echo    KITCHEN SYNC SERVER - STARTING...
echo ========================================================
echo.

REM Check if executable exists
if exist "dist\kitchen-sync-server-win.exe" (
    echo [OK] Executable found: dist\kitchen-sync-server-win.exe
    echo.
    echo Starting server...
    echo.
    cd dist
    kitchen-sync-server-win.exe
) else (
    echo [ERROR] Executable not found!
    echo.
    echo Please build the executable first:
    echo   1. npm install
    echo   2. npm run build:win
    echo.
    pause
    exit /b 1
)

pause
