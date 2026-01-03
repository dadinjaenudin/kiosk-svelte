@echo off
REM ===================================================================
REM  CREATE NEW USER - Kiosk POS System
REM  Script untuk membuat user baru (admin/owner/manager/cashier)
REM ===================================================================

echo.
echo ========================================
echo    CREATE NEW USER
echo ========================================
echo.

REM Get username
set /p USERNAME="Enter username: "
if "%USERNAME%"=="" (
    echo ERROR: Username cannot be empty
    pause
    exit /b 1
)

REM Get password
set /p PASSWORD="Enter password: "
if "%PASSWORD%"=="" (
    echo ERROR: Password cannot be empty
    pause
    exit /b 1
)

REM Get email
set /p EMAIL="Enter email (optional): "
if "%EMAIL%"=="" set EMAIL=%USERNAME%@example.com

REM Get first name
set /p FIRSTNAME="Enter first name (optional): "
if "%FIRSTNAME%"=="" set FIRSTNAME=User

REM Get last name
set /p LASTNAME="Enter last name (optional): "
if "%LASTNAME%"=="" set LASTNAME=Account

REM Select role
echo.
echo Select user role:
echo   1. Super Admin (full access)
echo   2. Owner (tenant management)
echo   3. Admin/Manager (outlet management)
echo   4. Cashier (POS operations)
echo.
set /p ROLE_CHOICE="Enter choice (1-4): "

if "%ROLE_CHOICE%"=="1" set ROLE=super_admin
if "%ROLE_CHOICE%"=="2" set ROLE=owner
if "%ROLE_CHOICE%"=="3" set ROLE=admin
if "%ROLE_CHOICE%"=="4" set ROLE=cashier

if "%ROLE%"=="" (
    echo ERROR: Invalid role choice
    pause
    exit /b 1
)

echo.
echo ========================================
echo    CREATING USER...
echo ========================================
echo.
echo Username: %USERNAME%
echo Email: %EMAIL%
echo Name: %FIRSTNAME% %LASTNAME%
echo Role: %ROLE%
echo.

REM Create user using Docker
docker-compose exec -T backend python manage.py shell << EOF
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant, Outlet

User = get_user_model()

# Check if user exists
if User.objects.filter(username='%USERNAME%').exists():
    print('ERROR: User %USERNAME% already exists!')
    exit(1)

# Get or create default tenant
tenant = Tenant.objects.first()
if not tenant:
    tenant = Tenant.objects.create(
        name='Default Tenant',
        slug='default-tenant',
        phone='021-12345678',
        email='info@default.com'
    )
    print(f'Created default tenant: {tenant.name}')

# Get or create default outlet
outlet = Outlet.objects.filter(tenant=tenant).first()
if not outlet:
    outlet = Outlet.objects.create(
        tenant=tenant,
        name='Main Outlet',
        slug='main-outlet',
        address='Jakarta',
        city='Jakarta',
        province='DKI Jakarta',
        postal_code='10220',
        phone='021-12345678'
    )
    print(f'Created default outlet: {outlet.name}')

# Create user
is_superuser = '%ROLE%' == 'super_admin'
is_staff = '%ROLE%' in ['super_admin', 'owner', 'admin']

user = User.objects.create_user(
    username='%USERNAME%',
    email='%EMAIL%',
    password='%PASSWORD%',
    first_name='%FIRSTNAME%',
    last_name='%LASTNAME%',
    role='%ROLE%',
    tenant=tenant,
    outlet=outlet,
    is_staff=is_staff,
    is_superuser=is_superuser
)

print('=' * 60)
print('SUCCESS! User created successfully')
print('=' * 60)
print(f'Username: {user.username}')
print(f'Email: {user.email}')
print(f'Name: {user.get_full_name()}')
print(f'Role: {user.get_role_display()}')
print(f'Tenant: {user.tenant.name if user.tenant else "None"}')
print(f'Outlet: {user.outlet.name if user.outlet else "None"}')
print(f'Superuser: {user.is_superuser}')
print(f'Staff: {user.is_staff}')
print('=' * 60)
EOF

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create user
    pause
    exit /b 1
)

echo.
echo ========================================
echo    USER CREATED SUCCESSFULLY!
echo ========================================
echo.
echo You can now login with:
echo   Username: %USERNAME%
echo   Password: %PASSWORD%
echo.
echo Admin Panel: http://localhost:5175/login
echo.
pause
