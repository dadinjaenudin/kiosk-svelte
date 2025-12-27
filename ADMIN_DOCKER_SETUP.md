# 🐳 Admin Panel Docker Setup

## 📋 Overview

Admin Panel sekarang bisa dijalankan dengan **2 cara**:
1. **Docker** - Production-like environment (Recommended untuk testing deployment)
2. **Local NPM** - Faster development with hot reload

---

## 🚀 Option 1: Docker (Recommended)

### Quick Start
```bash
# Di: D:\YOGYA-Kiosk\kiosk-svelte

# Pull latest code
git pull origin main

# Build and start ALL services (backend, frontend, admin)
docker-compose up --build

# OR start only admin
docker-compose up --build admin
```

### Using START_ADMIN.bat (Windows)
```bash
# Double-click START_ADMIN.bat
# Choose: [1] Docker

# OR run from terminal
START_ADMIN.bat
```

### Manual Docker Commands
```bash
# Build admin service
docker-compose build admin

# Start admin service (with logs)
docker-compose up admin

# Start admin service (detached/background)
docker-compose up -d admin

# View logs
docker-compose logs admin -f

# Stop admin service
docker-compose stop admin

# Restart admin service
docker-compose restart admin

# Remove admin container
docker-compose down admin
```

### Expected Output
```
kiosk_pos_admin | 
kiosk_pos_admin | > admin@0.0.1 dev
kiosk_pos_admin | > vite dev --host 0.0.0.0
kiosk_pos_admin | 
kiosk_pos_admin | VITE v5.0.10  ready in 1523 ms
kiosk_pos_admin | 
kiosk_pos_admin |   ➜  Local:   http://localhost:5173/
kiosk_pos_admin |   ➜  Network: http://0.0.0.0:5173/
```

**Access**: http://localhost:5175/ (mapped to container port 5173)

---

## 💻 Option 2: Local NPM (Faster Development)

### Quick Start
```bash
# Make sure backend is running in Docker
docker-compose up -d backend

# Install dependencies (first time only)
cd admin
npm install

# Start dev server
npm run dev
```

### Using START_ADMIN.bat (Windows)
```bash
# Double-click START_ADMIN.bat
# Choose: [2] Local NPM

# OR run from terminal
START_ADMIN.bat
```

### Benefits
- ⚡ **Faster hot reload** (no Docker layer)
- 🛠️ **Better debugging** (direct Node.js logs)
- 📦 **Easier npm package management**

**Access**: http://localhost:5175/

---

## 📦 Docker Services Overview

```yaml
services:
  db: PostgreSQL database (port 5433)
  redis: Redis cache (port 6380)
  backend: Django API (port 8001)
  celery_worker: Background tasks
  celery_beat: Scheduled tasks
  frontend: Kiosk app (port 5174)
  admin: Admin panel (port 5175)  # ← NEW!
  nginx: Reverse proxy (port 8082)
```

---

## 🧪 Testing Both Methods

### Test Docker Method
```bash
# Start admin with Docker
docker-compose up admin

# Open browser
http://localhost:5175/

# Login: admin / admin123

# Check logs
docker-compose logs admin -f
```

### Test Local NPM Method
```bash
# Make sure Docker admin is stopped
docker-compose stop admin

# Start local admin
cd admin
npm run dev

# Open browser
http://localhost:5175/

# Login: admin / admin123

# Check logs in terminal
```

---

## 🔄 Switching Between Methods

### From Docker to Local
```bash
# Stop Docker admin
docker-compose stop admin

# Start local admin
cd admin
npm run dev
```

### From Local to Docker
```bash
# Stop local admin (Ctrl+C in terminal)

# Start Docker admin
docker-compose up -d admin
```

---

## 🐛 Troubleshooting

### Problem 1: Port 5175 Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :5175

# Stop Docker admin if running
docker-compose stop admin

# OR kill the process
taskkill /PID <PID> /F

# Then restart
docker-compose up admin
```

### Problem 2: Admin Container Won't Start
```bash
# Check logs
docker-compose logs admin

# Common issues:
# - Node modules not installed
# - Port conflict
# - Syntax error in code

