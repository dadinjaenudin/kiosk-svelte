@echo off
REM ===================================================================
REM  🔄 Restart Backend and Test Login
REM  Quick script to apply ALLOWED_HOSTS fix
REM ===================================================================

echo.
echo ========================================
echo    🔄 Applying Backend Fix
echo ========================================
echo.

echo [1/5] Stopping backend...
docker-compose stop backend
echo ✅ Backend stopped
echo.

echo [2/5] Starting backend...
docker-compose up -d backend
echo ✅ Backend starting...
echo.

echo [3/5] Waiting for backend to be healthy (30 seconds)...
timeout /t 30 /nobreak
echo.

echo [4/5] Checking backend health...
curl -s http://localhost:8001/api/health/
echo.
echo.

echo [5/5] Testing login endpoint...
curl -X POST http://localhost:8001/api/auth/login/ ^
  -H "Content-Type: application/json" ^
  -H "Host: backend" ^
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
echo.
echo.

echo ========================================
echo    ✅ Backend Restarted
echo ========================================
echo.
echo If you see "token" above = SUCCESS! ✅
echo If you see "DisallowedHost" = NEED TO REBUILD ❌
echo.
echo Next steps:
echo 1. Open: http://localhost:5175/
echo 2. Login: admin / admin123
echo 3. Should work now!
echo.
pause
