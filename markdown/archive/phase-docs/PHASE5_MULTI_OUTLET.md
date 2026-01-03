# Phase 5: Multi-Outlet Test Data Migration

## Overview
Phase 5 creates comprehensive test data for the multi-outlet system, including outlets, tenant owners, and outlet-specific products.

## Date
January 2026

## Status
✅ **COMPLETED**

---

## Implementation Details

### New Test Data Script

**File**: `backend/setup_multi_outlet_test_data.py`

#### Key Features
- Creates 2 outlets per tenant (6 outlets total)
- Creates tenant_owner role users
- Creates outlet-specific cashiers and kitchen staff
- Assigns products to specific outlets or marks them as shared
- Manager users have access to multiple outlets via `accessible_outlets`

---

## Test Data Structure

### Tenants (3)
1. **Pizza Paradise**
   - Main Branch
   - North Branch

2. **Burger Station**
   - Central
   - West

3. **Noodle House**
   - Downtown
   - East

### Users (20 total)

#### Global Users (2)
- `superadmin` / `admin123` - Super Admin (all tenants, all outlets)
- `admin` / `admin123` - Admin (all tenants, all outlets)

#### Per-Tenant Users (6 each × 3 tenants = 18)

**Pizza Paradise:**
- `pizza_owner` / `owner123` - Tenant Owner (all Pizza outlets)
- `pizza_manager` / `manager123` - Manager (accessible: both outlets)
- `pizza_cashier` / `cashier123` - Cashier (Main Branch only)
- `pizza_cashier2` / `cashier123` - Cashier (North Branch only)
- `pizza_kitchen` / `kitchen123` - Kitchen (Main Branch only)
- `pizza_kitchen2` / `kitchen123` - Kitchen (North Branch only)

**Burger Station:**
- `burger_owner` / `owner123` - Tenant Owner (all Burger outlets)
- `burger_manager` / `manager123` - Manager (accessible: both outlets)
- `burger_cashier` / `cashier123` - Cashier (Central only)
- `burger_cashier2` / `cashier123` - Cashier (West only)
- `burger_kitchen` / `kitchen123` - Kitchen (Central only)
- `burger_kitchen2` / `kitchen123` - Kitchen (West only)

**Noodle House:**
- `noodle_owner` / `owner123` - Tenant Owner (all Noodle outlets)
- `noodle_manager` / `manager123` - Manager (accessible: both outlets)
- `noodle_cashier` / `cashier123` - Cashier (Downtown only)
- `noodle_cashier2` / `cashier123` - Cashier (East only)
- `noodle_kitchen` / `kitchen123` - Kitchen (Downtown only)
- `noodle_kitchen2` / `kitchen123` - Kitchen (East only)

### Products (12 total - 4 per tenant)

#### Product Distribution Pattern
For each tenant:
- **2 Outlet-Specific Products**: Assigned to individual outlets
- **2 Shared Products** (`outlet=null`): Available at all outlets

#### Pizza Paradise Products
1. **Margherita Pizza** (Rp 85,000) - Main Branch ONLY
2. **Pepperoni Pizza** (Rp 95,000) - North Branch ONLY
3. **Coca Cola** (Rp 15,000) - ALL OUTLETS (shared)
4. **Garlic Bread** (Rp 25,000) - ALL OUTLETS (shared)

#### Burger Station Products
1. **Classic Burger** (Rp 45,000) - Central ONLY
2. **Cheese Burger** (Rp 55,000) - West ONLY
3. **French Fries** (Rp 20,000) - ALL OUTLETS (shared)
4. **Iced Tea** (Rp 12,000) - ALL OUTLETS (shared)

#### Noodle House Products
1. **Ramen Bowl** (Rp 40,000) - Downtown ONLY
2. **Pad Thai** (Rp 38,000) - East ONLY
3. **Tom Yum Soup** (Rp 35,000) - ALL OUTLETS (shared)
4. **Spring Rolls** (Rp 22,000) - ALL OUTLETS (shared)

