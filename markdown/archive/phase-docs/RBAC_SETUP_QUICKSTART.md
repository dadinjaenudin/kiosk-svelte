# Quick Start: RBAC Test Data Setup

## 🚀 Quick Commands

### Windows PowerShell (Recommended)
```powershell
# Interactive mode
docker-compose exec backend python setup_rbac_test_data.py

# Or run the helper script
.\setup_rbac_test_docker.ps1
```

### Windows Command Prompt
```batch
# Interactive mode
docker-compose exec backend python setup_rbac_test_data.py

# Or run the helper script
setup_rbac_test_docker.bat
```

### Linux/Mac (Bash)
```bash
# Interactive mode
docker-compose exec backend python setup_rbac_test_data.py

# Or run the helper script
./setup_rbac_test_docker.sh
```

### Auto-Confirm (Skip prompt)
```powershell
# PowerShell
docker-compose exec backend sh -c "echo 'yes' | python setup_rbac_test_data.py"

# Or with Python
docker-compose exec -T backend python -c "
import sys
sys.stdin = open('/dev/stdin')
exec(open('setup_rbac_test_data.py').read().replace('input(', 'lambda x: \"yes\" # '))
"
```

---

## 📝 What Happens

1. **Clears existing data** (except superuser)
2. **Creates 3 tenants:**
   - Pizza Paradise (pizza-paradise)
   - Burger Station (burger-station)
   - Noodle House (noodle-house)

3. **Creates 11 test users:**
   - `superadmin` / `admin123` (super_admin)
   - `admin` / `admin123` (admin)
   - `pizza_manager` / `manager123` (manager)
   - `pizza_cashier` / `cashier123` (cashier)
   - `pizza_kitchen` / `kitchen123` (kitchen)
   - `burger_manager` / `manager123` (manager)
   - `burger_cashier` / `cashier123` (cashier)
   - `burger_kitchen` / `kitchen123` (kitchen)
   - `noodle_manager` / `manager123` (manager)
   - `noodle_cashier` / `cashier123` (cashier)
   - `noodle_kitchen` / `kitchen123` (kitchen)

4. **Creates sample data:**
   - Categories per tenant
   - Products per tenant
   - Promotions per tenant

---

## 🔍 Verify Setup

### Check containers are running
```bash
docker-compose ps
```

### Check backend logs
```bash
docker-compose logs backend
```

### Test backend API
```powershell
Invoke-WebRequest -Uri http://localhost:8001/api/health/ -UseBasicParsing
```

### Access admin panel
```
http://localhost:5175/
```

---

## 🐛 Troubleshooting

### Container not running
```bash
docker-compose up -d
docker-compose ps
```

### Database connection error
```bash
# Restart database container
docker-compose restart db
docker-compose logs db
```

### Permission denied (Linux/Mac)
```bash
chmod +x setup_rbac_test_docker.sh
./setup_rbac_test_docker.sh
```

### Script not found
```bash
# Make sure you're in the project root
cd /path/to/kiosk-svelte
docker-compose exec backend python setup_rbac_test_data.py
```

---

## 📚 Next Steps

After setup is complete:

1. **Access admin panel:** http://localhost:5175/
2. **Login with test accounts** (see above)
3. **Follow testing guide:** [RBAC_TESTING_GUIDE.md](./markdown/RBAC_TESTING_GUIDE.md)

---

## 🔄 Reset Data

To reset and run again:

```bash
# PowerShell
docker-compose exec backend python setup_rbac_test_data.py

# Auto-confirm
docker-compose exec backend sh -c "echo 'yes' | python setup_rbac_test_data.py"
```

---

## ✅ Success Output

You should see:
```
🗑️  Clearing existing data...
✅ All test data cleared

🏢 Creating tenants...
  ✓ Created: Pizza Paradise (PIZZA)
  ✓ Created: Burger Station (BURGER)
  ✓ Created: Noodle House (NOODLE)

👥 Creating users...
  ✓ Created: superadmin (super_admin) - Access: ALL TENANTS
  ...

📁 Creating categories...
  ...

🍕 Creating products...
  ...

🎉 Creating promotions...
  ...

🎯 RBAC TESTING DATA SETUP COMPLETE
✨ Ready for RBAC testing!
```
