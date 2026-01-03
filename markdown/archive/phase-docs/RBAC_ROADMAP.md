# Role-Based Access Control (RBAC) Implementation Roadmap

## 🎯 Goal
Implement consistent role-based access control across backend (Django) and frontend (SvelteKit) untuk multi-tenant POS system.

---

## 📋 Phase 1: Backend Foundation (Django)

### Step 1.1: Create Permission Classes
**File:** `backend/apps/core/permissions.py`

**Tasks:**
- [ ] Create `IsAuthenticatedUser` - base permission
- [ ] Create `IsSuperAdminOrAdmin` - untuk admin operations
- [ ] Create `IsTenantOwnerOrManager` - untuk tenant management
- [ ] Create `IsManagerOrAbove` - untuk manager level
- [ ] Create `IsCashierOrAbove` - untuk cashier operations
- [ ] Create `IsKitchenStaff` - untuk kitchen display

**Code Structure:**
```python
from rest_framework.permissions import BasePermission

class IsSuperAdminOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.role in ['admin', 'super_admin']
```

---

### Step 1.2: Create Tenant Context Middleware
**File:** `backend/apps/core/middleware.py`

**Tasks:**
- [ ] Create `SetTenantContextMiddleware`
- [ ] Auto-detect tenant from user
- [ ] Allow admin override dengan query param `?tenant=X`
- [ ] Store tenant in thread-local context
- [ ] Register middleware di `settings.py`

**Logic:**
```python
# Admin: dapat akses semua tenant via query param
# User biasa: hanya tenant mereka sendiri
```

---

### Step 1.3: Update All ViewSets - Products
**Files:**
- `backend/apps/products/views_admin.py`
- `backend/apps/products/views.py`

**Tasks:**
- [ ] Add appropriate `permission_classes` to `ProductAdminViewSet`
- [ ] Add appropriate `permission_classes` to `CategoryAdminViewSet`
- [ ] Ensure `get_queryset()` uses `all_objects` for TenantModel
- [ ] Auto-set tenant on `perform_create()`
- [ ] Add tenant validation on `perform_update()`

---

### Step 1.4: Update All ViewSets - Orders
**Files:**
- `backend/apps/orders/views_admin.py`
- `backend/apps/orders/views.py`

**Tasks:**
- [ ] Add `permission_classes` to `OrderAdminViewSet`
- [ ] Update `get_queryset()` untuk role-based filtering
- [ ] Auto-set tenant pada checkout
- [ ] Cashier hanya bisa create/update orders
- [ ] Manager bisa delete orders
- [ ] Add tenant filter untuk reports

---

### Step 1.5: Update All ViewSets - Customers
**File:** `backend/apps/customers/views_admin.py`

**Tasks:**
- [ ] Add `permission_classes` to `CustomerAdminViewSet`
- [ ] Update `get_queryset()` untuk tenant filtering
- [ ] Auto-set tenant on create
- [ ] Add bulk operations dengan permission check

---

### Step 1.6: Update All ViewSets - Promotions
**File:** `backend/apps/promotions/views.py`

**Tasks:**
- [ ] Add `permission_classes` to `PromotionViewSet`
- [ ] Update `get_queryset()` - admin sees all, user sees tenant only
- [ ] Auto-set tenant on create
- [ ] Validate products belong to same tenant

---

### Step 1.7: Update All ViewSets - Users & Tenants
**Files:**
- `backend/apps/users/views.py`
- `backend/apps/tenants/views.py`

**Tasks:**
- [ ] Add `IsSuperAdminOrAdmin` to `UserViewSet`
- [ ] Add `IsSuperAdminOrAdmin` to `TenantViewSet`
- [ ] Add `IsManagerOrAbove` to `OutletViewSet`
- [ ] Prevent non-admin from seeing other tenants' users
- [ ] Add `/me` endpoint untuk current user info

---

### Step 1.8: Testing & Validation
**Tasks:**
- [ ] Test super_admin dapat akses semua tenant
- [ ] Test admin dapat akses semua tenant
- [ ] Test manager hanya akses tenant sendiri
- [ ] Test cashier tidak bisa delete
- [ ] Test kitchen hanya bisa update order status
- [ ] Test tenant isolation (user A tidak bisa akses data user B)

---

## 📋 Phase 2: Frontend Foundation (SvelteKit)

### Step 2.1: Create Auth Store Enhancement
**File:** `admin/src/lib/stores/auth.js`

**Tasks:**
- [ ] Add role info ke user store
- [ ] Add tenant info ke user store
- [ ] Add `hasRole()` helper function
- [ ] Add `canAccessTenant()` helper function
- [ ] Add `canPerform()` untuk action-based check
- [ ] Store di localStorage untuk persistence

