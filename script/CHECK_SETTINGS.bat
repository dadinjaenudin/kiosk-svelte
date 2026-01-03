@echo off
REM ===================================================================
REM  🔍 Check Backend Settings
REM  Verify ALLOWED_HOSTS in running container
REM ===================================================================

echo.
echo ========================================
echo    🔍 Checking Backend Settings
echo ========================================
echo.

echo [1/3] Checking ALLOWED_HOSTS in container...
echo.
docker-compose exec backend cat config/settings.py | findstr /C:"ALLOWED_HOSTS"
echo.
echo.

echo [2/3] Checking if 'backend' is in ALLOWED_HOSTS...
echo.
docker-compose exec backend python -c "from config import settings; print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS); print('backend in ALLOWED_HOSTS:', 'backend' in settings.ALLOWED_HOSTS)"
echo.
echo.

echo [3/3] Checking Django's view of the request...
echo.
docker-compose exec backend python manage.py shell << EOF
from django.http import HttpRequest
from django.conf import settings
print("ALLOWED_HOSTS from settings:", settings.ALLOWED_HOSTS)
print("DEBUG mode:", settings.DEBUG)
EOF
echo.

echo ========================================
echo    📊 Diagnosis
echo ========================================
echo.
echo If ALLOWED_HOSTS shows:
echo   [..., 'backend', ...]
echo   ✅ Settings file is correct
echo.
echo If 'backend in ALLOWED_HOSTS' shows:
echo   True  ✅ Django loaded correct settings
echo   False ❌ Settings not loaded, need NUCLEAR_RESET.bat
echo.
echo If DEBUG is True:
echo   ✅ Should allow all hosts in development
echo.
pause
