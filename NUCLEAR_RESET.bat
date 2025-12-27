@echo off
REM ===================================================================
REM  🔥 Nuclear Option - Complete Backend Reset
REM  Clean everything and rebuild from scratch
REM ===================================================================

echo.
echo ========================================
echo    🔥 Complete Backend Reset
echo ========================================
echo.
echo This will:
echo   1. Stop all containers
echo   2. Remove backend container AND image
echo   3. Clear Python cache files (.pyc)
echo   4. Rebuild backend from scratch
echo   5. Start everything fresh
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo [1/8] Pulling latest code...
git pull origin main
echo.

echo [2/8] Stopping all containers...
docker-compose down
echo.

echo [3/8] Removing backend image...
docker rmi kiosk-svelte-backend 2>nul
docker rmi kiosk_pos_backend 2>nul
echo ✅ Backend image removed
echo.

echo [4/8] Cleaning Python cache in backend folder...
cd backend
for /r %%i in (*.pyc) do del "%%i" 2>nul
for /d /r %%i in (__pycache__) do rd /s /q "%%i" 2>nul
cd ..
echo ✅ Python cache cleaned
echo.

echo [5/8] Rebuilding backend (no cache, may take 3 minutes)...
docker-compose build --no-cache backend
echo ✅ Backend rebuilt
echo.

echo [6/8] Starting all services...
docker-compose up -d
echo ✅ Services starting
echo.

echo [7/8] Waiting for services to be healthy (60 seconds)...
timeout /t 60 /nobreak
echo.

echo [8/8] Testing...
echo.
echo Testing backend health:
curl.exe -s http://localhost:8001/api/health/
echo.
echo.
echo Testing login with Docker hostname:
curl.exe -s -X POST http://localhost:8001/api/auth/login/ -H "Content-Type: application/json" -H "Host: backend" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
echo.
echo.

echo ========================================
echo    📊 Final Check
echo ========================================
echo.
echo If you see JSON with "token" above:
echo   ✅ FIXED! Try browser login
echo.
echo If you still see DisallowedHost:
echo   ❌ Check if settings.py was actually updated
echo   Run: docker-compose exec backend cat config/settings.py | findstr ALLOWED_HOSTS
echo.
pause
