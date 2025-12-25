# 🔧 Port Configuration Update

## Changed Ports to Avoid Conflicts

### External Ports (Host Machine)

| Service | Old Port | New Port | Internal Port |
|---------|----------|----------|---------------|
| **PostgreSQL** | 5432 | **5433** | 5432 |
| **Redis** | 6379 | **6380** | 6379 |
| **Backend API** | 8000 | **8001** | 8000 |
| **Frontend** | 5173 | **5174** | 5173 |
| **Nginx HTTP** | 80 | **8080** | 80 |
| **Nginx HTTPS** | 443 | **8443** | 443 |

### Container Names (Renamed)

| Service | Old Name | New Name |
|---------|----------|----------|
| Database | `pos_db` | `kiosk_pos_db` |
| Redis | `pos_redis` | `kiosk_pos_redis` |
| Backend | `pos_backend` | `kiosk_pos_backend` |
| Frontend | `pos_frontend` | `kiosk_pos_frontend` |
| Celery Worker | `pos_celery_worker` | `kiosk_pos_celery_worker` |
| Celery Beat | `pos_celery_beat` | `kiosk_pos_celery_beat` |
| Nginx | `pos_nginx` | `kiosk_pos_nginx` |

---

## 🌐 Updated Access URLs

| Service | URL |
|---------|-----|
| **🖥️ Kiosk Mode** | `http://localhost:5174/kiosk` |
| **👤 Admin Panel** | `http://localhost:8001/admin` |
| **📖 API Docs** | `http://localhost:8001/api/docs` |
| **🔌 Backend API** | `http://localhost:8001/api` |
| **🌐 Nginx Proxy** | `http://localhost:8080` |

---

## 📝 What Changed

### 1. **docker-compose.yml**
- Updated all external port mappings
- Renamed all container names with `kiosk_pos_` prefix
- Updated frontend environment variables

### 2. **frontend/.env.example**
- `PUBLIC_API_URL=http://localhost:8001/api`
- `PUBLIC_WS_URL=ws://localhost:8001/ws`

### 3. **Internal Docker Network**
- No changes needed (containers still communicate on internal network)
- `db:5432`, `redis:6379`, `backend:8000` remain the same internally

---

## 🚀 Deployment with New Ports

```bash
# Pull latest changes
cd kiosk-svelte
git pull origin main

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Build and start
docker-compose build --no-cache
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py seed_demo_data

# Check status
docker-compose ps
```

---

## 🔍 Verify Services

```bash
# Check PostgreSQL
docker-compose exec db psql -U pos_user -d pos_db -c "SELECT version();"

# Check Redis
docker-compose exec redis redis-cli ping

# Check Backend API
curl http://localhost:8001/api/health

# Check Frontend
curl http://localhost:5174

# Check Nginx
curl http://localhost:8080/health
```

---

## 💡 Why These Ports?

- **Port 5432** → **5433**: PostgreSQL default port may be in use
- **Port 6379** → **6380**: Redis default port may be in use
- **Port 8000** → **8001**: Common Django dev server port conflict
- **Port 5173** → **5174**: Vite dev server may be running elsewhere
- **Port 80** → **8080**: Requires root privileges, 8080 is standard alternative
- **Port 443** → **8443**: Requires root privileges and SSL cert

---

## 🔗 Database Connection Strings

### From Host Machine (Local Development)
```bash
# PostgreSQL
postgresql://pos_user:pos_password_2024@localhost:5433/pos_db

# Redis
redis://localhost:6380/0
```

### From Docker Containers (Internal Network)
```bash
# PostgreSQL
postgresql://pos_user:pos_password_2024@db:5432/pos_db

# Redis
redis://redis:6379/0
```

---

## 📊 Quick Test Commands

```bash
# Test DB connection from host
psql -h localhost -p 5433 -U pos_user -d pos_db

# Test Redis from host
redis-cli -h localhost -p 6380 ping

# Test Backend API
curl http://localhost:8001/api/health

# Test Frontend
curl http://localhost:5174

# View all container logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## 🛠️ Troubleshooting

### If ports are still in use:

```bash
# Check what's using port
lsof -i :5433  # PostgreSQL
lsof -i :6380  # Redis
lsof -i :8001  # Backend
lsof -i :5174  # Frontend
lsof -i :8080  # Nginx

# Kill process using port
kill -9 $(lsof -ti:5433)
```

### If old containers conflict:

```bash
# Stop and remove old containers
docker stop pos_db pos_redis pos_backend pos_frontend pos_nginx
docker rm pos_db pos_redis pos_backend pos_frontend pos_nginx

# Or remove all stopped containers
docker container prune -f

# Then start fresh
docker-compose up -d
```

---

**✅ All port conflicts resolved!**
