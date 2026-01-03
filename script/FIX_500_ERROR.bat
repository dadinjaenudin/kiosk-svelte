@echo off
REM ===================================================================
REM  🔧 Fix 500 ImproperlyConfigured Error
REM  Run migrations and create admin user
REM ===================================================================

echo.
echo ========================================
echo    🔧 Fixing 500 Internal Server Error
echo ========================================
echo.

echo This will:
echo   1. Run migrations (especially authtoken)
echo   2. Create/reset admin user
echo   3. Test login
echo.
pause

echo [1/5] Running migrations...
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
echo.

echo [2/5] Checking authtoken migration...
docker-compose exec backend python manage.py showmigrations authtoken
echo.

echo [3/5] Creating/resetting admin user...
docker-compose exec backend python create_admin.py
echo.

echo [4/5] Restarting backend...
docker-compose restart backend
timeout /t 15 /nobreak
echo.

echo [5/5] Testing login...
echo.
curl.exe -s -X POST http://localhost:8001/api/auth/login/ -H "Content-Type: application/json" -H "Host: backend" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
echo.
echo.

echo ========================================
echo    📊 Results
echo ========================================
echo.
echo If you see JSON with "token":
echo   ✅ FIXED! Try browser login
echo.
echo If still HTML error:
echo   Check backend logs:
echo   docker-compose logs backend --tail=50
echo.
pause
