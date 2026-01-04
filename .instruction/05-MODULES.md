# 05 - APPLICATION MODULES

## Module Overview

Kiosk POS application terdiri dari **9 main modules** yang saling terintegrasi untuk menyediakan complete POS solution.

```
┌─────────────────────────────────────────────────────────────┐
│                    KIOSK POS MODULES                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ TENANTS  │  │  USERS   │  │ PRODUCTS │  │  ORDERS  │  │
│  │  (Core)  │  │  (Auth)  │  │(Catalog) │  │(Process) │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ PAYMENTS │  │PROMOTIONS│  │CUSTOMERS │  │ KITCHEN  │  │
│  │(Gateway) │  │ (Engine) │  │  (CRM)   │  │  (Sync)  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                              │
│  ┌──────────┐                                               │
│  │   CORE   │ (Base models, middleware, permissions)       │
│  └──────────┘                                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. TENANTS Module

**Location**: `backend/apps/tenants/`  
**Purpose**: Multi-tenant management & outlet handling

### Models
- **Tenant**: Restaurant brands/franchises
- **Outlet**: Physical store locations

### API Endpoints

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/tenants/` | super_admin | List all tenants |
| POST | `/api/tenants/` | super_admin | Create new tenant |
| GET | `/api/tenants/:id/` | tenant_owner+ | Get tenant details |
| PATCH | `/api/tenants/:id/` | tenant_owner+ | Update tenant |
| DELETE | `/api/tenants/:id/` | super_admin | Delete tenant |
| GET | `/api/outlets/` | manager+ | List outlets |
| POST | `/api/outlets/` | tenant_owner+ | Create outlet |
| GET | `/api/outlets/:id/` | manager+ | Get outlet details |
| PATCH | `/api/outlets/:id/` | manager+ | Update outlet |

### Key Features
✅ Tenant branding (logo, colors)  
✅ Tax & service charge configuration  
✅ Multi-outlet support  
✅ Outlet location & hours  
✅ WebSocket configuration per outlet

### Usage Example
```python
# Create tenant
tenant = Tenant.objects.create(
    name="Pizza Palace",
    slug="pizza-palace",
    primary_color="#FF6B35",
    tax_rate=10.00
)

# Create outlet
outlet = Outlet.objects.create(
    tenant=tenant,
    name="Mall Yogya",
    address="Jl. Affandi No.10",
    phone="0274-123456"
)
```

---

## 2. USERS Module

**Location**: `backend/apps/users/`  
**Purpose**: Authentication & role-based access control

### Models
- **User**: Custom user with roles & tenant association

### Roles
1. **super_admin**: System administrator
2. **admin**: Technical support
3. **tenant_owner**: Franchise owner
4. **manager**: Store manager
5. **cashier**: Front-line staff
6. **kitchen**: Kitchen staff

### API Endpoints

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/auth/login/` | public | Login (JWT) |
| POST | `/api/auth/register/` | admin+ | Register user |
| POST | `/api/auth/refresh/` | authenticated | Refresh token |
| GET | `/api/users/` | manager+ | List users |
| POST | `/api/users/` | manager+ | Create user |
| GET | `/api/users/:id/` | owner | Get user details |
| PATCH | `/api/users/:id/` | owner | Update user |
| GET | `/api/users/me/` | authenticated | Current user |

### Key Features
✅ JWT authentication  
✅ Role-based permissions  
✅ Tenant isolation  
✅ Multi-outlet access (managers)  
✅ User profile management

### Usage Example
```python
# Create user
user = User.objects.create_user(
    username='john_cashier',
    password='secure_password',
    role='cashier',
    tenant=tenant,
    outlet=outlet
)

