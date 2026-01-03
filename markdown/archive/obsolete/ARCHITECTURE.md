# Architecture Documentation

## System Overview

Enterprise F&B POS System dengan arsitektur multi-tenant, offline-first, dan real-time order processing.

## Technology Stack

### Frontend
- **Framework**: SvelteKit (Svelte 4)
- **Styling**: TailwindCSS + DaisyUI
- **State Management**: Svelte Stores + IndexedDB
- **Offline Support**: Service Worker + Dexie.js
- **PWA**: Vite PWA Plugin

### Backend
- **Framework**: Django 4.2 + DRF
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Task Queue**: Celery
- **Authentication**: JWT (Simple JWT)

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **Payment Gateway**: Midtrans/Xendit/Stripe

## Multi-Tenant Architecture

### Strategy: Shared Database dengan Row-Level Isolation

```
┌─────────────────────────────────────────┐
│            Load Balancer                 │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
   ┌────▼────┐        ┌─────▼────┐
   │ Django  │        │  Django  │
   │ Server  │        │  Server  │
   │   #1    │        │    #2    │
   └────┬────┘        └─────┬────┘
        │                   │
        └────────┬──────────┘
                 │
        ┌────────▼─────────┐
        │   PostgreSQL     │
        │  (Multi-Tenant)  │
        └──────────────────┘
```

### Tenant Identification
1. **Subdomain**: tenant1.pos.com, tenant2.pos.com
2. **Header**: X-Tenant-ID
3. **Token**: JWT contains tenant_id claim

### Data Isolation
```python
# Middleware automatically filters queries
class TenantMiddleware:
    def __call__(self, request):
        tenant = self.get_tenant(request)
        set_current_tenant(tenant)
```

All models inherit from:
```python
class TenantAwareModel(models.Model):
    tenant = models.ForeignKey(Tenant)
    
    class Meta:
        abstract = True
```

## Offline-First Architecture

### IndexedDB Schema
```javascript
POSDatabase
├── products (id, sku, name, category_id, price, sync_status)
├── categories (id, name, outlet_id, sort_order)
├── cart (id, product_id, quantity, modifiers)
├── orders (id, order_number, total, sync_status)
├── payments (id, order_id, method, amount, sync_status)
└── sync_queue (id, entity_type, action, data, retry_count)
```

### Sync Strategy
```
┌──────────────┐
│   Browser    │
│  (Offline)   │
└──────┬───────┘
       │
       │ 1. Create Order
       ▼
┌──────────────┐
│  IndexedDB   │ ◄── Store locally
└──────┬───────┘
       │
       │ 2. Add to Sync Queue
       ▼
┌──────────────┐
│  Sync Queue  │
└──────┬───────┘
       │
       │ 3. When Online
       ▼
┌──────────────┐
│ Backend API  │ ◄── Sync in background
└──────────────┘
```

### Conflict Resolution
- **Last-Write-Wins** for product updates
- **Server-Authority** for pricing and inventory
- **Merge Strategy** for cart items

## API Design

### RESTful Endpoints

#### Products
```
GET    /api/products/          - List products
GET    /api/products/:id/      - Get product
POST   /api/products/          - Create product (admin)
PATCH  /api/products/:id/      - Update product (admin)
DELETE /api/products/:id/      - Delete product (admin)
GET    /api/products/sync/     - Sync products for offline
```

#### Orders
```
POST   /api/orders/            - Create order
GET    /api/orders/:id/        - Get order detail
PATCH  /api/orders/:id/status/ - Update order status
GET    /api/orders/history/    - Order history
POST   /api/orders/hold/       - Hold order
POST   /api/orders/recall/:id/ - Recall held order
```

#### Payments
```
POST   /api/payments/qris/generate/     - Generate QRIS
POST   /api/payments/qris/check/:id/    - Check QRIS status
POST   /api/payments/callback/          - Payment webhook
GET    /api/payments/:id/status/        - Payment status
```

### WebSocket Channels

```
ws://api.pos.com/ws/kitchen/{outlet_id}/     - Kitchen updates
ws://api.pos.com/ws/orders/{outlet_id}/      - Order updates
ws://api.pos.com/ws/payments/{order_id}/     - Payment status
```

## Kiosk Mode UI Architecture

### Design Principles
1. **Touch-First**: Minimum 64x64px touch targets
2. **High Contrast**: Readable in bright environments
3. **Fullscreen**: No browser chrome
4. **Instant Feedback**: Optimistic UI updates
5. **Offline-Ready**: Works without internet