**Code Structure:**
```javascript
export const user = writable({
  id: null,
  username: '',
  role: '',
  tenant: null,
  permissions: []
});

export function hasRole(...roles) {
  return get(user).role && roles.includes(get(user).role);
}
```

---

### Step 2.2: Create Role Guard Store
**File:** `admin/src/lib/stores/roleGuard.js`

**Tasks:**
- [ ] Create `roleGuard` store
- [ ] Add `ROLE_HIERARCHY` constant
- [ ] Add `hasPermission(action, resource)` function
- [ ] Add `canCreate/Update/Delete` helpers
- [ ] Export role checking utilities

---

### Step 2.3: Create Route Guards
**File:** `admin/src/hooks.server.js` atau `admin/src/routes/+layout.server.js`

**Tasks:**
- [ ] Create server-side auth check
- [ ] Redirect ke login jika tidak authenticated
- [ ] Check role untuk protected routes
- [ ] Pass user data ke `+page.server.js`

**Protected Routes:**
```
/users -> IsSuperAdminOrAdmin
/tenants -> IsSuperAdminOrAdmin
/outlets -> IsManagerOrAbove
/products -> IsCashierOrAbove
/orders -> IsAuthenticatedUser
/promotions -> IsManagerOrAbove
```

---

### Step 2.4: Update Navigation Menu
**File:** `admin/src/lib/components/Sidebar.svelte`

**Tasks:**
- [ ] Import `hasRole` helper
- [ ] Add `{#if}` blocks untuk conditional menu
- [ ] Hide admin-only menu dari regular users
- [ ] Show tenant selector hanya untuk admin
- [ ] Add role badge di user profile

**Example:**
```svelte
{#if hasRole('admin', 'super_admin')}
  <a href="/tenants">Manage Tenants</a>
{/if}
```

---

### Step 2.5: Update All Admin Pages - Products
**Files:**
- `admin/src/routes/products/+page.svelte`
- `admin/src/routes/products/create/+page.svelte`
- `admin/src/routes/products/[id]/edit/+page.svelte`

**Tasks:**
- [ ] Add role check di `+page.js` (load function)
- [ ] Hide delete button untuk non-manager
- [ ] Show tenant selector untuk admin
- [ ] Disable tenant field untuk non-admin
- [ ] Add loading state dengan proper error handling

---

### Step 2.6: Update All Admin Pages - Orders
**Files:**
- `admin/src/routes/orders/+page.svelte`
- `admin/src/routes/orders/[id]/+page.svelte`

**Tasks:**
- [ ] Add role-based action buttons
- [ ] Cashier: tidak ada delete button
- [ ] Manager: full CRUD access
- [ ] Kitchen: hanya update status
- [ ] Show tenant filter untuk admin

---

### Step 2.7: Update All Admin Pages - Customers
**Files:**
- `admin/src/routes/customers/+page.svelte`
- `admin/src/routes/customers/create/+page.svelte`

**Tasks:**
- [ ] Add permission checks
- [ ] Hide actions based on role
- [ ] Auto-set tenant untuk non-admin

---

### Step 2.8: Update All Admin Pages - Promotions
**Files:**
- `admin/src/routes/promotions/+page.svelte`
- `admin/src/routes/promotions/create/+page.svelte`

**Tasks:**
- [ ] Add `IsManagerOrAbove` check
- [ ] Show tenant selector untuk admin
- [ ] Filter products by tenant
- [ ] Validate product selection

---

### Step 2.9: Update All Admin Pages - Users & Tenants
**Files:**
- `admin/src/routes/users/+page.svelte`
- `admin/src/routes/tenants/+page.svelte`

**Tasks:**
- [ ] Lock pages untuk admin only
- [ ] Redirect non-admin to dashboard
- [ ] Add server-side route guard

---

### Step 2.10: Create Reusable Components
**Files:**
- `admin/src/lib/components/RoleGuard.svelte`
- `admin/src/lib/components/TenantSelector.svelte`
- `admin/src/lib/components/PermissionButton.svelte`

**Tasks:**
- [ ] `<RoleGuard roles={['admin']}>` component
- [ ] `<TenantSelector>` untuk admin
- [ ] `<PermissionButton action="delete">` dengan auto-hide

**Example Usage:**
```svelte
<RoleGuard roles={['admin', 'manager']}>
  <button on:click={deleteItem}>Delete</button>
</RoleGuard>
```

---

## 📋 Phase 3: Integration & Testing

