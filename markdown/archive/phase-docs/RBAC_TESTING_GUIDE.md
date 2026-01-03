# RBAC Testing Guide

**Status:** Ready for Testing  
**Date:** January 2026  
**Test Environment:** 3 Tenants with Multiple Roles

---

## 📋 Overview

This guide provides step-by-step instructions for testing the complete RBAC (Role-Based Access Control) implementation across the admin panel. The testing environment includes 3 tenants with users in different roles to validate all permission scenarios.

---

## 🏗️ Test Environment Setup

### Prerequisites
1. Backend server running on `http://localhost:8001`
2. Admin panel running on `http://localhost:5175`
3. PostgreSQL database accessible

### Setup Test Data

#### Option 1: Direct Python (Local Development)
```bash
cd backend
python setup_rbac_test_data.py
# Type 'yes' when prompted
```

#### Option 2: Via Docker (Recommended for Production-like Environment)
```bash
# Make sure containers are running
docker-compose up -d

# Execute script inside backend container
docker-compose exec backend python setup_rbac_test_data.py
# Type 'yes' when prompted

# Or in one line with automatic yes
docker-compose exec backend python -c "exec(open('setup_rbac_test_data.py').read().replace(\"input(\", \"lambda x: 'yes' #\"))"
```

#### Option 3: Via PowerShell (Windows)
```powershell
# Make sure containers are running
docker-compose up -d

# Execute in backend container
docker-compose exec backend python setup_rbac_test_data.py

# Or run with automatic confirmation
docker-compose exec backend sh -c "echo 'yes' | python setup_rbac_test_data.py"
```

**What it does:**
- ⚠️ Clears ALL existing data (except superuser)
- Creates 3 test tenants (Pizza Paradise, Burger Station, Noodle House)
- Creates 11 test users (2 global + 3 per tenant)
- Creates sample products, categories, and promotions
- Ready for immediate testing

---

## 👥 Test Accounts

### Global Access Users

| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| `superadmin` | `admin123` | super_admin | All tenants, all features |
| `admin` | `admin123` | admin | All tenants, all features |

### Pizza Paradise (Tenant 1)

| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| `pizza_manager` | `manager123` | manager | Full CRUD (own tenant) |
| `pizza_cashier` | `cashier123` | cashier | Products (read), Orders (CRUD) |
| `pizza_kitchen` | `kitchen123` | kitchen | Orders only (status update) |

### Burger Station (Tenant 2)

| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| `burger_manager` | `manager123` | manager | Full CRUD (own tenant) |
| `burger_cashier` | `cashier123` | cashier | Products (read), Orders (CRUD) |
| `burger_kitchen` | `kitchen123` | kitchen | Orders only (status update) |

### Noodle House (Tenant 3)

| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| `noodle_manager` | `manager123` | manager | Full CRUD (own tenant) |
| `noodle_cashier` | `cashier123` | cashier | Products (read), Orders (CRUD) |
| `noodle_kitchen` | `kitchen123` | kitchen | Orders only (status update) |

---

## 🧪 Testing Scenarios

### Test 1: Super Admin Access

**Objective:** Verify super admin can access all tenants and features.

**Steps:**
1. **Login**
   - Navigate to `http://localhost:5175/login`
   - Username: `superadmin`
   - Password: `admin123`
   - Click "Login"

2. **Verify Navigation**
   - ✅ Should see ALL menu items:
     - Dashboard
     - Products
     - Categories
     - Orders
     - Customers
     - Promotions
     - Users
     - Tenants
     - Outlets

3. **Test Tenant Selector**
   - ✅ Should see "Tenant Selector" dropdown in sidebar
   - Select "Pizza Paradise"
   - Navigate to Products
   - ✅ Should see only Pizza products (Margherita, Pepperoni, etc.)
   - Select "Burger Station"
   - ✅ Should see only Burger products (Classic Burger, Cheese Burger, etc.)
   - Select "All Tenants"
   - ✅ Should see products from all tenants

4. **Test Full CRUD Access**
   - Navigate to Products
   - ✅ "Add Product" button visible
   - Click on any product → Edit
   - ✅ Edit form loads
   - ✅ "Delete" button visible on product row

5. **Test Admin Pages**
   - Navigate to Users
   - ✅ Page loads (not redirected to unauthorized)
   - ✅ Can see all users
   - Navigate to Tenants
   - ✅ Page loads
   - ✅ Can see all tenants

