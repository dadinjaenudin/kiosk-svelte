@echo off
REM ===================================================================
REM  🔍 Debug Login Issue
REM  Comprehensive diagnostics for 400 Bad Request
REM ===================================================================

echo.
echo ========================================
echo    🔍 Login Debugging Script
echo ========================================
echo.

REM Step 1: Backend Health
echo [1/6] Checking backend health...
curl -s http://localhost:8001/api/health/
echo.
echo.

REM Step 2: Check Admin User
echo [2/6] Checking if admin user exists...
docker-compose exec -T backend python manage.py shell << EOF
from apps.users.models import User
admin = User.objects.filter(username='admin').first()
if admin:
    print(f"\n✅ Admin user exists:")
    print(f"   Username: {admin.username}")
    print(f"   Email: {admin.email}")
    print(f"   Role: {admin.role}")
    print(f"   Active: {admin.is_active}")
else:
    print("\n❌ Admin user NOT FOUND!")
    print("   Run: CREATE_USERS.bat to create it")

print("\n📋 All users in database:")
for u in User.objects.all()[:10]:
    print(f"   - {u.username} ({u.role})")
exit()
EOF
echo.

REM Step 3: Test Login API Directly
echo [3/6] Testing login API directly...
curl -X POST http://localhost:8001/api/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
echo.
echo.

REM Step 4: Check Migrations
echo [4/6] Checking migrations status...
docker-compose exec -T backend python manage.py showmigrations | findstr /C:"auth" /C:"users"
echo.
echo.

REM Step 5: Check Backend Logs
echo [5/6] Recent backend logs...
echo ----------------------------------------
docker-compose logs backend --tail=30 | findstr /C:"POST" /C:"login" /C:"ERROR" /C:"auth"
echo ----------------------------------------
echo.

REM Step 6: Check Admin Container Proxy
echo [6/6] Recent admin proxy logs...
echo ----------------------------------------
docker-compose logs admin --tail=20 | findstr /C:"Proxying" /C:"response" /C:"error"
echo ----------------------------------------
echo.

echo.
echo ========================================
echo    📊 Diagnostic Summary
echo ========================================
echo.
echo If you see:
echo   ✅ Backend health OK
echo   ✅ Admin user exists
echo   ✅ Direct API test returns token
echo   ➡️ Issue is in frontend/proxy
echo.
echo   ✅ Backend health OK
echo   ❌ Admin user not found
echo   ➡️ Run: CREATE_USERS.bat
echo.
echo   ❌ Backend health fails
echo   ➡️ Run: docker-compose restart backend
echo.
echo   ✅ Admin exists
echo   ❌ Direct API test fails
echo   ➡️ Check backend logs for errors
echo.
echo ========================================
echo.
pause