### Categories (9 total - 3 per tenant)
- Pizza Paradise: Pizza, Beverages, Sides
- Burger Station: Burgers, Fries, Drinks
- Noodle House: Noodles, Soup, Appetizers

### Promotions (3 total - 1 per tenant)
- Pizza Paradise: Weekend Special (20% off)
- Burger Station: Combo Deal (Rp 15,000 off)
- Noodle House: Lunch Special (Rp 10,000 off)

---

## Script Features

### Transaction Safety
```python
@transaction.atomic
def reset_data():
    """All operations wrapped in transactions"""
    pass
```

### Outlet Creation
```python
@transaction.atomic
def create_outlets(tenants):
    """Create 2 outlets for each tenant"""
    outlets = {}
    
    # Pizza Paradise outlets
    outlets['pizza'] = []
    for i, name_suffix in enumerate(['Main Branch', 'North Branch'], 1):
        outlet = Outlet.objects.create(
            tenant=tenants[0],
            name=f'Pizza Paradise - {name_suffix}',
            slug=f'pizza-{name_suffix.lower().replace(" ", "-")}',
            address=f'Jl. Sudirman No. {100+i}, Jakarta',
            phone=f'+6281111111{i}',
            is_active=True
        )
        outlets['pizza'].append(outlet)
    
    return outlets
```

### User Outlet Assignment
```python
# Tenant Owner - can access all outlets in tenant
owner = User.objects.create_user(
    username=f'{prefix}_owner',
    role='tenant_owner',
    tenant=tenant,
    outlet=tenant_outlets[0]  # Default outlet
)

# Manager - accessible_outlets ManyToMany
manager = User.objects.create_user(
    username=f'{prefix}_manager',
    role='manager',
    tenant=tenant,
    outlet=tenant_outlets[0]
)
manager.accessible_outlets.add(*tenant_outlets)  # Add all outlets

# Cashier - assigned to specific outlet
cashier1 = User.objects.create_user(
    username=f'{prefix}_cashier',
    role='cashier',
    tenant=tenant,
    outlet=tenant_outlets[0]  # Main branch only
)
```

### Product Outlet Assignment
```python
# Product data: outlet_idx=0/1 for outlet-specific, None for shared
product_data = {
    'pizza': [
        ('Margherita Pizza', '001', 0, 85000, 10, 0),     # Main branch only
        ('Pepperoni Pizza', '002', 0, 95000, 8, 1),       # North branch only
        ('Coca Cola', 'BEV-001', 1, 15000, 50, None),     # All outlets
        ('Garlic Bread', 'SIDE-001', 2, 25000, 20, None)  # All outlets
    ]
}

# Create with outlet assignment
for name, sku_suffix, cat_idx, price, stock, outlet_idx in product_data[prefix]:
    outlet = tenant_outlets[outlet_idx] if outlet_idx is not None else None
    
    Product.all_objects.create(
        name=name,
        tenant=tenant,
        outlet=outlet,  # Specific outlet or None (shared)
        ...
    )
```

---

## Running the Script

### Via Docker
```bash
docker-compose exec -T backend python setup_multi_outlet_test_data.py
```

### Expected Output
```
🚀 MULTI-OUTLET TEST DATA SETUP
================================

🗑️  Clearing existing data...
✅ All test data cleared

🏢 Creating tenants...
  ✓ Created: Pizza Paradise
  ✓ Created: Burger Station
  ✓ Created: Noodle House

📍 Creating outlets...
  ✓ Pizza Paradise - Main Branch
  ✓ Pizza Paradise - North Branch
  ✓ Burger Station - Central
  ✓ Burger Station - West
  ✓ Noodle House - Downtown
  ✓ Noodle House - East

👥 Creating users...
  ✓ superadmin (super_admin) - ALL TENANTS
  ✓ admin (admin) - ALL TENANTS
  ✓ pizza_owner (tenant_owner) - Pizza Paradise - ALL OUTLETS
  ✓ pizza_manager (manager) - Both outlets
  ✓ pizza_cashier (cashier) - Pizza Paradise - Main Branch
  ✓ pizza_cashier2 (cashier) - Pizza Paradise - North Branch
  ...

📁 Creating categories...
📝 Creating products...
🎉 Creating promotions...

✨ Multi-outlet system ready for testing!
```

