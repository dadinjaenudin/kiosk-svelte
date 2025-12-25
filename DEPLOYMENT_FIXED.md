# 🚀 Deployment Guide - Fixed & Ready

## ✅ Problem SOLVED - Docker Build Error Fixed

**Issue**: `xendit-python==2.14.0` tidak tersedia di PyPI  
**Solution**: Implementasi **Custom REST API Clients** untuk Xendit & Midtrans (lebih reliable dan maintainable)

---

## 📦 Fresh Deployment (Step-by-Step)

### 1️⃣ Clone Repository (Atau Pull Update)

**Jika belum pernah clone:**
```bash
git clone https://github.com/dadinjaenudin/kiosk-svelte.git
cd kiosk-svelte
```

**Jika sudah ada local repository:**
```bash
cd kiosk-svelte
git pull origin main
```

---

### 2️⃣ Setup Environment Variables

```bash
# Copy template .env files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend/.env jika perlu (default sudah OK untuk development)
# nano backend/.env
```

**Important Environment Variables:**
```bash
# backend/.env
DJANGO_SECRET_KEY=your-secret-key-here
DATABASE_URL=postgres://postgres:postgres@db:5432/posdb
REDIS_URL=redis://redis:6379/0

# Payment Gateway Keys (Optional untuk testing dummy data)
MIDTRANS_SERVER_KEY=your-midtrans-server-key
XENDIT_SECRET_KEY=your-xendit-secret-key
XENDIT_CALLBACK_TOKEN=your-webhook-token
STRIPE_SECRET_KEY=your-stripe-key
```

---

### 3️⃣ Build & Start Docker Services

```bash
# Stop existing containers jika ada
docker-compose down

# Build dari scratch dengan force rebuild
docker-compose build --no-cache

# Start semua services
docker-compose up -d

# Cek status semua containers
docker-compose ps
```

**Expected Output:**
```
NAME                COMMAND                  STATUS              PORTS
kiosk-backend       "gunicorn config.wsg…"   Up 30 seconds       0.0.0.0:8000->8000/tcp
kiosk-frontend      "docker-entrypoint.s…"   Up 30 seconds       0.0.0.0:5173->5173/tcp
kiosk-db            "docker-entrypoint.s…"   Up 30 seconds       5432/tcp
kiosk-redis         "redis-server"           Up 30 seconds       6379/tcp
kiosk-celery        "celery -A config wo…"   Up 30 seconds       
kiosk-nginx         "nginx -g 'daemon of…"   Up 30 seconds       0.0.0.0:80->80/tcp
```

---

### 4️⃣ Database Setup

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: admin123 (atau password pilihan Anda)

# Seed dummy data (20 products, 5 categories, 2 users)
docker-compose exec backend python manage.py seed_demo_data
```

**Dummy Data yang akan dibuat:**
- ✅ **1 Tenant**: Warung Makan Sedap
- ✅ **2 Outlets**: Cabang Jakarta Selatan, Cabang Bandung
- ✅ **5 Categories**: Makanan Utama, Minuman Dingin, Minuman Panas, Snack, Dessert
- ✅ **20 Products**: Nasi Goreng (Rp 35,000), Mie Goreng (Rp 32,000), Es Teh Manis (Rp 8,000), dll.
- ✅ **Product Modifiers**: Extra Telur (+Rp 5,000), Level Pedas (Normal/Sedang/Pedas/Extra Pedas)
- ✅ **2 Users**: admin/admin123, cashier/cashier123

---

### 5️⃣ Verify Deployment

```bash
# Check logs untuk error
docker-compose logs -f backend
docker-compose logs -f frontend

# Test backend API
curl http://localhost:8000/api/health
# Expected: {"status":"ok","timestamp":"..."}

# Test frontend
curl http://localhost:5173
# Expected: HTML response
```

---

## 🌐 Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| **🖥️ Kiosk Mode** | `http://localhost:5173/kiosk` | - |
| **👤 Admin Panel** | `http://localhost:8000/admin` | `admin` / `admin123` |
| **📖 API Docs (Swagger)** | `http://localhost:8000/api/docs` | - |
| **📋 API Schema** | `http://localhost:8000/api/schema` | - |
| **🔌 Backend API** | `http://localhost:8000/api` | JWT Required |

---

## 🧪 Testing Kiosk Mode