### Component Structure
```
src/routes/kiosk/
├── +page.svelte              (Main POS interface)
├── payment/
│   └── +page.svelte          (Payment selection)
├── receipt/
│   └── +page.svelte          (Order receipt)
└── components/
    ├── ProductGrid.svelte
    ├── CartPanel.svelte
    ├── CategoryFilter.svelte
    └── OfflineIndicator.svelte
```

### State Management
```javascript
// Svelte Stores
- cartItems (writable)
- cartTotals (derived)
- isOnline (writable)
- selectedCategory (writable)

// IndexedDB
- Products cache
- Orders queue
- Sync status
```

## Payment Integration

### QRIS Flow (Midtrans/Xendit)
```
1. User selects QRIS payment
   ↓
2. Backend generates dynamic QRIS code
   ↓
3. Display QR code to user
   ↓
4. Poll payment status every 3s
   ↓
5. Webhook confirms payment
   ↓
6. Update order status → PAID
```

### Implementation
```javascript
// Frontend
async function generateQRIS(orderId, amount) {
  const response = await api.post('/payments/qris/generate/', {
    order_id: orderId,
    amount: amount
  });
  
  // Display QR code
  displayQRCode(response.qr_string);
  
  // Start polling
  startPaymentPolling(response.transaction_id);
}

// Backend (Django)
from midtransclient import Snap

def generate_qris(order):
    snap = Snap(server_key=settings.MIDTRANS_SERVER_KEY)
    params = {
        'transaction_details': {
            'order_id': order.order_number,
            'gross_amount': int(order.total)
        },
        'enabled_payments': ['gopay', 'shopeepay', 'qris']
    }
    transaction = snap.create_transaction(params)
    return transaction
```

## Security

### Authentication Flow
```
1. Login → JWT Access Token (15 min) + Refresh Token (7 days)
2. Store tokens in httpOnly cookies (web) or secure storage (mobile)
3. Access token in Authorization header: Bearer <token>
4. Auto-refresh when access token expires
```

### Authorization
```python
# Role-based permissions
ROLES = {
    'owner': ['*'],  # All permissions
    'admin': ['manage_products', 'view_reports', 'manage_users'],
    'cashier': ['create_order', 'process_payment'],
    'kitchen': ['view_orders', 'update_order_status']
}
```

### Payment Security
- No card data stored locally
- PCI DSS compliant payment gateway
- Webhook signature verification
- SSL/TLS encryption
- Rate limiting on payment endpoints

## Scalability

### Horizontal Scaling
```
┌─────────────┐
│   Nginx     │ Load Balancer
└──────┬──────┘
       │
   ┌───┴────┐
   │        │
┌──▼──┐  ┌──▼──┐
│Django│  │Django│  Stateless API Servers
│  #1  │  │  #2  │
└──┬───┘  └──┬───┘
   │         │
   └────┬────┘
        │
┌───────▼────────┐
│   PostgreSQL   │
│  (Primary)     │
└───────┬────────┘
        │
   ┌────┴────┐
   │         │
┌──▼──┐   ┌──▼──┐
│Read │   │Read │  Read Replicas
│  #1 │   │  #2 │
└─────┘   └─────┘
```

### Caching Strategy
```
L1: Browser Cache (Service Worker)
L2: Redis Cache (Menu data, 5 min TTL)
L3: Database Query Cache
L4: CDN (Static assets)
```

### Database Optimization
- **Indexes**: All foreign keys, search fields
- **Partitioning**: Orders by date (monthly partitions)
- **Connection Pooling**: pgBouncer
- **Query Optimization**: select_related, prefetch_related

## Monitoring & Observability

### Metrics to Track
- API response time (p50, p95, p99)
- Order processing time
- Payment success rate
- Sync queue length
- Database connection pool usage
- Cache hit rate

### Alerting
- Payment webhook failures
- Sync queue backlog > 1000
- API error rate > 5%
- Database connections > 80%

### Logging
```python
# Structured logging
logger.info('order_created', extra={
    'order_id': order.id,
    'tenant_id': order.tenant_id,
    'outlet_id': order.outlet_id,
    'total': order.total,
    'payment_method': order.payment_method
})
```

## Deployment

### Development
```bash
docker-compose up -d
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
# + SSL certificates (Let's Encrypt)
# + Environment variables from secrets
# + Database backups (daily)
# + Monitoring (Sentry, Prometheus)
```

## Future Enhancements

1. **Real-time Kitchen Display** - WebSocket-based KDS
2. **Advanced Analytics** - Business intelligence dashboard
3. **Loyalty Program** - Customer rewards integration
4. **Inventory Management** - Stock tracking and alerts
5. **Multi-currency** - Support for multiple currencies
6. **Voice Orders** - Speech-to-text for order entry
7. **AI Recommendations** - Smart product recommendations
