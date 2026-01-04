# 01 - SYSTEM ARCHITECTURE

## Architecture Overview

Kiosk POS menggunakan **three-tier architecture** dengan **multi-tenant isolation** di setiap layer.

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  Cashier Terminal (SvelteKit)  │  Admin Panel (SvelteKit)       │
│  - Port 5173                   │  - Port 5175                   │
│  - Customer-facing interface   │  - Management interface        │
│  - Order processing            │  - Configuration               │
└──────────────┬─────────────────┴────────────────┬───────────────┘
               │                                  │
               │ HTTP/REST API                    │ HTTP/REST API
               │                                  │
┌──────────────┴──────────────────────────────────┴───────────────┐
│                      APPLICATION LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│                    Django REST Framework                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Tenants    │  │    Users     │  │   Products   │         │
│  │  (Multi-     │  │   (RBAC)     │  │  (Catalog)   │         │
│  │   Tenant)    │  └──────────────┘  └──────────────┘         │
│  └──────────────┘                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Orders     │  │  Promotions  │  │  Customers   │         │
│  │  (Process)   │  │   (Engine)   │  │  (Manage)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │   Payments   │  │   Kitchen    │                            │
│  │  (Multi-Pay) │  │   (Sync)     │                            │
│  └──────────────┘  └──────────────┘                            │
│                                                                  │
│  Middleware Stack:                                              │
│  → CORS Middleware                                              │
│  → Authentication (JWT)                                         │
│  → TenantMiddleware (URL-based tenant detection)               │
│  → SetTenantContextMiddleware (User-based tenant context)      │
│  → SetOutletContextMiddleware (Outlet context)                 │
└──────────────┬──────────────────────────────────────────────────┘
               │
               │ PostgreSQL Connection
               │
┌──────────────┴──────────────────────────────────────────────────┐
│                        DATA LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│                     PostgreSQL Database                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Tenant Isolation Strategy:                              │  │
│  │  - Every model has tenant_id foreign key                 │  │
│  │  - TenantModel base class enforces filtering             │  │
│  │  - Row-level security per tenant                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   REAL-TIME LAYER (Optional)                     │
├─────────────────────────────────────────────────────────────────┤
│  Kitchen Sync Server (Node.js WebSocket)                        │
│  - Port 3001                                                    │
│  - Real-time order updates                                      │
│  - Kitchen Display System integration                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Frontend Layer

#### Cashier Terminal (`frontend/`)
```
frontend/
├── src/
│   ├── routes/
│   │   ├── [tenant]/           # Tenant-specific routes
│   │   │   ├── products/       # Product listing
│   │   │   ├── cart/           # Shopping cart
│   │   │   ├── checkout/       # Payment processing
│   │   │   └── settings/       # Terminal settings
│   │   └── +layout.svelte      # Root layout
│   ├── lib/
│   │   ├── api/                # API clients
│   │   ├── stores/             # Svelte stores
│   │   ├── components/         # Reusable components
│   │   └── utils/              # Helper functions
│   └── app.html
└── vite.config.js
```

**Purpose**: Customer-facing interface for order processing
**Tech**: SvelteKit, TailwindCSS
**Port**: 5173

#### Admin Panel (`admin/`)
```
admin/
├── src/
│   ├── routes/
│   │   ├── auth/               # Login/logout
│   │   ├── dashboard/          # Overview
│   │   ├── products/           # Product management
│   │   ├── promotions/         # Promotion management
│   │   ├── customers/          # Customer management
│   │   ├── orders/             # Order history
│   │   ├── users/              # User management
│   │   ├── tenants/            # Tenant management (super admin)
│   │   └── settings/           # System settings
│   ├── lib/
│   │   ├── api/
│   │   ├── components/
│   │   └── stores/
│   └── app.html
└── vite.config.js
```

**Purpose**: Management interface for admins, owners, managers
**Tech**: SvelteKit, TailwindCSS
**Port**: 5175

---

### 2. Backend Layer

