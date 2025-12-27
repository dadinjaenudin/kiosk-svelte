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
docker-compose exec backend python manage.py shell << EOF
from apps.users.models import User
from rest_framework.authtoken.models import Token

# Delete old admin if exists
User.objects.filter(username='admin').delete()

# Create new admin
admin = User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin123',
    first_name='Super',
    last_name='Admin',
    role='admin'
)
print(f"✅ Admin created: {admin.username}")

# Create token for admin
token, created = Token.objects.get_or_create(user=admin)
print(f"✅ Token created: {token.key[:20]}...")

exit()
EOF
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
echo If still error:
echo   Run: CHECK_BACKEND_LOGS.bat
echo   Share the output
echo.
pause
