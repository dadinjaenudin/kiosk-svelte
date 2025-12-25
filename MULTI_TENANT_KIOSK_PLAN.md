# 🏪 Multi-Tenant Kiosk Selection - Implementation Plan

## Current Issue

Saat ini kiosk menampilkan **semua produk dari semua tenant** karena:
- `/api/products/` di-exclude dari tenant middleware
- ViewSet menggunakan `all_objects` manager (no filtering)
- Frontend tidak memilih tenant

## Solution Options

### ✅ Option 1: Tenant Selection Screen (RECOMMENDED)

**Flow**:
1. Kiosk starts → Show tenant selection
2. User picks tenant → Show outlet selection (if multiple)
3. User picks outlet → Show menu with filtered products

**Pros**:
- ✅ Flexible (one device, multiple tenants)
- ✅ User-friendly
- ✅ Easy to switch
- ✅ No configuration needed

**Cons**:
- Extra step for users

---

### Option 2: URL/Subdomain Based

**Implementation**:
- `tenant1.yourdomain.com/kiosk`
- `tenant2.yourdomain.com/kiosk`

**Pros**:
- No selection screen
- Automatic tenant detection

**Cons**:
- Requires DNS setup
- More complex deployment

---

### Option 3: Device Configuration

**Implementation**:
- Each kiosk device configured with tenant ID
- Stored in localStorage/config

**Pros**:
- No user interaction
- Fast startup

**Cons**:
- Requires initial setup
- Can't easily switch

---

## Recommended Implementation

**Option 1 + Option 3 Hybrid**:
1. First time: Show tenant selection
2. Save choice to localStorage
3. Auto-load saved tenant on next visit
4. Allow manual change via button

---

## Implementation Steps

### Step 1: Backend API Endpoints

Create public endpoints for tenant selection:

```python
# backend/apps/tenants/views.py

class PublicTenantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public API for tenant selection (kiosk)
    """
    queryset = Tenant.objects.filter(is_active=True)
    serializer_class = TenantSerializer
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['get'])
    def outlets(self, request, pk=None):
        """Get outlets for a tenant"""
        tenant = self.get_object()
        outlets = Outlet.objects.filter(tenant=tenant, is_active=True)
        serializer = OutletSerializer(outlets, many=True)
        return Response(serializer.data)
```

**Endpoints**:
- `GET /api/tenants/` - List all active tenants
- `GET /api/tenants/{id}/outlets/` - List outlets for tenant

---

### Step 2: Update Middleware

```python
# backend/apps/tenants/middleware.py

EXCLUDE_URLS = [
    '/api/tenants/',  # Allow public tenant list
    '/api/products/', # Products still public (filtered by headers)
    '/api/health/',
    ...
]
```

---

### Step 3: Update Product API

Products API now reads X-Tenant-ID header for filtering:

```python
# backend/apps/products/views.py

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        # Get tenant from header
        tenant_id = self.request.headers.get('X-Tenant-ID')
        
        if tenant_id:
            # Filter by specific tenant
            return Product.objects.filter(
                tenant_id=tenant_id,
                is_available=True
            ).select_related('category').prefetch_related('modifiers')
        else:
            # Return all if no tenant specified (backward compatible)
            return Product.all_objects.filter(
                is_available=True
            ).select_related('category').prefetch_related('modifiers')
```

---

### Step 4: Frontend Tenant Selector

**Features**:
- Beautiful tenant selection screen
- Outlet selection (if multiple)
- Save to localStorage
- Auto-restore on reload
- "Change Location" button in kiosk

**UI Flow**:
```
┌─────────────────────────┐
│   Select Restaurant     │
│                         │
│  🏪 Warung Makan A      │
│  🏪 Pizza House         │
│  🏪 Kopi Kita           │
└─────────────────────────┘
           ↓
┌─────────────────────────┐
│   Select Location       │
│   Warung Makan A        │
│                         │
│  📍 Cabang Pusat        │
│  📍 Cabang Mall         │
│  📍 Cabang Timur        │
└─────────────────────────┘
           ↓
┌─────────────────────────┐
│  Warung Makan A         │
│  Cabang Pusat    [Change]│
│─────────────────────────│
│  Categories & Products  │
│  (Filtered by tenant)   │
└─────────────────────────┘
```

---

### Step 5: API Request with Headers

```javascript
// Frontend sends headers
const headers = {
  'X-Tenant-ID': selectedTenant.id,
  'X-Outlet-ID': selectedOutlet.id
};

const response = await fetch('/api/products/categories/', { headers });
```