#### Django Application Structure
```
backend/
├── apps/
│   ├── core/               # Base models & utilities
│   │   ├── models.py      # TenantModel, BaseModel
│   │   ├── middleware.py  # Tenant & Outlet context
│   │   └── permissions.py # Custom permissions
│   │
│   ├── tenants/           # Multi-tenant management
│   │   ├── models.py      # Tenant, Outlet
│   │   ├── views.py       # Tenant CRUD
│   │   ├── serializers.py
│   │   └── middleware.py  # TenantMiddleware
│   │
│   ├── users/             # Authentication & RBAC
│   │   ├── models.py      # CustomUser
│   │   ├── views.py       # Auth endpoints
│   │   ├── serializers.py
│   │   └── permissions.py # Role-based permissions
│   │
│   ├── products/          # Product catalog
│   │   ├── models.py      # Product, Category
│   │   ├── views.py       # Product CRUD
│   │   └── serializers.py
│   │
│   ├── orders/            # Order processing
│   │   ├── models.py      # Order, OrderItem
│   │   ├── views.py       # Order endpoints
│   │   └── serializers.py
│   │
│   ├── payments/          # Payment handling
│   │   ├── models.py      # Payment
│   │   ├── views.py       # Payment processing
│   │   └── serializers.py
│   │
│   ├── kitchen/           # Kitchen display
│   │   ├── models.py      # KitchenOrder
│   │   ├── views.py       # Kitchen endpoints
│   │   └── consumers.py   # WebSocket consumers
│   │
│   ├── promotions/        # Promotion engine
│   │   ├── models.py      # Promotion, PromotionProduct
│   │   ├── views.py       # Promotion CRUD
│   │   ├── serializers.py
│   │   └── engine.py      # Promotion calculation logic
│   │
│   └── customers/         # Customer management
│       ├── models.py      # Customer
│       ├── views.py       # Customer CRUD
│       └── serializers.py
│
├── config/
│   ├── settings.py        # Django settings
│   ├── urls.py            # URL routing
│   └── wsgi.py
│
└── manage.py
```

---

### 3. Data Layer

#### Database Schema Pattern

Every tenant-specific model inherits from `TenantModel`:

```python
# apps/core/models.py
class TenantModel(models.Model):
    """
    Base model for all tenant-specific models.
    Automatically filters queries by current tenant.
    """
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    
    objects = TenantAwareManager()  # Tenant-filtered queries
    all_objects = models.Manager()   # Bypass tenant filter (admin only)
    
    class Meta:
        abstract = True
```

**Benefits**:
- ✅ Automatic tenant filtering
- ✅ Data isolation by default
- ✅ Admin can bypass with `all_objects`
- ✅ Prevents cross-tenant data leaks

---

## Data Flow Diagrams

### Flow 1: Order Processing (Online)

```
Customer → Cashier Terminal → Backend API → Database
                                    ↓
                            Kitchen Sync Server
                                    ↓
                            Kitchen Display
```

**Detailed Steps**:
1. Customer selects products in cashier terminal
2. Frontend calculates subtotal, applies promotions
3. Customer proceeds to checkout
4. Frontend sends order to `POST /api/orders/`
5. Backend validates order, checks inventory
6. Backend creates Order in database
7. Backend triggers payment processing
8. Backend sends order to Kitchen Sync Server (WebSocket)
9. Kitchen Sync broadcasts to all connected Kitchen Displays
10. Kitchen marks items as "in progress"
11. Kitchen marks order as "complete"
12. Customer receives notification

---

### Flow 1b: Order Processing (Offline)

```
Customer → Cashier Terminal → IndexedDB → Sync Queue
                 ↓                           ↓ (when online)
          Cart Saved                    Backend API
                                             ↓
                                        Database
                                             ↓
                                    Kitchen Sync Server
```

**Detailed Steps (Offline-First)**:
1. **Offline Detection**: Frontend detects no network connection
2. **Local Cart**: Customer adds items → saved to IndexedDB cart table
3. **Checkout Offline**: 
   - Frontend saves order to IndexedDB orders table
   - Adds to sync_queue with action='create'
   - Shows "Order saved offline, will sync when online"