# Rebuild from scratch
docker-compose build --no-cache admin
docker-compose up admin
```

### Problem 3: "Cannot connect to backend"
```bash
# Check backend is running
docker-compose ps backend

# Should show: Up (healthy)

# If not, start backend
docker-compose up -d backend

# Wait 20 seconds for backend to be healthy
timeout /t 20
```

### Problem 4: Hot Reload Not Working in Docker
```bash
# This is expected behavior in Docker
# Solution: Use Local NPM method for development

# Stop Docker admin
docker-compose stop admin

# Use local NPM
cd admin
npm run dev
```

### Problem 5: CORS Errors
```bash
# Backend already configured for port 5175
# Just restart backend
docker-compose restart backend

# Hard refresh browser
Ctrl+Shift+R
```

---

## 📊 Resource Usage Comparison

| Method | Pros | Cons |
|--------|------|------|
| **Docker** | ✅ Production-like<br>✅ Isolated environment<br>✅ Easy deployment | ❌ Slower hot reload<br>❌ More resource usage<br>❌ Harder debugging |
| **Local NPM** | ✅ Fast hot reload<br>✅ Less resources<br>✅ Better debugging | ❌ Need Node.js installed<br>❌ Not production-like |

---

## 🎯 Recommended Workflow

### For Development
```bash
# Use Local NPM (faster)
cd admin
npm run dev
```

### For Testing Deployment
```bash
# Use Docker (production-like)
docker-compose up admin
```

### For Full Stack Testing
```bash
# Run everything in Docker
docker-compose up --build
```

**Services Running:**
- Backend API: http://localhost:8001/api/
- Kiosk Frontend: http://localhost:5174/kiosk
- Admin Panel: http://localhost:5175/
- Nginx: http://localhost:8082/

---

## 📁 Docker Files Added

```
admin/
├── Dockerfile           # ← NEW! Docker build instructions
├── .dockerignore        # ← NEW! Files to ignore in build
├── package.json
├── vite.config.js
└── src/
    └── ...

docker-compose.yml       # ← UPDATED! Added admin service
```

---

## 🔧 Environment Variables

### Docker (Auto-configured)
```yaml
environment:
  - NODE_ENV=development
  - PUBLIC_API_URL=http://localhost:8001/api
```

### Local NPM (Uses vite.config.js proxy)
```javascript
// Already configured in vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:8001',
    changeOrigin: true
  }
}
```

---

## 📝 Common Commands Cheat Sheet

### Docker Commands
```bash
# Start all services
docker-compose up

# Start with rebuild
docker-compose up --build

# Start only admin
docker-compose up admin

# Start in background
docker-compose up -d admin

# Stop admin
docker-compose stop admin

# View logs
docker-compose logs admin -f

# Restart admin
docker-compose restart admin

# Remove admin container
docker-compose down admin

# Rebuild admin
docker-compose build --no-cache admin
```

### Local NPM Commands
```bash
# Install dependencies
cd admin && npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## ✅ Success Criteria

### Docker Method Working
- ✅ `docker-compose up admin` starts without errors
- ✅ Logs show "VITE ready in X ms"
- ✅ http://localhost:5175/ loads login page
- ✅ Can login with admin/admin123
- ✅ No CORS errors in console

### Local NPM Working
- ✅ `npm run dev` starts without errors
- ✅ Console shows "Local: http://localhost:5175/"
- ✅ Login page loads
- ✅ Can authenticate successfully
- ✅ Hot reload works on file changes

---

## 🆘 Need Help?

### Check All Services Status
```bash
docker-compose ps
```

Expected output:
```
NAME                    STATUS
kiosk_pos_admin         Up
kiosk_pos_backend       Up (healthy)
kiosk_pos_db            Up (healthy)
kiosk_pos_frontend      Up
kiosk_pos_redis         Up (healthy)
```

### Check Admin Container Logs
```bash
docker-compose logs admin --tail=50
```

### Access Admin Container Shell
```bash
docker-compose exec admin sh

# Inside container
ls -la
cat package.json
exit
```

---

**Last Updated**: 2025-12-27  
**Version**: Docker Integration Complete
