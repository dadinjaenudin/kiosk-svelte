# 🚀 Quick Start Guide

Panduan cepat untuk menjalankan POS F&B System dalam 5 menit.

## Prerequisites

Pastikan sudah terinstall:
- **Docker** (20.10+)
- **Docker Compose** (2.0+)
- **Git**

## 1. Clone & Setup

```bash
# Clone repository
git clone <repository-url>
cd webapp

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

## 2. Start Services

```bash
# Build and start all containers
docker-compose up -d

# Wait for services to be healthy (~ 30 seconds)
docker-compose ps
```

Expected output:
```
NAME                COMMAND                  SERVICE       STATUS
pos_backend         "sh -c 'python manag…"   backend       Up (healthy)
pos_celery_beat     "celery -A config be…"   celery_beat   Up
pos_celery_worker   "celery -A config wo…"   celery_worker Up
pos_db              "docker-entrypoint.s…"   db            Up (healthy)
pos_frontend        "docker-entrypoint.s…"   frontend      Up
pos_nginx           "/docker-entrypoint.…"   nginx         Up
pos_redis           "docker-entrypoint.s…"   redis         Up (healthy)
```

## 3. Initialize Database

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser (for admin panel)
docker-compose exec backend python manage.py createsuperuser
# Username: admin
# Email: admin@pos.com
# Password: admin123 (use strong password in production!)

# Load demo data (optional)
docker-compose exec backend python manage.py seed_demo_data
```

## 4. Access Applications

### 🖥️ Kiosk Mode (Main Interface)
**URL**: http://localhost:5173/kiosk

Features:
- Touch-optimized interface
- Fullscreen mode (press F11)
- Offline-first capability
- Real-time cart updates

### 🔧 Admin Panel (Django)
**URL**: http://localhost:8000/admin
- Username: admin
- Password: (your created password)

### 📚 API Documentation
**URL**: http://localhost:8000/api/docs
- Interactive Swagger UI
- All API endpoints documented

### 🌐 Backend API
**URL**: http://localhost:8000/api
- Health check: http://localhost:8000/api/health/

## 5. Testing the Kiosk

### Add Demo Products

```bash
# Using Django shell
docker-compose exec backend python manage.py shell

# Paste this code:
from apps.tenants.models import Tenant
from apps.products.models import Product, Category

# Create tenant
tenant = Tenant.objects.create(name="Demo Restaurant", slug="demo")

# Create categories
cat_food = Category.objects.create(name="Food", tenant=tenant, sort_order=1)
cat_drinks = Category.objects.create(name="Drinks", tenant=tenant, sort_order=2)

# Create products
Product.objects.create(
    name="Nasi Goreng", 
    category=cat_food, 
    tenant=tenant,
    price=25000,
    description="Indonesian fried rice",
    sku="FD001"
)

Product.objects.create(
    name="Es Teh Manis", 
    category=cat_drinks, 
    tenant=tenant,
    price=5000,
    description="Sweet iced tea",
    sku="DR001"
)

print("Demo data created!")
exit()
```

### Test Offline Mode

1. Open http://localhost:5173/kiosk
2. Add items to cart
3. Open DevTools (F12)
4. Go to Network tab → Throttle to "Offline"
5. Try adding more items (should still work!)
6. Go back online → items sync automatically

## 6. Development Workflow

### Backend Development

```bash
# View logs
docker-compose logs -f backend

# Run Django commands
docker-compose exec backend python manage.py <command>

# Create new app
docker-compose exec backend python manage.py startapp myapp

# Make migrations
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

### Frontend Development

```bash
# View logs
docker-compose logs -f frontend

# Install new package
docker-compose exec frontend npm install <package>

# Rebuild
docker-compose exec frontend npm run build

# Run tests
docker-compose exec frontend npm test
```

### Database Access

```bash
# PostgreSQL shell
docker-compose exec db psql -U pos_user -d pos_db

# Common queries
\dt                  # List tables
\d users_user        # Describe table
SELECT * FROM users_user LIMIT 5;
```

### Redis Access

```bash
# Redis CLI
docker-compose exec redis redis-cli

# Common commands
KEYS *              # List all keys
GET pos:products    # Get value
FLUSHDB             # Clear database
```

## 7. Troubleshooting

### Containers not starting

```bash
# Check logs
docker-compose logs

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database connection error

```bash
# Restart database
docker-compose restart db

# Check database is healthy
docker-compose exec db pg_isready -U pos_user -d pos_db
```

### Frontend not loading

```bash
# Check if frontend is running
docker-compose ps frontend

# Rebuild node_modules
docker-compose exec frontend rm -rf node_modules
docker-compose exec frontend npm install
docker-compose restart frontend
```

### Port already in use

```bash
# Find process using port
sudo lsof -i :5173    # Frontend
sudo lsof -i :8000    # Backend
sudo lsof -i :5432    # PostgreSQL

# Kill process
kill -9 <PID>

# Or change ports in docker-compose.yml
```

## 8. Stop Services

```bash
# Stop all containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove volumes (WARNING: deletes all data!)
docker-compose down -v
```

## 9. Production Deployment

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Set environment variables
export DEBUG=False
export SECRET_KEY=<strong-secret-key>
export DATABASE_URL=<production-database-url>

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput

# Run migrations
docker-compose exec backend python manage.py migrate
```

## 10. Next Steps

✅ Customize branding (colors, logo)
✅ Add your product catalog
✅ Configure payment gateway (Midtrans/Xendit)
✅ Setup domain and SSL
✅ Configure monitoring (Sentry)
✅ Setup backups

## Need Help?

- 📖 Full documentation: README.md
- 🏗️ Architecture: ARCHITECTURE.md
- 🐛 Report issues: GitHub Issues
- 💬 Community: Discord/Slack

---

**Happy Coding! 🎉**