4. **Payment Offline**: Saves payment to IndexedDB payments table
5. **Online Restored**: 
   - Auto-detect online event
   - Start background sync process
6. **Sync to Server**:
   - Read pending items from sync_queue
   - POST order to backend API
   - Backend creates order in PostgreSQL
   - Sends to Kitchen Sync Server
7. **Sync Complete**:
   - Remove from sync_queue
   - Update order.sync_status = 'synced'
8. **Kitchen Receives**: Order appears on kitchen display

**Benefits**:
- ✅ POS never stops working (100% uptime)
- ✅ No lost orders from connection issues
- ✅ Automatic retry with exponential backoff
- ✅ Manual intervention only after 5 failed retries
- ✅ Cart persists across browser refresh

---

### Flow 2: RBAC Permission Check

```
User Request → JWT Decode → Extract Role & Tenant → Check Permission
                                                            ↓
                                                      Allow/Deny
```

**Detailed Steps**:
1. User sends request with JWT token
2. `AuthenticationMiddleware` validates JWT
3. `TenantMiddleware` extracts tenant from URL/user
4. `SetTenantContextMiddleware` sets tenant context
5. View checks user role & permissions
6. If authorized → Process request
7. If unauthorized → Return 403 Forbidden

---

### Flow 3: Multi-Tenant Isolation

```
Request URL: /api/tenant-slug-1/products/

TenantMiddleware:
  ↓ Extract tenant from URL → tenant_slug_1
  ↓ Load Tenant from database
  ↓ Set request.tenant

View:
  ↓ Query: Product.objects.filter(tenant=request.tenant)
  ↓ Return only tenant-slug-1's products

Response: [products of tenant-slug-1 only]
```

---

## Key Architectural Patterns

### 1. Multi-Tenancy Pattern

**Implementation**: Row-Level Multi-Tenancy (Shared Database, Shared Schema)

```python
# Example: Product model
class Product(TenantModel):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # tenant field inherited from TenantModel
    
    class Meta:
        db_table = 'products'

# Usage in views
def get_products(request):
    # This automatically filters by request.tenant
    products = Product.objects.all()  
    return products
```

**Advantages**:
- ✅ Single database instance (cost-effective)
- ✅ Easy to maintain
- ✅ Simple backups
- ✅ Automatic tenant filtering

**Disadvantages**:
- ❌ All tenants share database resources
- ❌ One tenant's heavy query affects others
- ❌ Migration applies to all tenants

**Alternative Considered**: Database-per-tenant
- Rejected due to complexity & cost

---

### 2. Middleware Stack Pattern

Middlewares are executed in order:

```python
# config/settings.py
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',              # 1. CORS
    'django.middleware.security.SecurityMiddleware',       # 2. Security
    'django.contrib.sessions.middleware.SessionMiddleware',# 3. Sessions
    'django.contrib.auth.middleware.AuthenticationMiddleware', # 4. Auth
    'apps.tenants.middleware.TenantMiddleware',           # 5. Tenant detection
    'apps.core.middleware.SetTenantContextMiddleware',    # 6. Tenant context
    'apps.core.middleware.SetOutletContextMiddleware',    # 7. Outlet context
]
```

**Flow**:
1. **CORS**: Check if request origin is allowed
2. **Security**: Add security headers
3. **Sessions**: Load session data
4. **Auth**: Authenticate user from JWT
5. **TenantMiddleware**: Detect tenant from URL `/api/{tenant_slug}/`
6. **SetTenantContextMiddleware**: Set tenant context from authenticated user
7. **SetOutletContextMiddleware**: Set outlet context for operations

---

### 3. Repository Pattern (API Layer)

Frontend uses API abstraction layer:

```javascript
// admin/src/lib/api/products.js
export async function getProducts(tenantId, filters = {}) {
    const response = await fetch(
        `/api/products/?tenant_id=${tenantId}&${new URLSearchParams(filters)}`
    );
    return response.json();
}

export async function createProduct(productData) {
    const response = await fetch('/api/products/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(productData)
    });
    return response.json();
}
```

