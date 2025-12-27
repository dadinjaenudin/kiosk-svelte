@echo off
REM ===================================================================
REM  🚀 Quick Start Admin Panel
REM  Path: D:\YOGYA-Kiosk\kiosk-svelte
REM ===================================================================

echo.
echo ========================================
echo    🚀 Admin Panel Startup
echo ========================================
echo.
echo Select startup method:
echo.
echo [1] Docker (Recommended for production-like environment)
echo [2] Local NPM (Faster for development)
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" goto docker
if "%choice%"=="2" goto local

echo ❌ Invalid choice. Exiting.
pause
exit /b 1

:docker
echo.
echo ========================================
echo    🐳 Starting Admin with Docker
echo ========================================
echo.

REM Check Docker
echo [1/3] 🐳 Checking Docker...
docker-compose ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running or docker-compose not found
    echo    Please start Docker Desktop first
    pause
    exit /b 1
)
echo ✅ Docker is running

REM Build and start admin service
echo.
echo [2/3] 🔨 Building admin service...
docker-compose build admin
if errorlevel 1 (
    echo ❌ Build failed
    pause
    exit /b 1
)
echo ✅ Build complete

echo.
echo [3/3] 🚀 Starting admin service...
docker-compose up admin
goto end

:local
echo.
echo ========================================
echo    💻 Starting Admin Locally
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "admin\package.json" (
    echo ❌ Error: Please run this script from project root
    echo    Expected path: D:\YOGYA-Kiosk\kiosk-svelte
    pause
    exit /b 1
)

REM Step 1: Check Docker
echo [1/5] 🐳 Checking Docker...
docker-compose ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running or docker-compose not found
    echo    Please start Docker Desktop first
    pause
    exit /b 1
)
echo ✅ Docker is running

REM Step 2: Check Backend
echo.
echo [2/5] 🔍 Checking Backend...
docker-compose ps | findstr "backend" | findstr "Up" >nul
if errorlevel 1 (
    echo ⚠️  Backend not running. Starting backend...
    docker-compose up -d backend
    echo ⏳ Waiting for backend to start...
    timeout /t 15 /nobreak >nul
)
echo ✅ Backend is running

REM Step 3: Install Dependencies (if needed)
echo.
echo [3/5] 📦 Checking npm dependencies...
if not exist "admin\node_modules" (
    echo ⚠️  Dependencies not found. Installing...
    cd admin
    call npm install
    cd ..
    if errorlevel 1 (
        echo ❌ npm install failed
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed
) else (
    echo ✅ Dependencies already installed
)

REM Step 4: Run Migration
echo.
echo [4/5] 🔄 Running database migrations...
docker-compose exec -T backend python manage.py migrate >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Migration might have issues, continuing anyway...
) else (
    echo ✅ Migrations complete
)

REM Step 5: Start Admin Server
echo.
echo [5/5] 🎯 Starting Admin Dev Server...
echo.
echo ========================================
echo    ✅ Admin Panel Starting!
echo ========================================
echo.
echo 📍 Admin Panel: http://localhost:5175/
echo 📍 Backend API: http://localhost:8001/api/
echo.
echo 🔐 Demo Login:
echo    Username: admin
echo    Password: admin123
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

cd admin
call npm run dev:local
goto end

:end
echo.
echo ⚠️  Admin server stopped
pause