**Expected Results:**
- ✅ All navigation items visible
- ✅ Tenant selector functional
- ✅ Can switch between tenants
- ✅ Full CRUD access to all resources
- ✅ Access to admin-only pages (Users, Tenants)

---

### Test 2: Regular Admin Access

**Objective:** Verify admin can access all tenants but no superuser features.

**Steps:**
1. **Logout** from superadmin (click username → Logout)

2. **Login**
   - Username: `admin`
   - Password: `admin123`

3. **Verify Navigation**
   - ✅ Should see all menu items (same as super admin)

4. **Test Tenant Switching**
   - ✅ Tenant selector visible
   - Switch between tenants
   - ✅ Data filters correctly per tenant

5. **Test Permissions**
   - Navigate to Products
   - ✅ Can create, edit, delete products
   - Navigate to Users
   - ✅ Can access user management
   - Navigate to Tenants
   - ✅ Can access tenant management

**Expected Results:**
- ✅ All features accessible
- ✅ Tenant switching works
- ✅ Behaves like super admin for testing purposes

---

### Test 3: Manager Access (Pizza Paradise)

**Objective:** Verify manager has full CRUD for own tenant only.

**Steps:**
1. **Logout** and **Login** as:
   - Username: `pizza_manager`
   - Password: `manager123`

2. **Verify Navigation**
   - ✅ Should see:
     - Dashboard
     - Products
     - Categories
     - Orders
     - Customers
     - Promotions
   - ❌ Should NOT see:
     - Users (hidden)
     - Tenants (hidden)
     - Outlets

3. **Verify Tenant Isolation**
   - ❌ NO tenant selector visible (fixed to Pizza Paradise)
   - Navigate to Products
   - ✅ Should ONLY see Pizza products
   - ✅ Should NOT see Burger or Noodle products

4. **Test Products CRUD**
   - ✅ "Add Product" button visible
   - Click "Add Product"
   - ✅ Create form loads
   - Create test product: "Test Pizza"
   - ✅ Product created successfully
   - Click "Edit" on any product
   - ✅ Can edit
   - ✅ "Delete" button visible
   - Click "Delete"
   - ✅ Product deleted successfully

5. **Test Promotions**
   - Navigate to Promotions
   - ✅ Page loads (not unauthorized)
   - ✅ Can see promotions
   - ✅ "Create Promotion" button visible

6. **Test Admin Pages (Should Fail)**
   - Navigate to `http://localhost:5175/users`
   - ❌ Should redirect to `/unauthorized`
   - ✅ "Access Denied" page shows
   - Navigate to `http://localhost:5175/tenants`
   - ❌ Should redirect to `/unauthorized`

**Expected Results:**
- ✅ Limited navigation (no admin pages)
- ✅ No tenant selector
- ✅ Only sees own tenant data
- ✅ Full CRUD on products, orders, promotions
- ❌ Cannot access Users/Tenants pages

---

### Test 4: Cashier Access (Burger Station)

**Objective:** Verify cashier has read-only products, can manage orders.

**Steps:**
1. **Logout** and **Login** as:
   - Username: `burger_cashier`
   - Password: `cashier123`

2. **Verify Navigation**
   - ✅ Should see:
     - Dashboard
     - Products
     - Categories
     - Orders
   - ❌ Should NOT see:
     - Promotions
     - Customers
     - Users
     - Tenants

3. **Test Products (Read-Only)**
   - Navigate to Products
   - ✅ Should see Burger products only
   - ❌ "Add Product" button HIDDEN
   - Click "Edit" on any product
   - ✅ Edit form may load (update permission for manager+)
   - Look for "Delete" button in product list
   - ❌ "Delete" button HIDDEN

4. **Test Orders**
   - Navigate to Orders
   - ✅ Page loads
   - ✅ Can see orders

5. **Test Restricted Pages**
   - Try to access Promotions: `http://localhost:5175/promotions`
   - ❌ Should redirect to `/unauthorized`
   - Try to access Users: `http://localhost:5175/users`
   - ❌ Should redirect to `/unauthorized`

**Expected Results:**
- ✅ Limited navigation
- ✅ Products read-only (no create/delete buttons)
- ✅ Can access orders
- ❌ Cannot create products
- ❌ Cannot delete products
- ❌ Cannot access promotions, users, tenants

