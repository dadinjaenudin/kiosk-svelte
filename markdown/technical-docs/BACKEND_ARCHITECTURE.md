# 🔧 Backend Architecture - Django REST API

## Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Django Apps & Responsibilities](#django-apps--responsibilities)
- [Request Flow](#request-flow)
- [Middleware Chain](#middleware-chain)
- [Authentication & Authorization](#authentication--authorization)
- [Database Models](#database-models)
- [API Design](#api-design)
- [Background Tasks](#background-tasks)

---

## Overview

Backend menggunakan **Django 4.2** dengan **Django REST Framework (DRF)** untuk menyediakan RESTful API. Struktur project mengikuti **app-based architecture** dimana setiap app memiliki tanggung jawab spesifik.

### Key Principles

- **Separation of Concerns**: Setiap app independent dan focused
- **DRY (Don't Repeat Yourself)**: Shared logic di `apps.core`
- **Fat Models, Thin Views**: Business logic di models/services, bukan views
- **API-First**: Semua operasi melalui REST API
- **Multi-Tenancy**: Data isolation per tenant

---

## Project Structure

```
backend/
├── config/                      # Django settings & configuration
│   ├── settings.py             # Main settings
│   ├── urls.py                 # Root URL routing
│   ├── wsgi.py                 # WSGI entry point
│   └── celery.py               # Celery configuration
│
├── apps/                       # Django applications
│   ├── core/                   # Shared utilities & base models
│   │   ├── models.py          # TenantModel, TimeStampedModel
│   │   ├── middleware.py      # Context middleware
│   │   ├── context.py         # Thread-local storage
│   │   ├── permissions.py     # Custom DRF permissions
│   │   └── utils.py           # Helper functions
│   │
│   ├── tenants/               # Multi-tenant management
│   │   ├── models.py         # Tenant, Outlet models
│   │   ├── middleware.py     # TenantMiddleware
│   │   ├── views.py          # Tenant CRUD API
│   │   ├── serializers.py    # Tenant serializers
│   │   └── urls.py           # Tenant routes
│   │
│   ├── users/                 # User & authentication
│   │   ├── models.py         # Custom User model
│   │   ├── views.py          # Auth, registration, profile
│   │   ├── serializers.py    # User serializers
│   │   ├── permissions.py    # Role-based permissions
│   │   ├── auth_urls.py      # Auth routes (login, register)
│   │   └── urls.py           # User management routes
│   │
│   ├── products/              # Product & menu management
│   │   ├── models.py         # Product, Category, Modifier
│   │   ├── views.py          # Product CRUD API
│   │   ├── serializers.py    # Product serializers
│   │   ├── filters.py        # Product filtering
│   │   └── urls.py           # Product routes
│   │
│   ├── orders/                # Order management
│   │   ├── models.py         # Order, OrderItem
│   │   ├── views.py          # Order API
│   │   ├── serializers.py    # Order serializers
│   │   ├── services.py       # Order business logic
│   │   └── urls.py           # Order routes
│   │
│   ├── payments/              # Payment processing
│   │   ├── models.py         # Payment, Transaction
│   │   ├── views.py          # Payment API
│   │   ├── gateways/         # Payment gateway integrations
│   │   │   ├── midtrans.py
│   │   │   └── xendit.py
│   │   └── urls.py
│   │
│   ├── kitchen/               # Kitchen operations
│   │   ├── models.py         # Kitchen display data
│   │   ├── views.py          # Kitchen API
│   │   └── urls.py
│   │
│   ├── promotions/            # Promotion & discount
│   │   ├── models.py         # Promotion, PromoCode
│   │   ├── views.py          # Promotion API
│   │   ├── services.py       # Promo calculation logic
│   │   └── urls.py
│   │
│   └── customers/             # Customer management
│       ├── models.py         # Customer, Loyalty
│       ├── views.py          # Customer API
│       └── urls.py
│
├── media/                      # Uploaded files (images, etc)
├── static/                     # Static files
├── staticfiles/                # Collected static files
├── manage.py                   # Django CLI
├── requirements.txt            # Python dependencies
└── Dockerfile                  # Docker image definition
```

---

## Django Apps & Responsibilities

### 1. **core** - Shared Utilities

**Purpose**: Base models, utilities, dan shared functionality.

```python
# apps/core/models.py
class TenantModel(models.Model):
    """Abstract base model for tenant-aware models"""
    class Meta:
        abstract = True
    
    def get_queryset(self):
        # Auto-filter by current tenant
        pass

class TimeStampedModel(models.Model):
    """Abstract base with created_at/updated_at"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
```

**Files**:
- `models.py`: Base abstract models
- `middleware.py`: Context middleware
- `context.py`: Thread-local storage untuk tenant context
- `permissions.py`: Custom DRF permissions
- `utils.py`: Helper functions (formatting, validation)

### 2. **tenants** - Multi-Tenant Management

**Purpose**: Mengelola tenants (brands) dan outlets (stores).

**Models**:
```python
class Tenant(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    logo = models.ImageField()
    tax_rate = models.DecimalField()
    service_charge_rate = models.DecimalField()
    # ... branding, business info

class Outlet(models.Model):
    tenant = models.ForeignKey(Tenant)
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField()
    # ... location, operational hours
```

**Key Features**:
- Tenant CRUD for admin
- Outlet management per tenant
- Tenant-based filtering via middleware

### 3. **users** - Authentication & User Management

**Purpose**: User authentication, authorization, dan role management.

**Custom User Model**:
```python
class User(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('tenant_owner', 'Tenant Owner'),
        ('manager', 'Manager'),
        ('cashier', 'Cashier'),
        ('kitchen', 'Kitchen Staff'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    tenant = models.ForeignKey(Tenant, null=True)
    outlet = models.ForeignKey(Outlet, null=True)
    accessible_outlets = models.ManyToManyField(Outlet)
```

**Authentication Methods**:
1. **JWT (JSON Web Token)** - Untuk Kiosk & Mobile
   - `/api/auth/token/` - Get access & refresh token
   - `/api/auth/token/refresh/` - Refresh access token

2. **Token-based** - Untuk Admin Panel
   - `/api/auth/login/` - Login dengan username/password
   - Returns DRF Token

**Permission System**:
```python
# apps/users/permissions.py
class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'super_admin'

class IsAdminOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['admin', 'tenant_owner']
```

### 4. **products** - Product & Menu Management

**Purpose**: Mengelola produk, kategori, dan modifier.

**Models**:
```python
class Category(TenantModel):
    tenant = models.ForeignKey(Tenant)
    name = models.CharField()
    sort_order = models.IntegerField()
    is_active = models.BooleanField()

class Product(TenantModel):
    tenant = models.ForeignKey(Tenant)
    outlet = models.ForeignKey(Outlet, null=True, blank=True)  # Outlet-specific
    category = models.ForeignKey(Category)
    
    sku = models.CharField(unique=True)
    name = models.CharField()
    price = models.DecimalField()
    
    # Stock management
    track_stock = models.BooleanField()
    stock_quantity = models.IntegerField()
    
    # Promo support
    has_promo = models.BooleanField()
    promo_price = models.DecimalField(null=True)
    
    # Flags
    is_active = models.BooleanField()
    is_available = models.BooleanField()
    is_popular = models.BooleanField()

class ProductModifier(models.Model):
    product = models.ForeignKey(Product, null=True)  # null = global
    name = models.CharField()  # "Size", "Topping", "Spicy Level"
    type = models.CharField(choices=MODIFIER_TYPES)
    price_adjustment = models.DecimalField()
```

**Key Features**:
- Multi-outlet product support (shared atau outlet-specific)
- Category-based organization
- Stock tracking
- Modifier system (size, topping, dll)
- Promo price support

### 5. **orders** - Order Management

**Purpose**: Mengelola order lifecycle dari draft sampai completed.

**Models**:
```python
class Order(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    tenant = models.ForeignKey(Tenant)
    outlet = models.ForeignKey(Outlet)
    order_number = models.CharField(unique=True)
    status = models.CharField(choices=STATUS_CHOICES)
    
    # Customer (optional for walk-in)
    customer_name = models.CharField()
    customer_phone = models.CharField()
    
    # Pricing
    subtotal = models.DecimalField()
    tax_amount = models.DecimalField()
    service_charge_amount = models.DecimalField()
    discount_amount = models.DecimalField()
    total_amount = models.DecimalField()
    
    # Payment
    payment_status = models.CharField()
    paid_amount = models.DecimalField()
    
    cashier = models.ForeignKey(User)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items')
    product = models.ForeignKey(Product)
    product_name = models.CharField()  # Snapshot
    quantity = models.IntegerField()
    unit_price = models.DecimalField()
    total_price = models.DecimalField()
    notes = models.TextField()
```

**Order Service**:
```python
# apps/orders/services.py
class OrderService:
    @staticmethod
    def create_order(tenant, outlet, cart_items, customer_info):
        """Create order from cart"""
        order = Order.objects.create(
            tenant=tenant,
            outlet=outlet,
            # ...
        )
        
        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                # ...
            )
        
        # Calculate totals
        order.calculate_totals()
        
        return order
    
    @staticmethod
    def apply_discount(order, promo_code):
        """Apply promotion discount"""
        # Validation & calculation
        pass
```

### 6. **payments** - Payment Processing

**Purpose**: Integrasi dengan payment gateway dan payment tracking.

**Models**:
```python
class Payment(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('qris', 'QRIS'),
        ('card', 'Debit/Credit Card'),
        ('ewallet', 'E-Wallet'),
    )
    
    order = models.ForeignKey(Order)
    method = models.CharField(choices=PAYMENT_METHODS)
    amount = models.DecimalField()
    status = models.CharField()  # pending, success, failed
    transaction_id = models.CharField()
    gateway_response = models.JSONField()
```

**Payment Gateway Integration**:
```python
# apps/payments/gateways/midtrans.py
class MidtransGateway:
    def create_transaction(self, order):
        """Create Midtrans transaction"""
        payload = {
            'transaction_details': {
                'order_id': order.order_number,
                'gross_amount': int(order.total_amount)
            },
            # ...
        }
        response = midtrans_api.charge(payload)
        return response

# apps/payments/gateways/xendit.py
class XenditGateway:
    def create_invoice(self, order):
        """Create Xendit invoice"""
        pass
```

### 7. **promotions** - Promotion Management

**Purpose**: Discount, promo code, dan campaign management.

**Models**:
```python
class Promotion(models.Model):
    PROMO_TYPES = (
        ('percentage', 'Percentage Discount'),
        ('fixed', 'Fixed Amount'),
        ('buy_x_get_y', 'Buy X Get Y'),
        ('bundle', 'Bundle Deal'),
    )
    
    tenant = models.ForeignKey(Tenant)
    name = models.CharField()
    type = models.CharField(choices=PROMO_TYPES)
    code = models.CharField(unique=True)
    
    # Discount rules
    discount_value = models.DecimalField()
    min_purchase = models.DecimalField()
    max_discount = models.DecimalField()
    
    # Applicable products
    applies_to_products = models.ManyToManyField(Product)
    applies_to_categories = models.ManyToManyField(Category)
    
    # Validity
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField()
```

### 8. **customers** - Customer Management

**Purpose**: Customer data, loyalty program, order history.

**Models**:
```python
class Customer(models.Model):
    tenant = models.ForeignKey(Tenant)
    name = models.CharField()
    email = models.EmailField()
    phone = models.CharField()
    
    # Loyalty
    loyalty_points = models.IntegerField(default=0)
    total_spent = models.DecimalField(default=0)
    visit_count = models.IntegerField(default=0)
```

---

## Request Flow

### Complete Request Lifecycle

```
1. HTTP Request arrives at Nginx
   └─> Reverse proxy to Django (port 8000)

2. Django receives request
   └─> WSGI (Gunicorn) processes

3. Middleware Chain (in order)
   ├─> CorsMiddleware - Handle CORS
   ├─> SecurityMiddleware - Security headers
   ├─> SessionMiddleware - Session handling
   ├─> AuthenticationMiddleware - JWT/Token auth
   ├─> TenantMiddleware - Extract tenant from header
   ├─> SetTenantContextMiddleware - Set thread-local context
   └─> SetOutletContextMiddleware - Set outlet context

4. URL Routing (urls.py)
   └─> Match URL pattern to view

5. View Processing
   ├─> DRF View/ViewSet
   ├─> Permission check (IsAuthenticated, etc)
   ├─> Validation (Serializer)
   ├─> Business logic (Service layer)
   └─> Database query (ORM + tenant filter)

6. Response
   ├─> Serialization (DRF Serializer)
   ├─> Format response (JSON)
   └─> HTTP Response
```

### Example: Create Order Request

```http
POST /api/orders/checkout/
Host: api.example.com
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>
X-Tenant-ID: 123
X-Outlet-ID: 456

{
  "customer_name": "John Doe",
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```

**Processing Steps**:

1. **TenantMiddleware** extracts `X-Tenant-ID: 123` dan `X-Outlet-ID: 456`
2. **AuthenticationMiddleware** validates JWT token
3. **URL Router** matches `/api/orders/checkout/` → `OrderViewSet.checkout()`
4. **Permission Check**: User must be authenticated
5. **Serializer Validation**: Validate request data
6. **Service Layer**: `OrderService.create_order()`
   - Fetch products (auto-filtered by tenant)
   - Calculate totals
   - Create Order & OrderItems
   - Update stock
7. **Response**: Serialized order data

```json
{
  "success": true,
  "order": {
    "id": 789,
    "order_number": "ORD-20260103-A1B2",
    "status": "pending",
    "total_amount": 150000,
    "items": [...]
  }
}
```

---

## Middleware Chain

### 1. TenantMiddleware

**Purpose**: Extract tenant & outlet dari request headers.

```python
# apps/tenants/middleware.py
class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tenant_id = request.headers.get('X-Tenant-ID')
        outlet_id = request.headers.get('X-Outlet-ID')
        
        if tenant_id:
            tenant = Tenant.objects.get(id=tenant_id)
            set_current_tenant(tenant)
        
        if outlet_id:
            outlet = Outlet.objects.get(id=outlet_id)
            set_current_outlet(outlet)
```

### 2. SetTenantContextMiddleware

**Purpose**: Set tenant context untuk admin operations.

```python
# apps/core/middleware.py
class SetTenantContextMiddleware:
    def __call__(self, request):
        user = request.user
        
        # If user has tenant, set as context
        if user.is_authenticated and user.tenant:
            set_current_tenant(user.tenant)
        
        response = self.get_response(request)
        
        # Clear context after request
        clear_tenant_context()
        
        return response
```

### 3. Thread-Local Context

**Purpose**: Store tenant/outlet context untuk diakses di mana saja.

```python
# apps/core/context.py
import threading

_thread_locals = threading.local()

def set_current_tenant(tenant):
    _thread_locals.tenant = tenant

def get_current_tenant():
    return getattr(_thread_locals, 'tenant', None)

def set_current_outlet(outlet):
    _thread_locals.outlet = outlet

def get_current_outlet():
    return getattr(_thread_locals, 'outlet', None)

def clear_tenant_context():
    _thread_locals.tenant = None
    _thread_locals.outlet = None
```

**Usage in Views**:

```python
from apps.core.context import get_current_tenant, get_current_outlet

class ProductViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        tenant = get_current_tenant()
        outlet = get_current_outlet()
        
        qs = Product.objects.filter(tenant=tenant)
        
        if outlet:
            # Filter by outlet or shared products
            qs = qs.filter(
                models.Q(outlet=outlet) |
                models.Q(outlet__isnull=True)
            )
        
        return qs
```

---

## Authentication & Authorization

### JWT Authentication

**Settings**:
```python
# config/settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ALGORITHM': 'HS256',
}
```

**Login Flow**:
```python
# POST /api/auth/token/
{
  "username": "cashier1",
  "password": "password123"
}

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "cashier1",
    "role": "cashier",
    "tenant_id": 123
  }
}
```

### Role-Based Permissions

```python
# apps/users/permissions.py
class IsSuperAdmin(permissions.BasePermission):
    """Only super admins"""
    def has_permission(self, request, view):
        return request.user.role == 'super_admin'

class IsAdminOrOwner(permissions.BasePermission):
    """Admins or tenant owners"""
    def has_permission(self, request, view):
        return request.user.role in ['admin', 'tenant_owner']

class IsCashierOrAbove(permissions.BasePermission):
    """Cashier, manager, or admin"""
    def has_permission(self, request, view):
        return request.user.role in ['cashier', 'manager', 'admin']
```

**Usage in Views**:
```python
class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrOwner]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # Public can view
            return []
        else:
            # Create/Update/Delete require admin
            return [IsAuthenticated(), IsAdminOrOwner()]
```

---

## Database Models

### Model Relationships

```
Tenant (1) ──── (N) Outlet
   │                  │
   │                  │
   ├──(N) Product     │
   │      │           │
   │      └──(N) OrderItem
   │                  │
   ├──(N) Category    │
   │                  │
   ├──(N) User ───────┘
   │      │
   │      └──(N) Order ──── (N) OrderItem
   │               │
   ├──(N) Promotion│
   │               │
   └──(N) Customer │
                   │
              (1) Payment
```

### Key Relationships

1. **Tenant → Outlet**: One-to-Many
2. **Tenant → Product**: One-to-Many (dapat outlet-specific)
3. **Product → OrderItem**: One-to-Many
4. **Order → OrderItem**: One-to-Many
5. **User → Tenant**: Many-to-One
6. **User → Outlet**: Many-to-Many (accessible_outlets)

---

## API Design

### REST Conventions

```
GET    /api/products/           - List all products
POST   /api/products/           - Create product
GET    /api/products/{id}/      - Get product detail
PUT    /api/products/{id}/      - Update product
PATCH  /api/products/{id}/      - Partial update
DELETE /api/products/{id}/      - Delete product
```

### Custom Actions

```python
class OrderViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """POST /api/orders/checkout/"""
        # Create order from cart
        pass
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """POST /api/orders/{id}/cancel/"""
        # Cancel order
        pass
```

### Response Format

**Success**:
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

**Error**:
```json
{
  "success": false,
  "error": "Error message",
  "details": { ... }
}
```

---

## Background Tasks

### Celery Configuration

```python
# config/celery.py
from celery import Celery

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# config/settings.py
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
```

### Example Tasks

```python
# apps/orders/tasks.py
from celery import shared_task

@shared_task
def send_order_notification(order_id):
    """Send notification to kitchen"""
    order = Order.objects.get(id=order_id)
    # Send notification logic
    pass

@shared_task
def generate_daily_report(outlet_id):
    """Generate daily sales report"""
    # Report generation logic
    pass
```

**Usage**:
```python
# In view
from apps.orders.tasks import send_order_notification

order = Order.objects.create(...)
send_order_notification.delay(order.id)  # Async
```

---

## Next Steps

- **[BACKEND_API_REFERENCE.md](BACKEND_API_REFERENCE.md)** - Complete API documentation
- **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)** - Database schema details
- **[MULTI_TENANT_DEEP_DIVE.md](MULTI_TENANT_DEEP_DIVE.md)** - Multi-tenant implementation

---

**Last Updated**: January 3, 2026