### Step 3.1: Backend-Frontend Integration
**Tasks:**
- [ ] Test login dengan different roles
- [ ] Verify token includes role & tenant info
- [ ] Test API calls dengan role-based filtering
- [ ] Test admin dapat switch tenant
- [ ] Test unauthorized access returns 403

---

### Step 3.2: End-to-End Testing
**Tasks:**
- [ ] Create test users untuk each role
- [ ] Test super_admin flow (all access)
- [ ] Test admin flow (multi-tenant)
- [ ] Test manager flow (single tenant)
- [ ] Test cashier flow (limited actions)
- [ ] Test kitchen flow (order status only)

---

### Step 3.3: Error Handling
**Tasks:**
- [ ] Add proper 403 error messages
- [ ] Show "No Permission" toast
- [ ] Redirect ke dashboard on unauthorized
- [ ] Log permission errors untuk audit

---

### Step 3.4: Performance Optimization
**Tasks:**
- [ ] Cache role checks di frontend
- [ ] Optimize queryset dengan proper select_related
- [ ] Add database indexes on role & tenant fields
- [ ] Lazy load non-critical data

---

## 📋 Phase 4: Documentation & Deployment

### Step 4.1: Documentation
**Tasks:**
- [ ] Update API documentation dengan permission requirements
- [ ] Create role matrix table
- [ ] Add permission examples
- [ ] Document tenant switching untuk admin

---

### Step 4.2: Database Migrations
**Tasks:**
- [ ] Create migration scripts untuk existing users
- [ ] Assign default roles
- [ ] Set tenant untuk orphaned records
- [ ] Backup database before deployment

---

### Step 4.3: Deployment Checklist
**Tasks:**
- [ ] Test di staging environment
- [ ] Run all migrations
- [ ] Verify permission checks work
- [ ] Test with production-like data
- [ ] Create admin user guide
- [ ] Deploy to production

---

## 🔧 Implementation Priority

### High Priority (Week 1)
1. ✅ Backend Permission Classes (Step 1.1)
2. ✅ Tenant Context Middleware (Step 1.2)
3. ✅ Update ViewSets - Products & Orders (Step 1.3, 1.4)
4. ✅ Frontend Auth Store (Step 2.1)
5. ✅ Route Guards (Step 2.3)

### Medium Priority (Week 2)
6. Update ViewSets - Customers, Promotions (Step 1.5, 1.6)
7. Update Navigation Menu (Step 2.4)
8. Update Admin Pages - Products, Orders (Step 2.5, 2.6)
9. Create Reusable Components (Step 2.10)

### Low Priority (Week 3)
10. Update ViewSets - Users & Tenants (Step 1.7)
11. Update Admin Pages - All remaining (Step 2.7, 2.8, 2.9)
12. Testing & Integration (Phase 3)
13. Documentation (Phase 4)

---

## 📊 Progress Tracking

| Phase | Status | Progress | Notes |
|-------|--------|----------|-------|
| Phase 1: Backend | 🟡 In Progress | 40% | Permissions created, need ViewSet updates |
| Phase 2: Frontend | 🔴 Not Started | 0% | Waiting for backend completion |
| Phase 3: Testing | 🔴 Not Started | 0% | - |
| Phase 4: Deployment | 🔴 Not Started | 0% | - |

---

## 🎓 Role Matrix Reference

| Role | Products | Orders | Customers | Promotions | Users | Tenants | Reports |
|------|----------|--------|-----------|------------|-------|---------|---------|
| **super_admin** | CRUD All | CRUD All | CRUD All | CRUD All | CRUD All | CRUD All | View All |
| **admin** | CRUD All | CRUD All | CRUD All | CRUD All | CRUD All | CRUD All | View All |
| **manager** | CRUD Own | CRUD Own | CRUD Own | CRUD Own | View Own | View Own | View Own |
| **cashier** | View Own | CR Own | CR Own | View Own | - | - | - |
| **kitchen** | View Own | U Status | - | - | - | - | - |

*CRUD = Create, Read, Update, Delete*
*Own = Data dari tenant sendiri saja*

---

## 🚀 Quick Start Commands

### Check Current Implementation Status
```bash
# Check which ViewSets have permission_classes
cd backend
grep -r "permission_classes" apps/*/views*.py

# Check role field in User model
python manage.py shell
from apps.users.models import User
print(User.ROLE_CHOICES)
```

### Run Tests
```bash
# Backend tests
cd backend
python manage.py test apps.core.tests.test_permissions

# Frontend tests
cd admin
npm run test
```

### Create Test Users
```bash
cd backend
python manage.py shell

# Script akan dibuat di Step 3.2
```

