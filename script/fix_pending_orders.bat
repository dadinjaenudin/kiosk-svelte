@echo off
REM Fix pending orders stuck in pending status

echo ================================
echo Fix Pending Orders
echo ================================
echo.
echo This will update pending orders to confirmed status
echo so they appear in Kitchen Display.
echo.
pause

echo.
echo Fixing pending orders...
echo.

type fix_pending_orders.py | docker-compose exec -T backend python manage.py shell

echo.
echo ================================
echo Done! Orders should now appear in Kitchen Display.
echo ================================
echo.
echo Next steps:
echo 1. Refresh Kitchen Display (F5)
echo 2. Orders should now be visible
echo.
pause