---

## Testing Scenarios

### Scenario 1: Tenant Owner Login
**User**: `pizza_owner` / `owner123`

**Expected Behavior**:
1. ✅ Can see OutletSelector in sidebar
2. ✅ Dropdown shows both Pizza Paradise outlets
3. ✅ Can switch between Main Branch and North Branch
4. ✅ When on Main Branch:
   - Sees: Margherita Pizza + Coca Cola + Garlic Bread
5. ✅ When on North Branch:
   - Sees: Pepperoni Pizza + Coca Cola + Garlic Bread

### Scenario 2: Manager with Multiple Outlets
**User**: `burger_manager` / `manager123`

**Expected Behavior**:
1. ✅ Can see OutletSelector in sidebar
2. ✅ Dropdown shows Central and West outlets
3. ✅ Can switch between accessible outlets
4. ✅ When on Central:
   - Sees: Classic Burger + French Fries + Iced Tea
5. ✅ When on West:
   - Sees: Cheese Burger + French Fries + Iced Tea

### Scenario 3: Cashier with Single Outlet
**User**: `noodle_cashier` / `cashier123`

**Expected Behavior**:
1. ✅ OutletSelector is HIDDEN (only 1 outlet)
2. ✅ Header shows outlet badge: "📍 Noodle House - Downtown"
3. ✅ Products page shows:
   - Ramen Bowl (Downtown only)
   - Tom Yum Soup (shared)
   - Spring Rolls (shared)
4. ✅ Does NOT see: Pad Thai (East only)

### Scenario 4: Second Branch Cashier
**User**: `noodle_cashier2` / `cashier123`

**Expected Behavior**:
1. ✅ OutletSelector is HIDDEN
2. ✅ Header shows: "📍 Noodle House - East"
3. ✅ Products page shows:
   - Pad Thai (East only)
   - Tom Yum Soup (shared)
   - Spring Rolls (shared)
4. ✅ Does NOT see: Ramen Bowl (Downtown only)

### Scenario 5: Kitchen Staff
**User**: `pizza_kitchen2` / `kitchen123`

**Expected Behavior**:
1. ✅ OutletSelector is HIDDEN
2. ✅ Assigned to: Pizza Paradise - North Branch
3. ✅ Kitchen Display shows orders for North Branch only
4. ✅ Can see product: Pepperoni Pizza + shared products

---

## Data Summary

### Statistics
- **Tenants**: 3
- **Outlets**: 6 (2 per tenant)
- **Users**: 20 total
  - 2 global (super_admin, admin)
  - 18 tenant-specific (6 per tenant)
- **Products**: 12 total (4 per tenant)
  - 6 outlet-specific
  - 6 shared (available at all outlets)
- **Categories**: 9 (3 per tenant)
- **Promotions**: 3 (1 per tenant)

### Product Distribution
| Tenant | Outlet-Specific | Shared | Total |
|--------|----------------|--------|-------|
| Pizza Paradise | 2 | 2 | 4 |
| Burger Station | 2 | 2 | 4 |
| Noodle House | 2 | 2 | 4 |
| **Total** | **6** | **6** | **12** |

### User Distribution by Role
| Role | Count | Outlets Access |
|------|-------|---------------|
| super_admin | 1 | All |
| admin | 1 | All |
| tenant_owner | 3 | All in tenant |
| manager | 3 | Multiple (accessible_outlets) |
| cashier | 6 | Single (assigned) |
| kitchen | 6 | Single (assigned) |
| **Total** | **20** | |

---

## Verification Steps

### 1. Check Outlets Created
```bash
docker-compose exec -T backend python manage.py shell -c "
from apps.tenants.models import Outlet;
print(f'Total outlets: {Outlet.objects.count()}');
for o in Outlet.objects.all():
    print(f'  - {o.name} ({o.tenant.name})')
"
```

**Expected**: 6 outlets (2 per tenant)