# Login
response = client.post('/api/auth/login/', {
    'username': 'john_cashier',
    'password': 'secure_password'
})
access_token = response.data['access']
```

---

## 3. PRODUCTS Module

**Location**: `backend/apps/products/`  
**Purpose**: Product catalog & inventory management

### Models
- **Category**: Product categories
- **Product**: Menu items
- **ProductModifier**: Customizations (size, toppings)
- **OutletProduct**: Per-outlet pricing & availability

### API Endpoints

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/categories/` | public | List categories |
| POST | `/api/categories/` | manager+ | Create category |
| GET | `/api/products/` | public | List products |
| POST | `/api/products/` | manager+ | Create product |
| GET | `/api/products/:id/` | public | Get product details |
| PATCH | `/api/products/:id/` | manager+ | Update product |
| DELETE | `/api/products/:id/` | manager+ | Delete product |
| GET | `/api/products/:id/modifiers/` | public | Get modifiers |
| POST | `/api/products/:id/modifiers/` | manager+ | Add modifier |

### Key Features
✅ Product catalog with images  
✅ Category organization  
✅ Price management  
✅ Stock tracking  
✅ Product modifiers (size, toppings)  
✅ Outlet-specific pricing  
✅ Bulk import/export

### Usage Example
```python
# Create product
product = Product.objects.create(
    tenant=tenant,
    category=category,
    sku='PIZZA-001',
    name='Pepperoni Pizza',
    description='Classic pepperoni pizza',
    price=95000,
    is_available=True
)

# Add modifier
modifier = ProductModifier.objects.create(
    product=product,
    name='Large Size',
    type='size',
    price_modifier=15000
)
```

---

## 4. ORDERS Module

**Location**: `backend/apps/orders/`  
**Purpose**: Order processing & management

### Models
- **Order**: Customer orders
- **OrderItem**: Order line items

### Order Status Flow
```
draft → pending → confirmed → preparing → ready → served → completed
                                    ↓
                              cancelled
```

### API Endpoints

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/orders/` | cashier+ | List orders |
| POST | `/api/orders/` | cashier+ | Create order |
| GET | `/api/orders/:id/` | cashier+ | Get order details |
| PATCH | `/api/orders/:id/` | cashier+ | Update order |
| POST | `/api/orders/:id/confirm/` | cashier+ | Confirm order |
| POST | `/api/orders/:id/cancel/` | manager+ | Cancel order |
| POST | `/api/orders/:id/complete/` | cashier+ | Complete order |
| GET | `/api/orders/:id/receipt/` | cashier+ | Get receipt |

### Key Features
✅ Multi-item orders  
✅ Product modifiers per item  
✅ Order status tracking  
✅ Tax & service charge calculation  
✅ Promotion application  
✅ Order history  
✅ Receipt generation

### Usage Example
```python
# Create order
order = Order.objects.create(
    tenant=tenant,
    outlet=outlet,
    customer_name='John Doe',
    customer_phone='08123456789',
    source='kiosk'
)

# Add items
OrderItem.objects.create(
    order=order,
    product=product,
    product_name=product.name,
    quantity=2,
    unit_price=product.price,
    total_price=product.price * 2
)

# Calculate totals
order.calculate_totals()
```

---

## 5. PAYMENTS Module

**Location**: `backend/apps/payments/`  
**Purpose**: Payment processing & gateway integration

### Models
- **Payment**: Payment transactions
- **PaymentCallback**: Webhook logs

### Payment Methods
- 💵 **Cash**: Direct cash payment
- 📱 **QRIS**: QR code Indonesian standard
- 💳 **E-Wallets**: GoPay, OVO, ShopeePay, DANA
- 💳 **Cards**: Debit/Credit cards

### Payment Gateways
- **Midtrans**: Primary gateway
- **Xendit**: Alternative gateway
- **Stripe**: International payments (future)

### API Endpoints

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| POST | `/api/payments/` | cashier+ | Create payment |
| GET | `/api/payments/:id/` | cashier+ | Get payment status |
| POST | `/api/payments/:id/cancel/` | manager+ | Cancel payment |
| POST | `/api/payments/webhook/` | public | Payment callback |

### Key Features
✅ Multiple payment methods  
✅ QR code generation  
✅ Payment gateway integration  
✅ Webhook handling  
✅ Payment retry  
✅ Refund support  
✅ Transaction logging

### Usage Example
```python
# Create payment
payment = Payment.objects.create(
    order=order,
    payment_method='qris',
    provider='midtrans',
    amount=order.total_amount
)

