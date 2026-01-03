@echo off
REM ===================================================================
REM  🚀 One-Click Test & Fix Backend Login
REM  Complete solution for DisallowedHost issue
REM ===================================================================

echo.
echo ========================================
echo    🚀 Backend Login Fix & Test
echo ========================================
echo.

echo Step 1: Pulling latest code...
git pull origin main
echo.

echo Step 2: Rebuilding backend (this may take 2 minutes)...
echo.
docker-compose stop backend
docker-compose rm -f backend
docker-compose build --no-cache backend
docker-compose up -d backend
echo.

echo Step 3: Waiting for backend to be ready (40 seconds)...
timeout /t 40 /nobreak
echo.

echo Step 4: Testing backend health...
curl -s http://localhost:8001/api/health/
echo.
echo.

echo Step 5: Testing login with Docker hostname...
curl -s -X POST http://localhost:8001/api/auth/login/ -H "Content-Type: application/json" -H "Host: backend" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
echo.
echo.

echo ========================================
echo    📊 Test Results
echo ========================================
echo.
echo Look at the output above:
echo.
echo If you see:
echo   {"token": "..." , "user": {...}}
echo   ✅ SUCCESS! Backend is fixed!
echo.
echo If you see:
echo   DisallowedHost HTML error
echo   ❌ FAILED - Try running this script again
echo.
echo If you see:
echo   Invalid credentials
echo   ❌ Admin user not created - Run: CREATE_USERS.bat
echo.
echo ========================================
echo.
echo Next: Open http://localhost:5175/ and login!
echo.
pause