---

## 📝 Notes

- **Security First:** Always implement authorization di backend, frontend hanya UI guard
- **Tenant Isolation:** Critical! User tidak boleh bisa bypass tenant filtering
- **Performance:** Use select_related, prefetch_related untuk optimize queries
- **Audit Log:** Consider adding audit log untuk sensitive operations
- **Testing:** Test dengan real users, bukan hanya unit tests

---

**Last Updated:** 2026-01-01
**Status:** ✅ COMPLETED - Production Ready

---

## 🚀 Next Phase: Multi-Outlet Extension

The RBAC foundation implemented in this roadmap has been successfully completed and is now being extended with **multi-outlet support** to enable franchise and multi-location management.

### What's Next: Multi-Outlet System

**Status:** Planning Phase  
**Documentation:** [MULTI_OUTLET_ROADMAP.md](MULTI_OUTLET_ROADMAP.md)

**Key Additions:**
- **Outlet-level data filtering** - Products, orders, and inventory per outlet
- **`accessible_outlets` ManyToMany** - Users can access multiple outlets
- **`tenant_owner` role** - New role for franchise owners managing all outlets
- **Outlet context management** - Similar to tenant context, adds outlet filtering
- **Outlet selector UI** - Frontend component for switching between outlets

### Architecture Overview

```
Current (RBAC):
User → Tenant (1:1)
Product → Tenant
Order → Tenant

Extended (Multi-Outlet):
User → Tenant (1:1) + accessible_outlets (M:N)
Tenant → Outlets (1:M)
Product → Outlet (outlet-specific inventory)
Order → Outlet (outlet-specific sales)
```

### Benefits of Multi-Outlet Extension

1. ✅ **Franchise Support** - Tenant owners can manage multiple locations
2. ✅ **Flexible Access** - Managers can be assigned to specific outlets
3. ✅ **Outlet Analytics** - Performance tracking per location
4. ✅ **Maintains RBAC** - Builds on existing permission system, doesn't replace it
5. ✅ **Backward Compatible** - Can disable outlet filtering if needed

### Role Evolution

```
RBAC Roles (Current):
- super_admin (100) - Platform admin
- admin (90) - Multi-tenant admin
- manager (50) - Tenant manager
- cashier (30) - Create orders
- kitchen (20) - Update order status

Multi-Outlet Roles (Extended):
- super_admin (100) - Platform admin [UNCHANGED]
- admin (90) - Multi-tenant admin [UNCHANGED]
- tenant_owner (80) - Franchise owner [NEW]
- manager (50) - Outlet manager [ENHANCED]
- cashier (30) - Outlet cashier [ENHANCED]
- kitchen (20) - Outlet kitchen [ENHANCED]
```

### Implementation Phases

The multi-outlet system will be implemented in 7 phases over 4-6 weeks:

1. **Phase 1:** Database Schema & Models (Week 1)
2. **Phase 2:** Backend Context & Middleware (Week 2)
3. **Phase 3:** Backend Permissions & API (Week 2-3)
4. **Phase 4:** Frontend Components (Week 3-4)
5. **Phase 5:** Data Migration & Testing (Week 4-5)
6. **Phase 6:** Analytics & Reporting (Week 5-6)
7. **Phase 7:** Documentation & Training (Week 6)

For complete implementation details, see [MULTI_OUTLET_ROADMAP.md](MULTI_OUTLET_ROADMAP.md)

---

## 📚 Complete Documentation Index

### RBAC Foundation (Completed)
- **[RBAC_ROADMAP.md](RBAC_ROADMAP.md)** - This file: Complete RBAC roadmap
- **[PHASE1_RBAC.md](PHASE1_RBAC.md)** - Backend foundation implementation
- **[PHASE2_RBAC.md](markdown/PHASE2_RBAC.md)** - Frontend components
- **[PHASE3_RBAC.md](markdown/PHASE3_RBAC.md)** - Page-level implementation
- **[RBAC_TESTING_GUIDE.md](markdown/RBAC_TESTING_GUIDE.md)** - Testing scenarios
- **[RBAC_SETUP_QUICKSTART.md](RBAC_SETUP_QUICKSTART.md)** - Quick setup guide

### Multi-Outlet Extension (Next)
- **[MULTI_OUTLET_ROADMAP.md](MULTI_OUTLET_ROADMAP.md)** - Multi-outlet system roadmap

---

**Note:** The RBAC system is production-ready and serves as the foundation for the multi-outlet extension. All RBAC concepts (roles, permissions, tenant isolation) remain intact and are enhanced with outlet-level filtering.