1. **Buka Kiosk Mode**: `http://localhost:5173/kiosk`
2. **Tekan F11**: Untuk fullscreen mode
3. **Browse Products**: 20 dummy products sudah tersedia
4. **Filter by Category**: Tap kategori (Makanan Utama, Minuman, dll.)
5. **Add to Cart**: Tap product card untuk add to cart
6. **Update Quantity**: Use +/- buttons di cart
7. **View Totals**: 
   - Subtotal
   - Tax (10% auto-calculated)
   - Service Charge (5% auto-calculated)
   - Grand Total
8. **Test Offline Mode**: 
   - Disconnect internet
   - App tetap berfungsi dengan IndexedDB
   - Data sync otomatis saat online kembali

---

## 🔧 Troubleshooting

### ❌ Port Already in Use

```bash
# Jika port 5173, 8000, atau 80 sudah dipakai
docker-compose down
sudo lsof -ti:5173 | xargs kill -9
sudo lsof -ti:8000 | xargs kill -9
sudo lsof -ti:80 | xargs kill -9
docker-compose up -d
```

### ❌ Backend Container Crash

```bash
# Check logs untuk error detail
docker-compose logs backend

# Rebuild backend container
docker-compose build --no-cache backend
docker-compose up -d
```

### ❌ Frontend Build Error

```bash
# Check logs
docker-compose logs frontend

# Rebuild frontend container
docker-compose build --no-cache frontend
docker-compose up -d
```

### ❌ Database Connection Error

```bash
# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db

# Verify database is ready
docker-compose exec db psql -U postgres -d posdb -c "\dt"
```

### ❌ Permission Denied Error

```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Restart containers
docker-compose down
docker-compose up -d
```

---

## 🔄 Update Process (Git Pull)

```bash
# Stop containers
docker-compose down

# Pull latest changes
git pull origin main

# Rebuild & restart
docker-compose build --no-cache
docker-compose up -d

# Run new migrations
docker-compose exec backend python manage.py migrate

# Restart services
docker-compose restart
```

---

## 🛑 Stop & Clean Up

```bash
# Stop all containers
docker-compose down

# Stop & remove volumes (CAUTION: Database will be deleted)
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Complete cleanup (remove everything)
docker-compose down -v --rmi all --remove-orphans
```

---

## 📊 Service Status Check

```bash
# Check all containers status
docker-compose ps

# Check specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
docker-compose logs -f redis
docker-compose logs -f celery

# Check resource usage
docker stats
```

---

## 🔐 Payment Gateway Integration (Optional)

### Xendit Setup
```bash
# Edit backend/.env
XENDIT_SECRET_KEY=xnd_development_yourkey
XENDIT_CALLBACK_TOKEN=your_webhook_token
```

**Test QRIS Payment:**
```python
from apps.payments.xendit_client import get_xendit_client

client = get_xendit_client()
qris = client.create_qris_payment(
    amount=100000,  # Rp 100,000
    external_id="ORDER-001",
    callback_url="http://yourdomain.com/api/payments/xendit/callback"
)
print(qris['qr_string'])  # Base64 QR code image
```

### Midtrans Setup
```bash
# Edit backend/.env
MIDTRANS_SERVER_KEY=SB-Mid-server-yourkey
MIDTRANS_CLIENT_KEY=SB-Mid-client-yourkey
```

**Test Snap Transaction:**
```python
from apps.payments.midtrans_client import get_midtrans_client

client = get_midtrans_client(is_production=False)
snap = client.create_snap_transaction(
    order_id="ORDER-001",
    gross_amount=100000,
    customer_name="John Doe",
    customer_email="john@example.com",
    customer_phone="081234567890"
)
print(snap['redirect_url'])  # Payment page URL
```

---

## 📈 Next Steps

1. ✅ **Docker Build Fixed** - Ready to deploy
2. ⚠️ **REST API Endpoints** - Create ViewSets & Serializers
3. ⚠️ **Payment Integration** - Implement webhook handlers
4. ⚠️ **Kitchen Display System** - WebSocket real-time updates
5. ⚠️ **User Authentication** - JWT login/logout endpoints
6. ⚠️ **Reports & Analytics** - Sales reports, inventory tracking

---

## 📞 Support

**GitHub Repository**: [https://github.com/dadinjaenudin/kiosk-svelte](https://github.com/dadinjaenudin/kiosk-svelte)

**Latest Commit**: `d5d31e9` - Fix xendit SDK, implement REST API clients

**Status**: ✅ **DOCKER BUILD FIXED - READY TO DEPLOY**

---

**Happy Coding! 🚀**
