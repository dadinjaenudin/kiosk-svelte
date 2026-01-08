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

docker-compose logs frontend --tail=50
docker-compose restart frontend
docker-compose restart admin

docker-compose down frontend; docker-compose up -d frontend
docker-compose build frontend; docker-compose up -d frontend

Untuk ke depannya, jika ada masalah dependency:
docker-compose build frontend
docker-compose up -d frontend

Start-Sleep -Seconds 15; docker-compose logs frontend --tail=20
Start-Sleep -Seconds 10; docker-compose logs frontend --tail=15 | Select-String "error|ready" | Select-Object -Last 5
docker-compose logs frontend 2>&1 | Select-String "ready in|error" | Select-Object -Last 3

## 🌐 URLs PENTING

### Frontend (Port 5174)
- **Kiosk:** http://localhost:5174/kiosk
- **Kitchen Login:** http://localhost:5174/kitchen/login
- **Kitchen Display:** http://localhost:5174/kitchen/display
- **Admin Panel:** http://localhost:5175/ (Port 5175)

### Backend (Port 8001)
- **API Docs:** http://localhost:8001/api/docs/
- **Django Admin:** http://localhost:8001/admin/
- **Health Check:** http://localhost:8001/api/health/

### GitHub
- **Repository:** https://github.com/dadinjaenudin/kiosk-svelte

---

## 🔧 Troubleshooting

### Kitchen Routes Return 404
**Problem:** `/kitchen/login` or `/kitchen/display` returns 404

**Solution:**
```bash
# Restart frontend container to load new routes
docker-compose restart frontend

# Wait for Vite to be ready (10-15 seconds)
Start-Sleep -Seconds 10

# Check logs
docker-compose logs frontend --tail=20

# Test access
curl http://localhost:5174/kitchen/login
```

### Frontend Not Loading Changes
**Problem:** Code changes not reflected in browser

**Solution:**
```bash
# Full rebuild
docker-compose down frontend
docker-compose build frontend --no-cache
docker-compose up -d frontend

# Or restart with clear cache
docker-compose restart frontend
```

### API Connection Refused
**Problem:** Frontend shows "connect ECONNREFUSED"

**Solution:**
```bash
# Check backend health
docker-compose ps
docker-compose logs backend --tail=20

# Restart backend if needed
docker-compose restart backend
```