# Process payment
result = payment.process()
if result['status'] == 'pending':
    qr_code_url = result['qr_code_url']
```

---

## 6. PROMOTIONS Module

**Location**: `backend/apps/promotions/`  
**Purpose**: Discount & promotion management

### Models
- **Promotion**: Promotion campaigns
- **PromotionProduct**: Product associations
- **PromotionUsage**: Usage tracking

### Promotion Types
1. **Percentage Discount**: % off products
2. **Fixed Amount**: Rp X off
3. **Buy X Get Y**: Buy quantity, get free/discount
4. **Bundle Deal**: Package deals

### API Endpoints

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/promotions/` | manager+ | List promotions |
| POST | `/api/promotions/` | manager+ | Create promotion |
| GET | `/api/promotions/:id/` | manager+ | Get promotion |
| PATCH | `/api/promotions/:id/` | manager+ | Update promotion |
| DELETE | `/api/promotions/:id/` | manager+ | Delete promotion |
| POST | `/api/promotions/:id/activate/` | manager+ | Activate promotion |
| GET | `/api/promotions/active/` | public | Get active promos |
| POST | `/api/promotions/apply/` | cashier+ | Apply to order |

### Key Features
✅ 4 promotion types  
✅ Product role (buy/get/both)  
✅ Time-based activation  
✅ Usage limits  
✅ Per-customer limits  
✅ Promotion code system  
✅ Auto-application  
✅ Stackable promotions

### Usage Example
```python
# Create promotion
promotion = Promotion.objects.create(
    tenant=tenant,
    name='Weekend Flash Sale',
    promo_type='percentage',
    discount_value=30,
    start_date=datetime.now(),
    end_date=datetime.now() + timedelta(days=2),
    is_active=True
)

# Add products
promotion.products.add(product1, product2)

# Apply to order
discount = promotion.calculate_discount(order)
order.discount_amount = discount
```

---

## 7. CUSTOMERS Module

**Location**: `backend/apps/customers/`  
**Purpose**: Customer relationship management

### Models
- **Customer**: Customer profiles

### Membership Tiers
- 🥉 **Regular**: Default tier
- 🥈 **Silver**: 10+ orders or Rp 1M spent
- 🥇 **Gold**: 50+ orders or Rp 5M spent
- 💎 **Platinum**: 100+ orders or Rp 10M spent

### API Endpoints

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/customers/` | cashier+ | List customers |
| POST | `/api/customers/` | cashier+ | Create customer |
| GET | `/api/customers/:id/` | cashier+ | Get customer |
| PATCH | `/api/customers/:id/` | cashier+ | Update customer |
| GET | `/api/customers/:id/orders/` | cashier+ | Order history |
| GET | `/api/customers/:id/stats/` | cashier+ | Customer stats |
| POST | `/api/customers/search/` | cashier+ | Search by phone |

### Key Features
✅ Customer profiles  
✅ Membership tiers  
✅ Points system  
✅ Order history  
✅ Purchase analytics  
✅ Marketing consent  
✅ Preferred outlet

### Usage Example
```python
# Create customer
customer = Customer.objects.create(
    tenant=tenant,
    name='Jane Smith',
    phone='08123456789',
    email='jane@example.com',
    membership_tier='regular'
)

# Get stats
stats = {
    'total_orders': customer.total_orders,
    'total_spent': customer.total_spent,
    'average_order': customer.average_order_value
}
```

---

## 8. KITCHEN Module

**Location**: `backend/apps/kitchen/`  
**Purpose**: Kitchen display system integration

### Real-Time Features
- 🔔 Instant order notifications
- 📺 Kitchen display updates
- ✅ Order status synchronization
- ⏱️ Preparation time tracking

### Socket.IO Events

**Connection**: `http://localhost:3002`  
**Technology**: Socket.IO 4.6.1 with room-based broadcasting

