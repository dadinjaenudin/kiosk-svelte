@echo off
REM ===================================================================
REM  🔍 Debug Admin Docker Container
REM  Checks admin container status and logs
REM ===================================================================

echo.
echo ========================================
echo    🔍 Admin Container Diagnostics
echo ========================================
echo.

echo [1/5] Checking Docker Status...
docker-compose ps
echo.

echo [2/5] Checking Admin Container Specifically...
docker-compose ps admin
echo.

echo [3/5] Admin Container Logs (last 50 lines)...
echo ----------------------------------------
docker-compose logs admin --tail=50
echo ----------------------------------------
echo.

echo [4/5] Checking if port 5175 is listening...
netstat -ano | findstr :5175
echo.

echo [5/5] Checking Backend Health...
curl -s http://localhost:8001/api/health/
echo.
echo.

echo ========================================
echo    📋 Diagnostic Complete
echo ========================================
echo.
echo Possible Issues:
echo [1] Admin container crashed - Check logs above
echo [2] Port conflict - Check netstat output
echo [3] Backend not ready - Check health endpoint
echo [4] Build error - Try: docker-compose build --no-cache admin
echo.
pause
