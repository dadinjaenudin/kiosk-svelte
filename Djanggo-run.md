cd kiosk-svelte
docker-compose down

git pull origin main

# Atau jika ada perubahan lokal
git fetch origin main
git merge origin/main

docker-compose up --build -d
docker-compose exec backend python manage.py makemigrations
docker-compose run --rm backend python manage.py migrate
docker-compose exec backend python manage.py seed_demo_data
docker-compose exec backend python manage.py seed_foodcourt
docker-compose exec backend python manage.py seed_promotion
docker-compose exec backend python manage.py seed_customer

# Note: Admin user will be assigned to 'Warung Nasi Padang' tenant
# To view products from other tenants, login with tenant-specific users:
# - warung-nasi-padang / password123
# - mie-ayam-bakso / password123
# - ayam-geprek / password123
# - soto-betawi / password123
# - nasi-goreng / password123

docker-compose restart frontend

docker-compose restart admin

docker-compose exec backend python manage.py shell
>>> from apps.users.models import User
>>> admin = User.objects.filter(username='admin').first()
>>> if not admin:
...     admin = User.objects.create_superuser(
...         username='admin',
...         password='admin123',
...         email='admin@example.com',
...         role='admin'
...     )
>>> print(f"Admin exists: {admin.username}, Role: {admin.role}")
>>> exit()

URLs PENTING
Kiosk: http://localhost:5174/kiosk
Kitchen: http://localhost:5174/kitchen
API Docs: http://localhost:8001/api/docs/
Django Admin: http://localhost:8001/admin/
GitHub: https://github.com/dadinjaenudin/kiosk-svelte
