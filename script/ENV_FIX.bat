@echo off
REM ===================================================================
REM  🎯 FINAL FIX - Environment Variable Override
REM  Sets ALLOWED_HOSTS via docker-compose environment
REM ===================================================================

echo.
echo ========================================
echo    🎯 FINAL FIX
echo ========================================
echo.
echo This fix sets ALLOWED_HOSTS via environment variable
echo which overrides settings.py default.
echo.

echo [1/5] Pulling latest docker-compose.yml...
git pull origin main
echo.

echo [2/5] Stopping containers...
docker-compose down
echo.

echo [3/5] Starting with new environment...
docker-compose up -d
echo.

echo [4/5] Waiting for backend (30 seconds)...
timeout /t 30 /nobreak
echo.

echo [5/5] Testing...
echo.
echo Test 1: Check environment variable in container
docker-compose exec backend env | findstr ALLOWED_HOSTS
echo.
echo.

echo Test 2: Check Django loaded settings
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
echo If Test 1 shows:
echo   ALLOWED_HOSTS=localhost,127.0.0.1,...,backend,...
echo   ✅ Environment variable set correctly
echo.
echo If Test 2 shows:
echo   backend in list: True
echo   ✅ Django loaded correct settings
echo.
echo If Test 3 shows:
echo   {"token": "...", ...}
echo   ✅ COMPLETELY FIXED! Try browser!
echo.
pause
