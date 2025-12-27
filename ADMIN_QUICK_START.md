# 🚀 Admin Panel Quick Start Guide

## 📋 Prerequisites
- ✅ Docker Desktop running
- ✅ Backend container running (`docker-compose up backend`)
- ✅ Node.js installed (v18+)

## 🎯 Quick Setup (5 Minutes)

### Step 1: Pull Latest Code
```bash
# Di: D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
```

### Step 2: Install Admin Dependencies
```bash
# Masuk ke folder admin
cd admin

# Install npm packages
npm install
```

**Expected Output:**
```
added 234 packages in 45s
```

### Step 3: Backend Migration
```bash
# Kembali ke root project
cd ..

# Run migration untuk authtoken
docker-compose exec backend python manage.py migrate
```

**Expected Output:**
```
Operations to perform:
  Apply all migrations: admin, auth, authtoken, ...
Running migrations:
  Applying authtoken.0001_initial... OK
  Applying authtoken.0002_auto_20160226_1747... OK
```

### Step 4: Create Super Admin (Jika belum ada)
```bash
docker-compose exec backend python manage.py shell
```

Paste this:
```python
from apps.users.models import User
from apps.tenants.models import Tenant

# Create super admin (jika belum ada)
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
    print("✅ Super Admin already exists")

# Create Owner user untuk setiap tenant
for tenant in Tenant.objects.all():
    username = f"owner_{tenant.slug}"
    if not User.objects.filter(username=username).exists():
        owner = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password='password123',
            first_name='Owner',
            last_name=tenant.name,
            role='owner',
            tenant=tenant
        )
        print(f"✅ Owner created: {owner.username} for {tenant.name}")

print("\n🎉 All users created!")
print("\n📝 Login Credentials:")
print("   Super Admin: admin / admin123")
print("   Owners: owner_{tenant-slug} / password123")
exit()
```

**Expected Output:**
```
✅ Super Admin created: admin
✅ Owner created: owner_warung-nasi-padang for Warung Nasi Padang
✅ Owner created: owner_mie-ayam-bakso for Mie Ayam & Bakso
✅ Owner created: owner_ayam-geprek for Ayam Geprek Mantap
✅ Owner created: owner_soto-betawi-h-mamat for Soto Betawi H. Mamat
✅ Owner created: owner_nasi-goreng for Nasi Goreng Abang

🎉 All users created!

📝 Login Credentials:
   Super Admin: admin / admin123
   Owners: owner_{tenant-slug} / password123
```

### Step 5: Run Admin Dev Server
```bash
# Di folder admin
cd admin
npm run dev
```

**Expected Output:**
```
VITE v5.0.10  ready in 823 ms

  ➜  Local:   http://localhost:5175/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### Step 6: Open Admin Panel
1. Open browser: **http://localhost:5175/**
2. You should see **Login Page**
3. Login with: **admin** / **admin123**
4. You should see **Dashboard**

---

## 🧪 Testing Checklist

### ✅ Backend API Test
```bash
# Test auth endpoint
curl -X POST http://localhost:8001/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Expected Response:**
```json
{
  "token": "abc123...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "full_name": "Super Admin"
  }
}
```

### ✅ Frontend Access
1. **Login Page**: http://localhost:5175/
2. **Dashboard**: http://localhost:5175/dashboard (after login)

### ✅ Browser Console Check
Press **F12** → Console tab:
- Should NOT see CORS errors
- Should see: `✅ User authenticated: admin`

---

## 🐛 Troubleshooting

### Problem 1: Port 5175 Already in Use
```bash
# Kill existing process
netstat -ano | findstr :5175
taskkill /PID <PID> /F

# Or use different port
npm run dev -- --port 5176
```

### Problem 2: Backend Connection Refused
```bash
# Check backend is running
docker-compose ps

# If not running
docker-compose up backend -d

# Check logs
docker-compose logs backend --tail=50
```

### Problem 3: CORS Error in Console
```bash
# Restart backend after settings change
docker-compose restart backend

# Wait 10 seconds
timeout /t 10

# Hard refresh browser
# Windows: Ctrl+Shift+R
# Mac: Cmd+Shift+R
```

### Problem 4: "npm: command not found"
- Install Node.js from: https://nodejs.org/
- Restart terminal/PowerShell
- Verify: `node --version` and `npm --version`

### Problem 5: Database Migration Error
```bash
# Reset migrations
docker-compose exec backend python manage.py migrate --fake authtoken zero
docker-compose exec backend python manage.py migrate authtoken
```

---

## 📁 Project Structure

