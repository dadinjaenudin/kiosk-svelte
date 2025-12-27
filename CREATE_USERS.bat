@echo off
REM ===================================================================
REM  👥 Create Admin Users
REM  Creates super admin and tenant owners
REM ===================================================================

echo.
echo ========================================
echo    👥 Creating Admin Users
echo ========================================
echo.

REM Check Docker
docker-compose ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running
    pause
    exit /b 1
)

echo 📝 Creating users via Django shell...
echo.

docker-compose exec -T backend python manage.py shell << EOF
from apps.users.models import User
from apps.tenants.models import Tenant

print("🔍 Checking existing users...")

# Create super admin
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        first_name='Super',
        last_name='Admin',
        role='admin'
    )
    print(f"✅ Super Admin created: {admin.username}")
else:
    print("✅ Super Admin already exists: admin")

# Create Owner for each tenant
print("\n🏪 Creating tenant owners...")
tenant_count = 0
for tenant in Tenant.objects.all():
    username = f"owner_{tenant.slug}"
    if not User.objects.filter(username=username).exists():
        owner = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password='password123',
            first_name='Owner',
            last_name=tenant.name[:20],
            role='owner',
            tenant=tenant
        )
        print(f"✅ Created: {owner.username} for {tenant.name}")
        tenant_count += 1
    else:
        print(f"✅ Exists: {username}")

print("\n" + "="*50)
print("🎉 User Creation Complete!")
print("="*50)
print("\n📝 Login Credentials:")
print("   Super Admin:")
print("      Username: admin")
print("      Password: admin123")
print("\n   Tenant Owners:")
print("      Username: owner_{tenant-slug}")
print("      Password: password123")
print("\n🔗 Admin Panel: http://localhost:5175/")
print("="*50)
EOF

echo.
echo ✅ Users created successfully!
echo.
echo 🔗 You can now login at: http://localhost:5175/
echo.
pause
