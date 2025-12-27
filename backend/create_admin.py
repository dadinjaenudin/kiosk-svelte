"""
Create admin user with token for admin panel
"""
from apps.users.models import User
from rest_framework.authtoken.models import Token

print("🔍 Checking for existing admin user...")

# Delete old admin if exists
deleted_count = User.objects.filter(username='admin').delete()[0]
if deleted_count > 0:
    print(f"✅ Deleted {deleted_count} old admin user(s)")

print("👤 Creating new admin user...")

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
print(f"   Email: {admin.email}")
print(f"   Role: {admin.role}")

# Create token for admin
print("🔑 Creating authentication token...")
token, created = Token.objects.get_or_create(user=admin)
if created:
    print(f"✅ Token created: {token.key[:20]}...")
else:
    print(f"✅ Token already exists: {token.key[:20]}...")

print("\n🎉 Admin user setup complete!")
print(f"   Username: admin")
print(f"   Password: admin123")
print(f"   Token: {token.key}")
