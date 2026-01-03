@echo off
REM ===================================================================
REM  🔨 Rebuild Backend (Force Apply Settings)
REM  Use this if RESTART_BACKEND.bat didn't work
REM ===================================================================

echo.
echo ========================================
echo    🔨 Rebuilding Backend
echo ========================================
echo.
echo This will:
echo   1. Stop backend container
echo   2. Remove old container
echo   3. Rebuild with new settings
echo   4. Start fresh container
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo [1/5] Stopping and removing backend...
docker-compose stop backend
docker-compose rm -f backend
echo ✅ Backend removed
echo.

echo [2/5] Rebuilding backend (may take 1-2 minutes)...
docker-compose build --no-cache backend
echo ✅ Backend rebuilt
echo.

echo [3/5] Starting backend...
docker-compose up -d backend
echo ✅ Backend starting...
echo.

echo [4/5] Waiting for backend to be ready (40 seconds)...
timeout /t 40 /nobreak
echo.

echo [5/5] Testing backend health...
curl -s http://localhost:8001/api/health/
echo.
echo.

echo Testing login with Docker hostname...
curl -X POST http://localhost:8001/api/auth/login/ ^
  -H "Content-Type: application/json" ^
  -H "Host: backend" ^
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
echo.
echo.

echo ========================================
echo    ✅ Backend Rebuild Complete
echo ========================================
echo.
echo If you see JSON with "token" above:
echo   ✅ SUCCESS! Backend accepts Docker hostname
echo.
echo If you still see HTML error:
echo   ❌ Check backend logs: docker-compose logs backend --tail=50
echo.
echo Next: Try login at http://localhost:5175/
echo.
pause