### 2. Check User Outlet Assignments
```bash
docker-compose exec -T backend python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
for u in User.objects.filter(tenant__isnull=False):
    outlets = u.accessible_outlets.count() if u.role == 'manager' else 1
    print(f'{u.username} ({u.role}) - Outlet: {u.outlet.name if u.outlet else \"None\"} - Accessible: {outlets}')
"
```

**Expected**: Managers have accessible_outlets, others have single assigned outlet

### 3. Check Product Outlet Distribution
```bash
docker-compose exec -T backend python manage.py shell -c "
from apps.products.models import Product;
shared = Product.all_objects.filter(outlet__isnull=True).count();
specific = Product.all_objects.filter(outlet__isnull=False).count();
print(f'Shared products: {shared}');
print(f'Outlet-specific: {specific}');
for p in Product.all_objects.all():
    outlet_info = p.outlet.name if p.outlet else 'All Outlets'
    print(f'  - {p.name} ({p.tenant.name}) - {outlet_info}')
"
```

**Expected**: 6 shared, 6 outlet-specific

---

## Benefits

### Comprehensive Testing
✅ Covers all role scenarios (owner, manager, cashier, kitchen)
✅ Tests outlet-specific product filtering
✅ Tests shared product visibility
✅ Tests multi-outlet access for managers
✅ Tests single-outlet restrictions for cashiers/kitchen

### Realistic Data
✅ Multiple branches per tenant (realistic franchise setup)
✅ Mix of shared and outlet-specific products
✅ Different users assigned to different outlets
✅ Manager with access to multiple outlets

### Easy Reset
✅ @transaction.atomic ensures clean rollback on error
✅ Single script execution creates entire test environment
✅ Can be re-run anytime to reset to known state

---

## Next Steps

### Immediate
1. ✅ Login to admin panel
2. ✅ Test each user role
3. ✅ Verify outlet switching works
4. ✅ Check product filtering by outlet

### Phase 6 (Optional)
- Add outlet-level analytics
- Sales reports by outlet
- Inventory management per outlet
- Outlet performance comparison

### Phase 7
- User documentation
- Training materials
- Video tutorials for outlet management

---

## Troubleshooting

### Issue: Script fails with "Outlet matching query does not exist"
**Solution**: Ensure migrations are applied
```bash
docker-compose exec backend python manage.py migrate
```

### Issue: Products not filtering by outlet
**Solution**: Check middleware is configured
```python
# config/settings.py
MIDDLEWARE = [
    ...
    'apps.core.middleware.SetOutletContextMiddleware',  # After auth middleware
]
```

### Issue: OutletSelector not showing
**Solution**: Check user role and accessible outlets
- tenant_owner should see all outlets in tenant
- manager should have accessible_outlets assigned
- cashier/kitchen should be hidden if only 1 outlet

---

## Related Files

### Backend
- `backend/setup_multi_outlet_test_data.py` - Test data script (THIS)
- `backend/setup_rbac_test_data.py` - Original RBAC script (deprecated for multi-outlet)
- `backend/apps/users/models.py` - User model with accessible_outlets
- `backend/apps/products/models.py` - Product model with outlet field
- `backend/apps/tenants/models.py` - Tenant and Outlet models

### Documentation
- `markdown/PHASE1_MULTI_OUTLET.md` - Database schema
- `markdown/PHASE2_MULTI_OUTLET.md` - Backend context
- `markdown/PHASE3_MULTI_OUTLET.md` - Permissions & filtering
- `markdown/PHASE4_MULTI_OUTLET.md` - Frontend components
- `markdown/PHASE5_MULTI_OUTLET.md` - THIS FILE

---

## Conclusion

Phase 5 successfully creates a complete multi-outlet test environment with:

✅ 6 outlets (2 per tenant)
✅ 20 users with proper outlet assignments
✅ 12 products (mix of outlet-specific and shared)
✅ tenant_owner role users
✅ Manager users with multi-outlet access
✅ Cashier/kitchen users with single-outlet restrictions

The system is now ready for comprehensive multi-outlet testing!