---

### Test 5: Kitchen Staff Access (Noodle House)

**Objective:** Verify kitchen staff can ONLY access orders.

**Steps:**
1. **Logout** and **Login** as:
   - Username: `noodle_kitchen`
   - Password: `kitchen123`

2. **Verify Navigation**
   - ✅ Should ONLY see:
     - Dashboard
     - Orders
   - ❌ Everything else hidden

3. **Test Orders Access**
   - Navigate to Orders
   - ✅ Page loads
   - ✅ Can see Noodle House orders only

4. **Test Restricted Access**
   - Try to access Products: `http://localhost:5175/products`
   - ❌ Should redirect to `/unauthorized`
   - Try to access Promotions: `http://localhost:5175/promotions`
   - ❌ Should redirect to `/unauthorized`

**Expected Results:**
- ✅ Minimal navigation (orders only)
- ✅ Can view and update order status
- ❌ Cannot access any other pages

---

### Test 6: Cross-Tenant Isolation

**Objective:** Verify users cannot see other tenant's data.

**Steps:**
1. **Login** as `pizza_manager` (manager123)

2. **Check Products**
   - Navigate to Products
   - ✅ Should see 4 Pizza products
   - ❌ Should NOT see any Burger or Noodle products

3. **Direct API Test** (optional)
   - Open browser DevTools (F12)
   - Go to Console
   - Run:
     ```javascript
     fetch('http://localhost:8001/api/admin/products/', {
       headers: {
         'Authorization': 'Bearer ' + localStorage.getItem('token')
       }
     }).then(r => r.json()).then(d => console.log(d))
     ```
   - ✅ Should only return Pizza products
   - ❌ Should NOT include Burger/Noodle products

4. **Try Direct ID Access** (optional)
   - Find a Burger product ID (e.g., from admin/superadmin session)
   - Try to access via URL: `http://localhost:5175/products/[burger-product-id]/edit`
   - ❌ Should either show 404 or unauthorized error

**Expected Results:**
- ✅ Each tenant user sees only their own data
- ✅ API enforces tenant filtering
- ❌ Cannot access other tenant's data via direct ID

---

### Test 7: Permission Matrix Validation

**Objective:** Validate complete permission matrix.

**Test Matrix:**

| Feature | Kitchen | Cashier | Manager | Admin |
|---------|---------|---------|---------|-------|
| **Products** |
| - View | ❌ | ✅ | ✅ | ✅ |
| - Create | ❌ | ❌ | ✅ | ✅ |
| - Edit | ❌ | ❌ | ✅ | ✅ |
| - Delete | ❌ | ❌ | ✅ | ✅ |
| **Orders** |
| - View | ✅ | ✅ | ✅ | ✅ |
| - Create | ❌ | ✅ | ✅ | ✅ |
| - Update | ✅ | ✅ | ✅ | ✅ |
| - Delete | ❌ | ❌ | ✅ | ✅ |
| **Promotions** |
| - View | ❌ | ❌ | ✅ | ✅ |
| - Create | ❌ | ❌ | ✅ | ✅ |
| - Edit | ❌ | ❌ | ✅ | ✅ |
| - Delete | ❌ | ❌ | ✅ | ✅ |
| **Users** |
| - Access | ❌ | ❌ | ❌ | ✅ |
| **Tenants** |
| - Access | ❌ | ❌ | ❌ | ✅ |

**Validation Steps:**
For each role, test the features and verify checkmarks match expected behavior.

---

## 🐛 Common Issues & Troubleshooting

### Issue 1: "Access Denied" on login
**Cause:** User role not properly set  
**Solution:** Re-run setup script

### Issue 2: Seeing wrong tenant's data
**Cause:** Tenant context not being set  
**Solution:** 
- Check backend middleware is registered
- Verify `SetTenantContextMiddleware` is active
- Check browser console for errors

### Issue 3: Admin can't switch tenants
**Cause:** Tenant selector not rendering  
**Solution:**
- Verify user role is 'admin' or 'super_admin'
- Check `isAdmin()` function in auth store
- Clear browser cache/localStorage

### Issue 4: Kitchen staff can access products
**Cause:** Route guard not working  
**Solution:**
- Verify `+page.js` exists with `requireRoleLevel()`
- Check `ROLE_HIERARCHY` values
- Review console for errors