**Benefits**:
- ✅ Centralized API logic
- ✅ Easy to mock for testing
- ✅ Consistent error handling
- ✅ DRY principle

---

### 4. Store Pattern (State Management)

```javascript
// admin/src/lib/stores/auth.js
import { writable } from 'svelte/store';

export const user = writable(null);
export const tenant = writable(null);
export const outlet = writable(null);

export function setAuthData(userData) {
    user.set(userData);
    tenant.set(userData.tenant);
    outlet.set(userData.outlet);
}
```

**Usage**:
```svelte
<script>
    import { user, tenant } from '$lib/stores/auth';
    
    $: if ($user && $user.role === 'cashier') {
        // Cashier-specific UI
    }
</script>
```

---

## Security Architecture

### 1. Authentication Flow

```
┌──────────┐
│  Login   │
│  Request │
└────┬─────┘
     │
     ▼
┌─────────────────┐
│ Validate        │
│ Credentials     │
└────┬────────────┘
     │
     ▼
┌─────────────────┐     ┌──────────────┐
│ Generate JWT    │────→│ Access Token │
│ (Access +       │     │ (15 min)     │
│  Refresh)       │     └──────────────┘
└────┬────────────┘     ┌──────────────┐
     │                  │ Refresh Token│
     └─────────────────→│ (7 days)     │
                        └──────────────┘
```

**Token Structure**:
```json
{
  "user_id": 123,
  "username": "john_cashier",
  "role": "cashier",
  "tenant_id": 67,
  "outlet_id": 45,
  "exp": 1234567890
}
```

---

### 2. Authorization Layers

**Layer 1: View-Level Permission**
```python
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import IsTenantUser

class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsTenantUser]
```

**Layer 2: Object-Level Permission**
```python
def has_object_permission(self, request, view, obj):
    # Check if object belongs to user's tenant
    return obj.tenant_id == request.user.tenant_id
```

**Layer 3: Field-Level Permission**
```python
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'cost']  # cost only for managers
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context['request'].user.role == 'cashier':
            self.fields.pop('cost')  # Hide cost from cashiers
```

---

### 3. Tenant Isolation Enforcement

```python
# apps/tenants/middleware.py
class TenantMiddleware:
    def __call__(self, request):
        # Extract tenant from URL
        tenant_slug = self.extract_tenant_slug(request.path)
        
        if tenant_slug:
            try:
                tenant = Tenant.objects.get(slug=tenant_slug)
                request.tenant = tenant
            except Tenant.DoesNotExist:
                return HttpResponseNotFound("Tenant not found")
        
        return self.get_response(request)
```

```python
# apps/core/managers.py
class TenantAwareManager(models.Manager):
    def get_queryset(self):
        # Automatically filter by current tenant
        from apps.core.middleware import get_current_tenant
        tenant = get_current_tenant()
        if tenant:
            return super().get_queryset().filter(tenant=tenant)
        return super().get_queryset()
```

---

## Performance Optimization

### 1. Database Query Optimization

**Problem**: N+1 queries when loading orders with items

**Solution**: Use `select_related` and `prefetch_related`
```python
orders = Order.objects.select_related('customer', 'outlet').prefetch_related(
    'items__product',
    'payments'
).filter(tenant=request.tenant)
```

---

### 2. Caching Strategy

**Cache Layers**:
1. **Browser Cache**: Static assets (images, JS, CSS)
2. **API Response Cache**: Product listings, categories
3. **Database Query Cache**: Frequently accessed data

```python
from django.core.cache import cache

def get_products_cached(tenant_id):
    cache_key = f'products_tenant_{tenant_id}'
    products = cache.get(cache_key)
    
    if not products:
        products = list(Product.objects.filter(tenant_id=tenant_id))
        cache.set(cache_key, products, timeout=300)  # 5 minutes
    
    return products
```

---

### 3. Real-Time Communication Optimization

