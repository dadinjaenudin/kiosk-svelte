# 🛠️ Development Setup Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start (Docker)](#quick-start-docker)
- [Local Development (Non-Docker)](#local-development-non-docker)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Development Workflow](#development-workflow)
- [Debugging](#debugging)
- [Common Issues](#common-issues)

---

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| **Docker** | 20.x+ | Container runtime |
| **Docker Compose** | 2.x+ | Multi-container orchestration |
| **Node.js** | 18.x+ | Frontend development |
| **Python** | 3.11+ | Backend development |
| **PostgreSQL** | 15+ | Database (if not using Docker) |
| **Git** | 2.x+ | Version control |

### Install Docker (Recommended)

**Windows**:
```powershell
# Download Docker Desktop from docker.com
# Install and restart

# Verify installation
docker --version
docker-compose --version
```

**Mac**:
```bash
# Using Homebrew
brew install --cask docker

# Or download Docker Desktop
# Verify
docker --version
```

**Linux**:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# Start service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
```

### Install Node.js

**Windows/Mac**:
- Download from [nodejs.org](https://nodejs.org/)
- Install LTS version (18.x or 20.x)

**Linux**:
```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

**Verify**:
```bash
node --version  # Should show v18.x or v20.x
npm --version   # Should show 9.x or 10.x
```

### Install Python

**Windows**:
- Download from [python.org](https://www.python.org/)
- Install Python 3.11+
- Check "Add to PATH"

**Mac**:
```bash
brew install python@3.11
```

**Linux**:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Verify**:
```bash
python --version  # or python3 --version
pip --version
```

---

## Quick Start (Docker)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/pos-fnb-system.git
cd pos-fnb-system
```

### 2. Create Environment File

```bash
# Copy example env file
cp backend/.env.example backend/.env

# Edit with your values (optional for development)
# nano backend/.env  # Linux/Mac
# notepad backend\.env  # Windows
```

**Minimal `.env` for Development**:
```env
# Django
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,backend,*

# Database
DATABASE_NAME=pos_db
DATABASE_USER=pos_user
DATABASE_PASSWORD=pos_password_2024
DATABASE_HOST=db
DATABASE_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 3. Build and Start Containers

```bash
# Build images and start all services
docker-compose up --build

# Or run in background (detached mode)
docker-compose up -d --build
```

**First time startup** will:
- Pull base images (PostgreSQL, Redis, etc.)
- Build backend & frontend images
- Run database migrations
- Collect static files
- Start all services

**Wait for**:
```
✅ kiosk_pos_db        | database system is ready
✅ kiosk_pos_redis     | Ready to accept connections
✅ kiosk_pos_backend   | Booting worker with pid
✅ kiosk_pos_frontend  | ready in 3421 ms
```

### 4. Create Superuser

```bash
# In new terminal
docker-compose exec backend python manage.py createsuperuser

# Follow prompts:
# Username: admin
# Email: admin@example.com
# Password: ********
```

### 5. Load Sample Data (Optional)

```bash
# Load test data for multi-tenant setup
docker-compose exec backend python manage.py setup_multi_outlet_test_data.py

# This creates:
# - 3 tenants (restaurant brands)
# - 2-3 outlets per tenant
# - Products, categories
# - Sample users
```

### 6. Access Application

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend (Kiosk)** | http://localhost:5173 | No auth required |
| **Admin Panel** | http://localhost:5173/admin | Use created superuser |
| **Kitchen Display** | http://localhost:5173/kitchen | No auth required |
| **Backend API** | http://localhost:8001/api/ | API endpoints |
| **API Docs (Swagger)** | http://localhost:8001/api/docs/ | Interactive API docs |
| **Django Admin** | http://localhost:8001/admin/ | Use superuser |

### 7. Stop Services

```bash
# Stop containers (preserves data)
docker-compose stop

# Stop and remove containers (keeps volumes)
docker-compose down

# Stop and remove everything including volumes (⚠️ deletes data)
docker-compose down -v
```

---

## Local Development (Non-Docker)

For development without Docker (better performance, easier debugging).

### 1. Setup PostgreSQL

**Install PostgreSQL 15**:

```bash
# Mac
brew install postgresql@15
brew services start postgresql@15

# Linux
sudo apt install postgresql-15

# Windows
# Download from postgresql.org
```

**Create Database**:

```sql
-- Connect to postgres
psql -U postgres

-- Create user and database
CREATE USER pos_user WITH PASSWORD 'pos_password_2024';
CREATE DATABASE pos_db OWNER pos_user;
GRANT ALL PRIVILEGES ON DATABASE pos_db TO pos_user;

-- Exit
\q
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env for local setup
# DATABASE_HOST=localhost
# DATABASE_PORT=5432
# REDIS_URL=redis://localhost:6379/0
```

**Run Migrations**:

```bash
python manage.py makemigrations
python manage.py migrate
```

**Create Superuser**:

```bash
python manage.py createsuperuser
```

**Load Sample Data**:

```bash
python setup_multi_outlet_test_data.py
```

**Run Development Server**:

```bash
# Start Django server
python manage.py runserver 0.0.0.0:8000

# Server runs at http://localhost:8000
```

### 3. Setup Redis (for Celery)

**Install Redis**:

```bash
# Mac
brew install redis
brew services start redis

# Linux
sudo apt install redis-server
sudo systemctl start redis

# Windows
# Download from https://github.com/microsoftarchive/redis/releases
```

**Start Celery Worker** (in new terminal):

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

celery -A config worker -l info
```

**Start Celery Beat** (in new terminal):

```bash
cd backend
source venv/bin/activate

celery -A config beat -l info
```

### 4. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env
# VITE_API_URL=http://localhost:8000
```

**Run Development Server**:

```bash
npm run dev

# Server runs at http://localhost:5173
```

### 5. Development Servers Running

You should now have:

```
✅ PostgreSQL     - localhost:5432
✅ Redis          - localhost:6379
✅ Django Backend - localhost:8000
✅ Celery Worker  - Running in background
✅ Celery Beat    - Running in background
✅ Vite Frontend  - localhost:5173
```

---

## Environment Configuration

### Backend Environment Variables

```env
# backend/.env

# Django Core
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,*

# Database
DATABASE_NAME=pos_db
DATABASE_USER=pos_user
DATABASE_PASSWORD=pos_password_2024
DATABASE_HOST=localhost  # or 'db' for Docker
DATABASE_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0  # or redis://redis:6379/0 for Docker

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Payment Gateways (optional)
MIDTRANS_SERVER_KEY=your-midtrans-server-key
MIDTRANS_CLIENT_KEY=your-midtrans-client-key
MIDTRANS_IS_PRODUCTION=False

XENDIT_SECRET_KEY=your-xendit-secret-key
XENDIT_WEBHOOK_TOKEN=your-xendit-webhook-token

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Frontend Environment Variables

```env
# frontend/.env

# API URL
VITE_API_URL=http://localhost:8000

# Public API URL (for SSR)
VITE_PUBLIC_API_URL=http://localhost:8000

# App Config
VITE_APP_NAME=POS F&B System
VITE_APP_VERSION=1.0.0

# Feature Flags
VITE_ENABLE_PWA=true
VITE_ENABLE_OFFLINE=true
VITE_ENABLE_ANALYTICS=false
```

---

## Database Setup

### Initial Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Load Test Data

**Option 1: Multi-Tenant Test Data**

```bash
python setup_multi_outlet_test_data.py
```

This creates:
- 3 Tenants (Ayam Geprek, Kopi Kenangan, Bakso)
- 2-3 Outlets per tenant
- 10+ Products per tenant
- Categories
- Sample users (admin, cashier, kitchen)

**Option 2: Manual Data Entry**

Access Django Admin: http://localhost:8000/admin/

Create:
1. Tenant (brand)
2. Outlet (location)
3. Categories
4. Products
5. Users

### Reset Database

```bash
# Drop and recreate database
python manage.py flush

# Or drop database and migrate fresh
dropdb -U pos_user pos_db
createdb -U pos_user pos_db
python manage.py migrate
```

---

## Running the Application

### Docker Development

```bash
# Start all services
docker-compose up

# Start specific service
docker-compose up backend
docker-compose up frontend

# Rebuild after code changes
docker-compose up --build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Execute commands in container
docker-compose exec backend python manage.py shell
docker-compose exec backend python manage.py migrate
```

### Local Development

**Terminal 1 - Backend**:
```bash
cd backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

**Terminal 2 - Celery Worker**:
```bash
cd backend
source venv/bin/activate
celery -A config worker -l info
```

**Terminal 3 - Celery Beat** (optional):
```bash
cd backend
source venv/bin/activate
celery -A config beat -l info
```

**Terminal 4 - Frontend**:
```bash
cd frontend
npm run dev
```

---

## Development Workflow

### Daily Workflow

1. **Start development servers**
   ```bash
   docker-compose up  # or start services manually
   ```

2. **Make code changes**
   - Backend: Edit Python files (auto-reload enabled)
   - Frontend: Edit Svelte files (HMR enabled)

3. **Test changes**
   - Backend: http://localhost:8000
   - Frontend: http://localhost:5173

4. **Run tests** (if available)
   ```bash
   # Backend tests
   docker-compose exec backend python manage.py test
   
   # Frontend tests
   cd frontend
   npm run test
   ```

5. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push
   ```

### Code Hot Reload

**Backend** (Django):
- Auto-reloads when Python files change
- Restart required for settings.py changes
- Restart: `Ctrl+C` then `python manage.py runserver`

**Frontend** (Vite):
- Hot Module Replacement (HMR) enabled
- Changes apply instantly without page reload
- Full reload for config changes

### Database Changes

```bash
# After modifying models.py

# 1. Create migration
python manage.py makemigrations

# 2. Review migration
python manage.py showmigrations

# 3. Apply migration
python manage.py migrate

# 4. For Docker
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

---

## Debugging

### Backend Debugging

**Django Debug Toolbar**:

```python
# backend/config/settings.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
```

Access at: http://localhost:8000/ (toolbar on right side)

**Print Debugging**:

```python
# In views.py
def my_view(request):
    print("Debug:", request.data)  # Logs to console
    import pdb; pdb.set_trace()    # Breakpoint
```

**VS Code Launch Configuration**:

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Django",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/manage.py",
      "args": ["runserver", "0.0.0.0:8000"],
      "django": true,
      "justMyCode": false
    }
  ]
}
```

### Frontend Debugging

**Browser DevTools**:
- Open DevTools (F12)
- Console tab for logs
- Network tab for API calls
- Application tab for IndexedDB

**Svelte DevTools**:
- Install Chrome/Firefox extension
- Inspect Svelte components
- View store values

**Console Logging**:

```javascript
// In component
console.log('Cart items:', $cartItems);
console.table($cartItems);  // Table format
```

---

## Common Issues

### Issue 1: Port Already in Use

**Error**: `Port 8000 is already allocated`

**Solution**:
```bash
# Find process using port
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /F /PID <PID>  # Windows

# Or change port in docker-compose.yml
ports:
  - "8001:8000"
```

### Issue 2: Database Connection Error

**Error**: `FATAL: password authentication failed`

**Solution**:
```bash
# Verify credentials in .env
# Recreate database
docker-compose down -v
docker-compose up -d db
docker-compose exec backend python manage.py migrate
```

### Issue 3: Node Modules Not Found

**Error**: `Cannot find module 'svelte'`

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue 4: Migration Conflicts

**Error**: `Conflicting migrations detected`

**Solution**:
```bash
# Reset migrations (⚠️ development only)
python manage.py migrate --fake-initial
# Or
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

### Issue 5: CORS Errors

**Error**: `Access-Control-Allow-Origin missing`

**Solution**:
```python
# backend/config/settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:3000',
]
CORS_ALLOW_CREDENTIALS = True
```

---

## Next Steps

After setup, explore:

- **[BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md)** - Backend code structure
- **[FRONTEND_ARCHITECTURE.md](FRONTEND_ARCHITECTURE.md)** - Frontend code structure
- **[CODING_STANDARDS.md](CODING_STANDARDS.md)** - Coding conventions
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Writing tests

---

**Last Updated**: January 3, 2026
