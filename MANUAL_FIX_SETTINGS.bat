@echo off
REM ===================================================================
REM  ✍️ Manually Fix ALLOWED_HOSTS
REM  Direct edit if git pull/reset doesn't work
REM ===================================================================

echo.
echo ========================================
echo    ✍️ Manual ALLOWED_HOSTS Fix
echo ========================================
echo.

echo This will backup and manually fix settings.py
echo.
pause

echo [1/4] Creating backup...
copy backend\config\settings.py backend\config\settings.py.backup
echo ✅ Backup created: backend\config\settings.py.backup
echo.

echo [2/4] Creating fixed settings.py...
(
echo # Security
echo SECRET_KEY = env^('SECRET_KEY', default='django-insecure-dev-key-change-in-production'^)
echo DEBUG = env^('DEBUG', default=True^)
echo ALLOWED_HOSTS = env.list^('ALLOWED_HOSTS', default=[
echo     'localhost',
echo     '127.0.0.1',
echo     '0.0.0.0',
echo     'backend',              # Docker internal hostname
echo     'kiosk_pos_backend',    # Docker container name
echo     '*'                     # Allow all in development
echo ]^)
) > backend\config\settings_fix.txt

echo ✅ Fix file created
echo.

echo [3/4] Checking current settings.py line 16-26...
type backend\config\settings.py | more +16 | findstr /N "." | findstr /B "1: 2: 3: 4: 5: 6: 7: 8: 9: 10:"
echo.

echo [4/4] Instructions to apply fix:
echo.
echo OPTION A - Manual Edit:
echo   1. Open: backend\config\settings.py
echo   2. Find line ~19: ALLOWED_HOSTS = env.list(...)
echo   3. Replace lines 19-26 with content from: backend\config\settings_fix.txt
echo   4. Save file
echo   5. Run: NUCLEAR_RESET.bat
echo.
echo OPTION B - Use Backup ^& Git:
echo   1. Run: git diff backend\config\settings.py
echo   2. If shows changes, run: git checkout backend\config\settings.py
echo   3. Run: git pull origin main
echo   4. Run: NUCLEAR_RESET.bat
echo.
echo OPTION C - Copy from GitHub:
echo   1. Open: https://github.com/dadinjaenudin/kiosk-svelte/blob/main/backend/config/settings.py
echo   2. Copy lines 16-26
echo   3. Paste into your backend\config\settings.py
echo   4. Save
echo   5. Run: NUCLEAR_RESET.bat
echo.
echo ========================================
echo.
echo Reference - Correct ALLOWED_HOSTS:
echo.
type backend\config\settings_fix.txt
echo.
echo ========================================
echo.
pause
