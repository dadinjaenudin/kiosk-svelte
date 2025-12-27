@echo off
REM Check orders in database for debugging Kitchen Display - Windows Batch Version

echo ================================
echo Kitchen Display - Database Check
echo ================================
echo.

echo Step 1: Checking all orders in database...
echo.

docker-compose exec -T backend python manage.py shell < check_orders.py

echo.
echo ================================
echo Check complete!
echo ================================
pause