---

## Security Considerations

### Public Endpoints
- ✅ `/api/tenants/` - Public (show restaurant list)
- ✅ `/api/tenants/{id}/outlets/` - Public (show locations)
- ✅ `/api/products/` - Public BUT filtered by X-Tenant-ID header

### Protected Endpoints
- 🔒 `/api/orders/` - Requires auth
- 🔒 `/api/payments/` - Requires auth
- 🔒 `/api/users/` - Requires auth

### Data Isolation
- Tenant selection is **optional** for kiosk
- If X-Tenant-ID header provided → filter by tenant
- If not provided → show all (backward compatible)
- Each tenant only sees their own orders/payments (auth required)

---

## Implementation Checklist

### Backend
- [ ] Create `PublicTenantViewSet`
- [ ] Add `/api/tenants/` endpoint
- [ ] Add `/api/tenants/{id}/outlets/` endpoint
- [ ] Update middleware EXCLUDE_URLS
- [ ] Update ProductViewSet to read X-Tenant-ID header
- [ ] Update CategoryViewSet to read X-Tenant-ID header

### Frontend
- [ ] Create TenantSelector component
- [ ] Create OutletSelector component
- [ ] Update kiosk page with tenant flow
- [ ] Add localStorage persistence
- [ ] Add "Change Location" button
- [ ] Send X-Tenant-ID header in all API requests

### Testing
- [ ] Test tenant selection
- [ ] Test outlet selection
- [ ] Test localStorage persistence
- [ ] Test filtered products
- [ ] Test backward compatibility (no tenant)

---

## Migration Strategy

### Phase 1: Add Tenant Selection (Non-Breaking)
- Add new endpoints
- Add tenant selector UI
- Keep backward compatibility (works without tenant selection)

### Phase 2: Encourage Tenant Selection
- Show tenant selector by default
- Save to localStorage
- Auto-restore saved tenant

### Phase 3: Make Tenant Required (Optional)
- Force tenant selection
- Remove all_objects fallback
- Strict tenant isolation

---

## Example Implementation

### Backend Tenant API

```python
# backend/apps/tenants/urls.py
router = DefaultRouter()
router.register(r'', PublicTenantViewSet, basename='tenant')

urlpatterns = [
    path('', include(router.urls)),
]
```

```python
# backend/config/urls.py
urlpatterns = [
    path('api/tenants/', include('apps.tenants.urls')),
    ...
]
```

### Frontend Tenant Store

```javascript
// lib/stores/tenant.js
import { writable } from 'svelte/store';

export const selectedTenant = writable(null);
export const selectedOutlet = writable(null);

export function saveTenantChoice(tenant, outlet) {
    selectedTenant.set(tenant);
    selectedOutlet.set(outlet);
    
    localStorage.setItem('kiosk_tenant', JSON.stringify(tenant));
    localStorage.setItem('kiosk_outlet', JSON.stringify(outlet));
}

export function loadSavedTenant() {
    const tenant = JSON.parse(localStorage.getItem('kiosk_tenant') || 'null');
    const outlet = JSON.parse(localStorage.getItem('kiosk_outlet') || 'null');
    
    if (tenant) selectedTenant.set(tenant);
    if (outlet) selectedOutlet.set(outlet);
    
    return { tenant, outlet };
}
```

---

## Benefits

### For Business Owners
- ✅ Multi-tenant support from day 1
- ✅ Each restaurant has isolated data
- ✅ Easy to add new restaurants
- ✅ No cross-contamination

### For Customers
- ✅ Clear restaurant selection
- ✅ See correct menu for location
- ✅ No confusion
- ✅ Fast and simple

### For Developers
- ✅ Clean architecture
- ✅ Proper data isolation
- ✅ Easy to test
- ✅ Backward compatible

---

## Next Steps

**Implement Now?**

Saya bisa implementasikan tenant selection sekarang. Akan membutuhkan:

1. **Backend**: Tenant API endpoints (~30 mins)
2. **Backend**: Update ProductViewSet filtering (~15 mins)
3. **Frontend**: Tenant selector UI (~45 mins)
4. **Frontend**: Update API calls with headers (~15 mins)
5. **Testing**: End-to-end testing (~30 mins)

**Total**: ~2-3 hours

**Atau simpan untuk nanti?**

Kalau mau simpan dulu, current system tetap works (show all products). Tapi kalau mau proper multi-tenant, sebaiknya implement sekarang.

**Your choice!** 🎯