### Issue 5: Create/Delete buttons visible for cashier
**Cause:** Permission components not working  
**Solution:**
- Verify `PermissionButton` and `RoleGuard` imports
- Check `PERMISSION_MATRIX` in auth.js
- Inspect element to see if component rendered

---

## ✅ Test Checklist

### Super Admin Tests
- [ ] Can login successfully
- [ ] Sees all navigation items
- [ ] Tenant selector visible and functional
- [ ] Can switch between tenants
- [ ] Data filters correctly per selected tenant
- [ ] Full CRUD access to all resources
- [ ] Can access Users page
- [ ] Can access Tenants page

### Admin Tests
- [ ] Can login successfully
- [ ] Sees all navigation items
- [ ] Tenant selector visible
- [ ] Can switch tenants
- [ ] Full CRUD access

### Manager Tests (Each Tenant)
- [ ] Can login successfully
- [ ] Limited navigation (no Users/Tenants)
- [ ] No tenant selector
- [ ] Only sees own tenant data
- [ ] Can create products
- [ ] Can edit products
- [ ] Can delete products
- [ ] Can manage promotions
- [ ] Redirected from /users
- [ ] Redirected from /tenants

### Cashier Tests (Each Tenant)
- [ ] Can login successfully
- [ ] Limited navigation (Products, Orders only)
- [ ] Only sees own tenant data
- [ ] "Add Product" button hidden
- [ ] "Delete" button hidden on products
- [ ] Can access orders
- [ ] Redirected from /promotions

### Kitchen Tests (Each Tenant)
- [ ] Can login successfully
- [ ] Minimal navigation (Orders only)
- [ ] Only sees orders
- [ ] Redirected from /products
- [ ] Redirected from /promotions

### Cross-Tenant Isolation
- [ ] Pizza manager sees only Pizza data
- [ ] Burger cashier sees only Burger data
- [ ] Noodle kitchen sees only Noodle orders
- [ ] Direct API calls filtered by tenant
- [ ] Cannot access other tenant data via URL manipulation

---

## 📊 Test Results Template

```
RBAC Testing Results
Date: ___________
Tester: ___________

| Test Scenario | Status | Notes |
|---------------|--------|-------|
| Super Admin Access | ✅/❌ | |
| Admin Access | ✅/❌ | |
| Manager Access | ✅/❌ | |
| Cashier Access | ✅/❌ | |
| Kitchen Access | ✅/❌ | |
| Cross-Tenant Isolation | ✅/❌ | |
| Permission Matrix | ✅/❌ | |

Issues Found:
1. _______________________
2. _______________________
3. _______________________

Overall Status: ✅ PASS / ❌ FAIL
```

---

## 🔄 Resetting Test Environment

To reset and start fresh:

### Local Python
```bash
cd backend
python setup_rbac_test_data.py
# Type 'yes' when prompted
```

### Docker
```bash
docker-compose exec backend python setup_rbac_test_data.py
# Type 'yes' when prompted
```

### Docker with Auto-Confirm (PowerShell)
```powershell
docker-compose exec backend sh -c "echo 'yes' | python setup_rbac_test_data.py"
```

This will:
- Clear all test data
- Recreate tenants, users, products
- Reset to clean state

---

## 📚 Related Documentation

- [PHASE1_RBAC.md](./PHASE1_RBAC.md) - Backend implementation
- [PHASE2_RBAC.md](./PHASE2_RBAC.md) - Frontend components
- [PHASE3_RBAC.md](./PHASE3_RBAC.md) - Page-level implementation
- [RBAC_ROADMAP.md](../RBAC_ROADMAP.md) - Complete roadmap

---

## 🎯 Success Criteria

All tests pass when:

1. **Authentication**: All users can login with correct credentials
2. **Authorization**: Each role sees only permitted pages
3. **Tenant Isolation**: Users see only their tenant's data
4. **UI Adaptation**: Buttons/forms show/hide based on permissions
5. **API Security**: Backend enforces permissions on all endpoints
6. **Cross-Tenant**: No data leakage between tenants
7. **Admin Features**: Admin/super admin can switch tenants freely

**Test Status: Ready for execution** ✅

---

## 📞 Support

If you encounter issues:
1. Check console logs (F12 in browser)
2. Check backend logs
3. Verify database state
4. Re-run setup script
5. Review permission configuration in code

Good luck with testing! 🚀
