@echo off
REM ===================================================================
REM  🔍 Check Backend Logs for 500 Error
REM  View recent errors and configuration issues
REM ===================================================================

echo.
echo ========================================
echo    🔍 Backend Error Diagnosis
echo ========================================
echo.

echo [1/3] Recent backend logs (last 50 lines)...
echo.
docker-compose logs backend --tail=50
echo.
echo.

echo [2/3] Check for ImproperlyConfigured errors...
echo.
docker-compose logs backend --tail=100 | findstr /C:"ImproperlyConfigured" /C:"Error" /C:"Exception"
echo.
echo.

echo [3/3] Test login and capture error...
echo.
curl.exe -v -X POST http://localhost:8001/api/auth/login/ -H "Content-Type: application/json" -H "Host: backend" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
echo.
echo.

echo ========================================
echo    📊 Common ImproperlyConfigured Issues
echo ========================================
echo.
echo 1. SECRET_KEY not set
echo 2. Database connection failed
echo 3. Missing rest_framework.authtoken in INSTALLED_APPS
echo 4. Token model not migrated
echo 5. CORS settings issue
echo.
echo Check the logs above for specific error message.
echo.
pause
