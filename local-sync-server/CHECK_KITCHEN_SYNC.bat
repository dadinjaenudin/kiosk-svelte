@echo off
title Kitchen Sync Server - Health Check
color 0B

echo.
echo ========================================================
echo    KITCHEN SYNC SERVER - HEALTH CHECK
echo ========================================================
echo.

echo Checking server status...
echo.

curl -s http://localhost:3002/health

if %ERRORLEVEL% EQU 0 (
    echo.
    echo.
    echo [OK] Server is running!
    echo.
) else (
    echo.
    echo.
    echo [ERROR] Server is not running or not reachable!
    echo.
    echo Please start the server first:
    echo   Double-click START_KITCHEN_SYNC.bat
    echo.
)

pause
