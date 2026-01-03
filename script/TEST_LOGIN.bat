@echo off
REM ===================================================================
REM  🧪 Test Login Endpoint
REM  Quick test to verify ALLOWED_HOSTS fix
REM ===================================================================

echo.
echo ========================================
echo    🧪 Testing Login Endpoint
echo ========================================
echo.

echo [1/3] Testing backend health...
curl -s http://localhost:8001/api/health/
echo.
echo.

echo [2/3] Testing login with localhost (should work)...
curl -s -X POST http://localhost:8001/api/auth/login/ -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
echo.
echo.

echo [3/3] Testing login with Docker hostname (the fix!)...
curl -s -X POST http://localhost:8001/api/auth/login/ -H "Content-Type: application/json" -H "Host: backend" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
echo.
echo.

echo ========================================
echo    📊 Test Results
echo ========================================
echo.
echo If you see JSON with "token" in both tests:
echo   ✅ BACKEND FIXED! Login should work in browser
echo.
echo If test 2 works but test 3 shows HTML error:
echo   ❌ ALLOWED_HOSTS not applied yet
echo   ➡️ Run: REBUILD_BACKEND.bat
echo.
echo If both fail with "Invalid credentials":
echo   ❌ Admin user not created
echo   ➡️ Run: CREATE_USERS.bat
echo.
pause