#### Client → Server Events

| Event | Payload | Description |
|-------|---------|-------------|
| `subscribe_outlet` | `outletId: number` | Join outlet-specific room |
| `identify` | `{ type: 'pos'\|'kitchen', outletId }` | Identify client type |
| `new_order` | `Order object` | Broadcast new order to outlet |
| `update_status` | `{ id, order_number, outlet_id, status }` | Update order status |
| `complete_order` | `{ id, order_number, outlet_id }` | Mark order completed |
| `cancel_order` | `{ id, order_number, outlet_id }` | Cancel order |
| `broadcast` | `any` | Generic broadcast to outlet |

#### Server → Client Events

| Event | Payload | Description |
|-------|---------|-------------|
| `connected` | `{ message, socketId, timestamp }` | Connection established |
| `subscribed` | `{ outletId, timestamp }` | Successfully subscribed |
| `order_created` | `Order object` | New order received |
| `order_updated` | `{ id, status, timestamp }` | Order status changed |
| `order_completed` | `{ id, order_number }` | Order completed |
| `order_cancelled` | `{ id, order_number }` | Order cancelled |
| `order_sent` | `{ orderId, timestamp }` | Acknowledgment |
| `status_updated` | `{ orderId, timestamp }` | Acknowledgment |

### API Endpoints

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| GET | `/api/kitchen/orders/` | kitchen+ | Get pending orders |
| PATCH | `/api/kitchen/orders/:id/status/` | kitchen+ | Update status |
| POST | `/api/kitchen/orders/:id/ready/` | kitchen+ | Mark ready |

### Key Features
✅ Socket.IO real-time communication  
✅ Room-based broadcasting per outlet  
✅ Automatic reconnection  
✅ Transport fallback (WebSocket → Polling)  
✅ Order queue display  
✅ Priority ordering  
✅ Status updates with acknowledgment  
✅ Preparation timer  
✅ Multi-outlet isolation

### Usage Example
```javascript
// Kitchen display client
import io from 'socket.io-client';

const socket = io('http://localhost:3002', {
    transports: ['websocket', 'polling']
});

socket.on('connect', () => {
    // Subscribe to outlet
    socket.emit('subscribe_outlet', outlet_id);
    
    // Identify as kitchen
    socket.emit('identify', { 
        type: 'kitchen', 
        outletId: outlet_id 
    });
});

socket.on('subscribed', (data) => {
    console.log('Subscribed to outlet:', data.outletId);
});

socket.on('order_created', (order) => {
    displayOrder(order);
    playNotificationSound();
});

socket.on('order_updated', (update) => {
    updateOrderStatus(update);
});

socket.on('order_completed', (data) => {
    removeOrderFromDisplay(data.id);
});

// Update order status from kitchen
function updateStatus(orderId, status) {
    socket.emit('update_status', {
        id: orderId,
        order_number: 'ORD-001',
        outlet_id: outlet_id,
        status: status // 'preparing', 'ready', 'completed'
    });
}

// Complete order
function completeOrder(orderId, orderNumber) {
    socket.emit('complete_order', {
        id: orderId,
        order_number: orderNumber,
        outlet_id: outlet_id
    });
}
```

---

## 9. CORE Module

**Location**: `backend/apps/core/`  
**Purpose**: Base models, middleware, utilities

### Components
- **TenantModel**: Base class for tenant-specific models
- **TenantMiddleware**: Tenant context management
- **Permissions**: Custom permission classes
- **Managers**: TenantAwareManager, etc.

### Key Features
✅ Automatic tenant filtering  
✅ Context management  
✅ Permission utilities  
✅ Base model classes  
✅ Middleware stack

### Usage Example
```python
# Create tenant-aware model
class MyModel(TenantModel):
    name = models.CharField(max_length=200)
    # tenant field automatically added

# Queries auto-filtered by tenant
items = MyModel.objects.all()
# Only returns current tenant's items

# Admin bypass
all_items = MyModel.all_objects.all()
# Returns items from all tenants
```