```
D:\YOGYA-Kiosk\kiosk-svelte\
├── admin/                    # ← NEW! Admin Web App
│   ├── src/
│   │   ├── routes/
│   │   │   ├── +layout.svelte
│   │   │   ├── +page.svelte
│   │   │   ├── login/
│   │   │   │   └── +page.svelte
│   │   │   └── dashboard/
│   │   │       └── +page.svelte
│   │   ├── lib/
│   │   │   ├── stores/
│   │   │   │   └── auth.js
│   │   │   └── api/
│   │   │       └── auth.js
│   │   ├── app.html
│   │   └── app.css
│   ├── package.json
│   ├── vite.config.js
│   ├── svelte.config.js
│   └── tailwind.config.js
├── frontend/                 # Existing Kiosk App
│   └── ...
├── backend/                  # Django Backend
│   ├── apps/
│   │   └── users/
│   │       ├── auth_views.py    # ← NEW!
│   │       └── auth_urls.py     # ← NEW!
│   └── config/
│       ├── settings.py          # ← UPDATED (CORS, authtoken)
│       └── urls.py              # ← UPDATED (auth routes)
└── docker-compose.yml
```

---

## 🎯 What You Should See

### Login Page (http://localhost:5175/)
![Login Page]
- Email/Username field
- Password field
- "Sign In" button
- Clean, modern UI with gradients

### Dashboard (http://localhost:5175/dashboard)
![Dashboard]
- Top navigation with user profile
- Sidebar with menu items:
  - 📊 Dashboard (active)
  - 📦 Orders
  - 👥 Customers
  - 🏷️ Promotions
  - 📈 Reports
  - ⚙️ Settings
- Main content:
  - 4 Stats Cards:
    - 💰 Today's Revenue
    - 📦 Orders Today
    - 👥 Total Customers
    - 🔥 Active Promos
  - Top Products chart
  - Recent Orders table

---

## 🔐 Demo Accounts

| Username | Password | Role | Access |
|----------|----------|------|--------|
| admin | admin123 | Super Admin | Full access |
| owner_warung-nasi-padang | password123 | Owner | Warung Nasi Padang |
| owner_mie-ayam-bakso | password123 | Owner | Mie Ayam & Bakso |
| owner_ayam-geprek | password123 | Owner | Ayam Geprek Mantap |
| owner_soto-betawi-h-mamat | password123 | Owner | Soto Betawi H. Mamat |
| owner_nasi-goreng | password123 | Owner | Nasi Goreng Abang |

---

## 📝 Common Commands

### Development
```bash
# Start admin dev server
cd admin && npm run dev

# Start backend
docker-compose up backend -d

# View backend logs
docker-compose logs backend -f

# View admin logs
# (in admin folder, npm run dev shows logs in terminal)
```

### Database
```bash
# Create migration
docker-compose exec backend python manage.py makemigrations

# Apply migration
docker-compose exec backend python manage.py migrate

# Django shell
docker-compose exec backend python manage.py shell
```

### User Management
```bash
# Create superuser
docker-compose exec backend python manage.py createsuperuser

# List users
docker-compose exec backend python manage.py shell
>>> from apps.users.models import User
>>> User.objects.all().values('username', 'role', 'tenant__name')
>>> exit()
```

---

## 🎉 Success Criteria

✅ Admin dev server running on port 5175  
✅ Backend API responding on port 8001  
✅ Login page loads without errors  
✅ Can login with admin/admin123  
✅ Dashboard displays after login  
✅ No CORS errors in browser console  
✅ User profile shows in top-right  
✅ Sidebar navigation works  

---

## 🆘 Need Help?

### Check Backend Health
```bash
curl http://localhost:8001/api/health/
```

Expected: `{"status":"ok","service":"POS Backend"}`

### Check Auth Endpoint
```bash
curl http://localhost:8001/api/auth/me/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### View All Logs
```bash
# Backend
docker-compose logs backend --tail=100

# Admin (check terminal where npm run dev is running)
```

---

## 📚 Next Steps

After successful setup:
1. ✅ **Phase 1 Complete**: Foundation ready
2. 🔄 **Phase 2**: Real data integration
   - Connect dashboard to real orders
   - Implement charts with real data
   - Add order management features
3. 🔄 **Phase 3**: Customer management
4. 🔄 **Phase 4**: Promo management

---

## 🔗 Useful Links

- **Kiosk Frontend**: http://localhost:5174/kiosk
- **Admin Panel**: http://localhost:5175/
- **Backend API**: http://localhost:8001/api/
- **API Docs**: http://localhost:8001/api/docs/
- **Django Admin**: http://localhost:8001/admin/

---

**Last Updated**: 2025-12-27  
**Version**: Phase 1 - Foundation Complete  
**Documentation**: See `PHASE1_ADMIN_COMPLETE.md` for technical details
