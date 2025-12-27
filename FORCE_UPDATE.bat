@echo off
REM ===================================================================
REM  🔧 Force Update Settings & Rebuild
REM  Ensures settings.py is correct before rebuild
REM ===================================================================

echo.
echo ========================================
echo    🔧 Force Update & Rebuild
echo ========================================
echo.

echo [1/9] Checking current settings.py...
echo.
type backend\config\settings.py | findstr /N "ALLOWED_HOSTS" | findstr /C:"19:" /C:"20:" /C:"21:" /C:"22:" /C:"23:" /C:"24:" /C:"25:" /C:"26:"
echo.

echo [2/9] Fetching latest from GitHub...
git fetch origin main
echo.

echo [3/9] Resetting local changes (if any)...
git reset --hard origin/main
echo.

echo [4/9] Verifying settings.py updated...
echo.
type backend\config\settings.py | findstr /C:"'backend'" /C:"'kiosk_pos_backend'" /C:"'*'"
echo.
echo If you see 'backend', 'kiosk_pos_backend', and '*' above, settings are correct!
echo.
pause

echo [5/9] Stopping all containers...
docker-compose down
echo.

echo [6/9] Removing backend images...
docker rmi kiosk-svelte-backend kiosk-svelte_backend kiosk_pos_backend -f 2>nul
echo.

echo [7/9] Rebuilding backend (3-5 minutes)...
docker-compose build --no-cache --pull backend
echo.

echo [8/9] Starting all services...
docker-compose up -d
echo.

echo [9/9] Waiting for services (60 seconds)...
timeout /t 60 /nobreak
echo.

echo ========================================
echo    🧪 Testing
echo ========================================
echo.

echo Test 1: Backend health
curl.exe -s http://localhost:8001/api/health/
echo.
echo.

echo Test 2: Check settings in container
docker-compose exec backend python -c "from config import settings; print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS); print('backend in list:', 'backend' in settings.ALLOWED_HOSTS)"
echo.
echo.

echo Test 3: Login with Docker hostname
curl.exe -s -X POST http://localhost:8001/api/auth/login/ -H "Content-Type: application/json" -H "Host: backend" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
echo.
echo.

echo ========================================
echo    📊 Results
echo ========================================
echo.
echo If Test 2 shows "backend in list: True":
echo   ✅ Settings loaded correctly
echo.
echo If Test 3 shows JSON with "token":
echo   ✅ COMPLETELY FIXED! Try browser
echo.
echo If still HTML error:
echo   ❌ Share output with developer
echo.
pause