---

## Module Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                    DEPENDENCY GRAPH                          │
└─────────────────────────────────────────────────────────────┘

                           CORE
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
     TENANTS              USERS              PRODUCTS
        │                    │                    │
        │                    │                    │
        └────────┬───────────┴──────┬─────────────┘
                 │                  │
               ORDERS ──────────────┤
                 │                  │
        ┌────────┼────────┐         │
        │        │        │         │
    PAYMENTS  KITCHEN  PROMOTIONS   │
                              │     │
                          CUSTOMERS │
                              │     │
                              └─────┘
```

---

## API Response Format

### Success Response
```json
{
  "id": 123,
  "name": "Product Name",
  "price": "95000.00",
  "created_at": "2026-01-04T12:00:00Z"
}
```

### List Response (Paginated)
```json
{
  "count": 100,
  "next": "http://api/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Product 1"
    }
  ]
}
```

### Error Response
```json
{
  "error": "ValidationError",
  "message": "Product price must be positive",
  "field": "price",
  "code": "INVALID_PRICE"
}
```

---

## Common Filters

### Query Parameters

| Parameter | Usage | Example |
|-----------|-------|---------|
| `tenant_id` | Filter by tenant | `?tenant_id=67` |
| `outlet_id` | Filter by outlet | `?outlet_id=45` |
| `search` | Text search | `?search=pizza` |
| `is_active` | Active items only | `?is_active=true` |
| `category` | Filter by category | `?category=5` |
| `page` | Pagination | `?page=2` |
| `page_size` | Items per page | `?page_size=20` |
| `ordering` | Sort field | `?ordering=-created_at` |

### Example
```
GET /api/products/?tenant_id=67&category=5&is_active=true&search=pizza&page=1&page_size=20
```

---

## Testing Endpoints

### Manual Testing with cURL
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Get products with auth
curl http://localhost:8000/api/products/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-Tenant-ID: 67"

# Create order
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "John Doe",
    "items": [
      {"product_id": 1, "quantity": 2}
    ]
  }'
```

---

## Frontend Integration

### API Client Example
```javascript
// lib/api/client.js
const API_BASE = 'http://localhost:8000/api';

async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    const tenantId = localStorage.getItem('tenant_id');
    
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            'X-Tenant-ID': tenantId,
            ...options.headers
        }
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'API Error');
    }
    
    return response.json();
}

// Usage
const products = await apiRequest('/products/');
const order = await apiRequest('/orders/', {
    method: 'POST',
    body: JSON.stringify({ customer_name: 'John' })
});
```

---

## Performance Considerations

### Caching Strategy
```python
# Cache product list (5 minutes)
from django.core.cache import cache

def get_products_cached(tenant_id):
    cache_key = f'products_tenant_{tenant_id}'
    products = cache.get(cache_key)
    
    if not products:
        products = list(Product.objects.filter(tenant_id=tenant_id))
        cache.set(cache_key, products, timeout=300)
    
    return products
```

### Batch Operations
```python
# Bulk create order items
OrderItem.objects.bulk_create([
    OrderItem(order=order, product=p, quantity=1)
    for p in products
])

# Bulk update status
Order.objects.filter(status='pending').update(status='confirmed')
```

---

## Security Best Practices

### 1. Always Validate Tenant Context
```python
@permission_classes([IsTenantUser])
def my_view(request):
    # request.tenant is validated by middleware
    items = MyModel.objects.all()  # Auto-filtered by tenant
```

### 2. Never Trust Client Input
```python
# ❌ Bad
tenant_id = request.data.get('tenant_id')
product.tenant_id = tenant_id

# ✅ Good
product.tenant = request.tenant
```

### 3. Use Permissions
```python
class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsTenantUser]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsOwnerOrManager()]
        return [IsTenantUser()]
```

---

**Last Updated**: January 4, 2026  
**API Version**: 2.0  
**Total Endpoints**: 80+