**WebSocket Connection Pooling**:
- One connection per kitchen display
- Broadcast to multiple displays
- Automatic reconnection on failure

```javascript
// Kitchen Sync Server
io.on('connection', (socket) => {
    socket.on('subscribe', (outletId) => {
        socket.join(`outlet_${outletId}`);
    });
    
    socket.on('new_order', (order) => {
        io.to(`outlet_${order.outlet_id}`).emit('order_update', order);
    });
});
```

---

## Scalability Considerations

### Horizontal Scaling

**Current Setup**: Single server (Docker Compose)

**Scaling Path**:
```
Stage 1: Monolith (Current)
  ↓
Stage 2: Load Balancer + Multiple App Servers
  ↓
Stage 3: Separate Database Server
  ↓
Stage 4: Microservices (Orders, Products, Kitchen as separate services)
  ↓
Stage 5: Multi-Region Deployment
```

---

### Database Scaling

**Current**: Single PostgreSQL instance

**Scaling Options**:
1. **Read Replicas**: Separate read/write databases
2. **Partitioning**: Partition by tenant_id
3. **Sharding**: Different databases for different tenant groups

```python
# Future: Database routing
class TenantRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'orders':
            return 'orders_db'
        return 'default'
```

---

## Deployment Architecture

### Development
```
Developer Machine
├── Docker Compose
│   ├── Backend (Django)
│   ├── Frontend (Vite Dev Server)
│   ├── Admin (Vite Dev Server)
│   ├── PostgreSQL
│   └── Nginx (reverse proxy)
```

### Production (Planned)
```
Cloud Provider (AWS/GCP/Azure)
├── Load Balancer
│   ├── Backend Instances (Auto-scaling)
│   ├── Static Assets (CDN)
│   └── WebSocket Server (Kitchen Sync)
├── Managed PostgreSQL (RDS/Cloud SQL)
├── Redis (Caching)
└── S3/Cloud Storage (Media files)
```

---

## Design Decisions & Trade-offs

### Decision 1: Row-Level Multi-Tenancy
**Chosen**: Shared database with tenant_id column
**Alternatives**: Database per tenant, Schema per tenant
**Rationale**: Cost-effective, easier to maintain, sufficient isolation
**Trade-off**: Potential cross-tenant query risk (mitigated by TenantModel)

### Decision 2: JWT Authentication
**Chosen**: JWT with short-lived access tokens
**Alternatives**: Session-based auth, OAuth
**Rationale**: Stateless, scalable, mobile-friendly
**Trade-off**: Cannot revoke tokens immediately (mitigated by short expiry)

### Decision 3: SvelteKit for Frontend
**Chosen**: SvelteKit
**Alternatives**: React, Vue, Angular
**Rationale**: Small bundle size, fast performance, SSR support
**Trade-off**: Smaller ecosystem than React

### Decision 4: WebSocket for Kitchen Sync
**Chosen**: Separate Node.js WebSocket server
**Alternatives**: Django Channels, Polling
**Rationale**: Real-time, efficient, dedicated service
**Trade-off**: Additional service to maintain

---

## Component Communication

### API Communication Pattern
```
Frontend ←→ Backend
  HTTP REST API
  - JSON request/response
  - JWT authentication
  - Tenant-specific endpoints
```

### Real-Time Communication Pattern
```
Backend → Kitchen Sync Server → Kitchen Display
  HTTP POST      WebSocket        WebSocket
```

---

## Error Handling Strategy

### Backend Error Responses
```json
{
  "error": "ValidationError",
  "message": "Product price must be positive",
  "field": "price",
  "code": "INVALID_PRICE"
}
```

### Frontend Error Handling
```javascript
try {
    await createProduct(data);
} catch (error) {
    if (error.code === 'INVALID_PRICE') {
        showError('Price must be positive');
    } else {
        showError('Failed to create product');
    }
}
```

---

**Last Updated**: January 4, 2026  
**Version**: 2.0  
**Next Review**: Architecture review scheduled for Q2 2026
