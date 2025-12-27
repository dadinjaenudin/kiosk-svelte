# 🔧 Admin Port Configuration Fix

## 🐛 Problem
- **Docker**: Admin container crashes with `ERR_EMPTY_RESPONSE`
- **Root Cause**: Port mismatch
  - `package.json` hardcoded `--port 5175`
  - Docker exposes `5173:5175` (internal:external)
  - Container tried to bind to 5175 but Docker expects 5173

## ✅ Solution Applied

### 1. **package.json** - Dual Scripts
```json
"scripts": {
  "dev": "vite dev --host",              // For Docker (uses vite.config.js port)
  "dev:local": "vite dev --port 5175 --host",  // For local NPM
  "build": "vite build",
  "preview": "vite preview"
}
```

### 2. **vite.config.js** - Environment-aware Port
```javascript
export default defineConfig({
  plugins: [sveltekit()],
  server: {
    port: process.env.VITE_PORT || 5173,  // Docker uses 5173, local uses 5175
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8001',
        changeOrigin: true
      }
    }
  }
});
```

### 3. **docker-compose.yml** - Environment Variables
```yaml
admin:
  environment:
    - NODE_ENV=development
    - VITE_PORT=5173              # ← Container internal port
    - VITE_API_URL=http://backend:8000  # ← Docker network URL
    - PUBLIC_API_URL=http://localhost:8001/api
  ports:
    - "5175:5173"  # External:Internal
```

### 4. **START_ADMIN.bat** - Use Correct Script
```batch
# For local NPM
npm run dev:local  # Uses port 5175
```

## 📊 Port Mapping

| Mode | Container Port | Host Port | Access URL | Script |
|------|----------------|-----------|------------|--------|
| **Docker** | 5173 | 5175 | http://localhost:5175/ | `npm run dev` |
| **Local NPM** | - | 5175 | http://localhost:5175/ | `npm run dev:local` |

## 🚀 Usage

### Docker (Production-like)
```bash
# docker-compose.yml sets VITE_PORT=5173
docker-compose up --build admin

# Container binds to: 0.0.0.0:5173
# Docker maps: 5173 → 5175
# Access: http://localhost:5175/
```

### Local NPM (Development)
```bash
# Uses dev:local script with --port 5175
cd admin
npm run dev:local

# Server binds to: 0.0.0.0:5175
# Access: http://localhost:5175/
```

## 🧪 Testing

### Test Docker
```bash
# Pull latest fix
git pull origin main

# Rebuild admin
docker-compose build --no-cache admin

# Start admin
docker-compose up admin

# Expected output:
kiosk_pos_admin | VITE v5.0.10  ready in 1523 ms
kiosk_pos_admin |   ➜  Local:   http://localhost:5173/
kiosk_pos_admin |   ➜  Network: http://0.0.0.0:5173/

# Access: http://localhost:5175/ ✅
```

### Test Local NPM
```bash
cd admin
npm run dev:local

# Expected output:
VITE v5.0.10  ready in 823 ms
  ➜  Local:   http://localhost:5175/
  ➜  Network: http://0.0.0.0:5175/

# Access: http://localhost:5175/ ✅
```

## 🐛 Previous Error
```
This page isn't working
localhost didn't send any data.
ERR_EMPTY_RESPONSE
```

**Cause**: Container tried to bind to port 5175, but Docker was mapping 5173→5175, resulting in no service on 5173.

## ✅ After Fix
```
Admin login page loads correctly at http://localhost:5175/
- Docker: Container runs on 5173, mapped to host 5175
- Local: Server runs directly on 5175
```

## 📝 Checklist

Before starting admin:
- ✅ Pull latest code: `git pull origin main`
- ✅ Backend running: `docker-compose ps backend` shows "Up (healthy)"
- ✅ Port 5175 free: `netstat -ano | findstr :5175` (should be empty)

For Docker mode:
- ✅ Rebuild: `docker-compose build --no-cache admin`
- ✅ Start: `docker-compose up admin`
- ✅ Check logs: Look for "VITE ready" message
- ✅ Access: http://localhost:5175/

For Local mode:
- ✅ Install deps: `npm install` (first time)
- ✅ Start: `npm run dev:local`
- ✅ Check output: "Local: http://localhost:5175/"
- ✅ Access: http://localhost:5175/

## 🔗 Related Files
- `admin/package.json` - Scripts
- `admin/vite.config.js` - Port configuration
- `docker-compose.yml` - Environment variables
- `START_ADMIN.bat` - Startup script
- `DEBUG_ADMIN.bat` - Diagnostic tool

---

**Fixed**: 2025-12-27  
**Commit**: feat: Fix admin port configuration for Docker  
**Files Changed**: 4 (package.json, vite.config.js, docker-compose.yml, START_ADMIN.bat)
