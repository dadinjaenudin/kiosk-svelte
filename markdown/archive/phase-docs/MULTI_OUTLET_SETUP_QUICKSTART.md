# Multi-Outlet Test Data Setup

## Quick Start

### Windows (Command Prompt)
```cmd
setup_multi_outlet_test_docker.bat
```

### Windows (PowerShell)
```powershell
.\setup_multi_outlet_test_docker.ps1
```

### Linux/Mac
```bash
bash setup_multi_outlet_test_docker.sh
```

### Manual (Docker)
```bash
docker-compose exec backend python setup_multi_outlet_test_data.py
```

---

## What Gets Created

### Tenants (3)
- **Pizza Paradise** (2 outlets: Main Branch, North Branch)
- **Burger Station** (2 outlets: Central, West)
- **Noodle House** (2 outlets: Downtown, East)

### Users (20)
#### Global Users
- `superadmin` / `admin123` - Super Admin
- `admin` / `admin123` - Admin

#### Per-Tenant Users (6 each)
- `{tenant}_owner` / `owner123` - Tenant Owner (all outlets)
- `{tenant}_manager` / `manager123` - Manager (both outlets)
- `{tenant}_cashier` / `cashier123` - Cashier (Main/Central/Downtown)
- `{tenant}_cashier2` / `cashier123` - Cashier (Branch 2)
- `{tenant}_kitchen` / `kitchen123` - Kitchen (Main/Central/Downtown)
- `{tenant}_kitchen2` / `kitchen123` - Kitchen (Branch 2)

### Products (12)
- **4 per tenant**: 2 outlet-specific + 2 shared (available at all outlets)

### Categories (9)
- **3 per tenant**: Different categories per tenant

### Promotions (3)
- **1 per tenant**: Active promotions

---

## Test Accounts

| Username | Password | Role | Access |
|----------|----------|------|--------|
| `superadmin` | `admin123` | Super Admin | All tenants & outlets |
| `admin` | `admin123` | Admin | All tenants & outlets |
| `pizza_owner` | `owner123` | Tenant Owner | Pizza Paradise - All outlets |
| `pizza_manager` | `manager123` | Manager | Pizza Paradise - Both outlets |
| `pizza_cashier` | `cashier123` | Cashier | Pizza Paradise - Main Branch |
| `burger_manager` | `manager123` | Manager | Burger Station - Both outlets |
| `noodle_cashier2` | `cashier123` | Cashier | Noodle House - East |

---

## What to Test

### 1. Tenant Owner
Login as `pizza_owner`:
- ✅ See OutletSelector with 2 outlets
- ✅ Switch between Main Branch and North Branch
- ✅ Products filter by outlet

### 2. Manager with Multiple Outlets
Login as `burger_manager`:
- ✅ See OutletSelector with accessible outlets
- ✅ Switch between Central and West
- ✅ See outlet-specific + shared products

### 3. Cashier with Single Outlet
Login as `noodle_cashier`:
- ✅ OutletSelector is HIDDEN (only 1 outlet)
- ✅ Header shows outlet badge
- ✅ Only see products for assigned outlet + shared

---

## Admin Panel
http://localhost:5175/

---

## Documentation
See `markdown/PHASE5_MULTI_OUTLET.md` for detailed documentation.

---

## ⚠️ Warning
This script will **DELETE ALL EXISTING DATA** before creating test data!
