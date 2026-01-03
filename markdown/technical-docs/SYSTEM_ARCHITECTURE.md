# 🏗️ System Architecture - Enterprise F&B POS System

## Table of Contents
- [Overview](#overview)
- [High-Level Architecture](#high-level-architecture)
- [Tech Stack](#tech-stack)
- [Service Architecture](#service-architecture)
- [Design Patterns](#design-patterns)
- [Network Topology](#network-topology)
- [Data Flow](#data-flow)

---

## Overview

Sistem POS F&B ini adalah aplikasi enterprise yang didesain untuk menangani operasi multi-tenant (multi-brand) dengan multiple outlets. Sistem ini menggunakan **microservices-inspired monolithic architecture** yang di-containerize dengan Docker.

### Karakteristik Utama

- **Multi-Tenant**: Satu instance aplikasi melayani multiple brands/tenants
- **Multi-Outlet**: Setiap tenant dapat memiliki multiple outlets/stores
- **Offline-First**: Frontend dapat bekerja tanpa koneksi internet
- **Real-Time**: Kitchen display & order updates secara real-time
- **Scalable**: Dapat di-scale horizontal dengan load balancer
- **Secure**: JWT authentication, RBAC, dan data isolation

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Kiosk POS  │  │  Kitchen KDS │  │ Admin Panel  │          │
│  │   (Svelte)   │  │   (Svelte)   │  │   (Svelte)   │          │
│  │  + IndexedDB │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                  │                  │                  │
└─────────┼──────────────────┼──────────────────┼──────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                    ┌────────▼────────┐
                    │   NGINX Proxy   │
                    │   (Port 80/443) │
                    └────────┬────────┘
                             │
          ┌──────────────────┴──────────────────┐
          │                                      │
    ┌─────▼─────┐                    ┌──────────▼──────────┐
    │  Backend  │                    │    Frontend         │
    │  (Django) │                    │   (SvelteKit SSR)   │
    │   :8000   │                    │      :5173          │
    └─────┬─────┘                    └─────────────────────┘
          │
    ┌─────┴─────────────────────┐
    │                            │
┌───▼────┐     ┌────────┐   ┌───▼──┐
│  DB    │     │ Redis  │   │Celery│
│Postgres│     │ Cache  │   │Worker│
│ :5432  │     │ :6379  │   │      │
└────────┘     └────────┘   └──────┘
```

### Component Responsibilities

| Component | Tanggung Jawab | Port |
|-----------|---------------|------|
| **Nginx** | Reverse proxy, SSL termination, load balancing | 80, 443 |
| **Frontend (SvelteKit)** | UI rendering, routing, offline storage | 5173 |
| **Backend (Django)** | Business logic, API, authentication | 8000 |
| **PostgreSQL** | Primary data store | 5432 |
| **Redis** | Cache, session, Celery broker | 6379 |
| **Celery Worker** | Async tasks (email, reports, sync) | - |
| **Celery Beat** | Scheduled tasks (cron jobs) | - |

---

## Tech Stack

### Backend Stack

```python
Framework:    Django 4.2.x
API:          Django REST Framework 3.14.x
Auth:         djangorestframework-simplejwt
Database:     PostgreSQL 15
Cache:        Redis 7
Task Queue:   Celery 5.x
WSGI Server:  Gunicorn
```

**Justifikasi:**
- **Django**: Mature, secure, ORM yang powerful, admin interface built-in
- **DRF**: Industry standard untuk REST API, serialization yang robust
- **JWT**: Stateless authentication, scalable untuk distributed systems
- **PostgreSQL**: ACID compliant, JSON support, full-text search
- **Redis**: High performance cache, pub/sub untuk real-time
- **Celery**: Reliable task queue, scheduling, retry mechanism

### Frontend Stack

```javascript
Framework:     SvelteKit 1.x
Language:      JavaScript/TypeScript
UI:            TailwindCSS + DaisyUI
State:         Svelte Stores
Offline:       IndexedDB (Dexie.js)
PWA:           Vite PWA Plugin
HTTP Client:   Fetch API + Retry logic
```

**Justifikasi:**
- **SvelteKit**: Fast, reactive, SSR support, minimal bundle size
- **TailwindCSS**: Utility-first, rapid prototyping, consistent design
- **IndexedDB**: Persistent offline storage, async, large capacity
- **Stores**: Simple, reactive state management tanpa boilerplate
- **PWA**: Installable, offline capable, native-like experience

### Infrastructure

```yaml
Containerization:  Docker + Docker Compose
Reverse Proxy:     Nginx 1.25
CI/CD:             GitHub Actions
Monitoring:        (Planned: Sentry, Prometheus)
Logging:           Docker logs + ELK stack (optional)
```

---

## Service Architecture

### Docker Compose Services

```yaml
services:
  db:          # PostgreSQL database
  redis:       # Cache & message broker
  backend:     # Django API server
  celery_worker:   # Background task processor
  celery_beat:     # Scheduled task scheduler
  frontend:    # SvelteKit SSR (optional, bisa static)
  nginx:       # Reverse proxy
```

### Service Dependencies

```
nginx
  ├── backend (depends on: db, redis)
  │     ├── celery_worker (depends on: backend, redis)
  │     └── celery_beat (depends on: backend, redis)
  └── frontend (optional for SSR)
```

### Health Checks

Setiap service memiliki health check:

```yaml
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/api/health/"]
    interval: 30s
    timeout: 10s
    retries: 3

db:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U pos_user"]
    interval: 10s
    timeout: 5s
    retries: 5
```

---

## Design Patterns

### 1. Repository Pattern

**Backend**: Menggunakan Django ORM sebagai repository layer.

```python
# apps/products/repositories.py
class ProductRepository:
    @staticmethod
    def get_active_products(tenant_id):
        return Product.objects.filter(
            tenant_id=tenant_id,
            is_active=True
        )
```

### 2. Service Layer Pattern

**Backend**: Business logic di service layer, bukan di views.

```python
# apps/orders/services.py
class OrderService:
    def create_order(self, cart_items, customer_info):
        # Business logic here
        # Calculate totals, apply discounts, etc.
        pass
```

### 3. Store Pattern (State Management)

**Frontend**: Centralized state dengan Svelte stores.

```javascript
// src/lib/stores/cart.js
export const cartStore = writable({
  items: [],
  total: 0
});
```

### 4. Middleware Chain

**Backend**: Request processing pipeline.

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'apps.tenants.middleware.TenantMiddleware',  # Extract tenant
    'apps.core.middleware.SetTenantContextMiddleware',
    'apps.core.middleware.SetOutletContextMiddleware',
]
```

### 5. Strategy Pattern

**Backend**: Payment processing dengan multiple gateways.

```python
class PaymentStrategy:
    def process_payment(self, amount): pass

class MidtransPayment(PaymentStrategy):
    def process_payment(self, amount):
        # Midtrans specific logic
        pass

class XenditPayment(PaymentStrategy):
    def process_payment(self, amount):
        # Xendit specific logic
        pass
```

### 6. Observer Pattern

**Frontend**: Reactive updates dengan Svelte stores.

```javascript
// Ketika cart berubah, UI otomatis update
$: totalItems = $cartStore.items.length;
```

### 7. Factory Pattern

**Backend**: Dynamic object creation (serializers, validators).

```python
class SerializerFactory:
    @staticmethod
    def get_serializer(model_type):
        if model_type == 'product':
            return ProductSerializer
        elif model_type == 'order':
            return OrderSerializer
```

---

## Network Topology

### Production Setup

```
Internet
    │
    ▼
┌─────────────────┐
│   Load Balancer │
│   (CloudFlare)  │
└────────┬────────┘
         │
    ┌────┴────┐
    │  Nginx  │
    │ :80/443 │
    └────┬────┘
         │
    ┌────┴──────────────┐
    │                   │
┌───▼────┐      ┌───────▼──────┐
│Backend │      │  Frontend    │
│Cluster │      │  Static CDN  │
│(Multi) │      │              │
└───┬────┘      └──────────────┘
    │
┌───┴─────┐
│   DB    │
│(Primary)│
└───┬─────┘
    │
┌───┴─────┐
│DB Replica│
│(Standby)│
└─────────┘
```

### Development Setup

```
localhost:80 (Nginx)
    ├── localhost:8001 → Backend (Django)
    ├── localhost:5173 → Frontend (Vite dev)
    ├── localhost:5433 → PostgreSQL
    └── localhost:6380 → Redis
```

---

## Data Flow

### 1. Order Creation Flow

```
┌──────┐   1. Add to Cart    ┌─────────┐
│Client│─────────────────────▶│Frontend │
└──────┘                      │  Store  │
                              └────┬────┘
                                   │ 2. IndexedDB
                                   │    (Offline save)
                                   ▼
                              ┌─────────┐
                              │IndexedDB│
                              └─────────┘
                                   │
                      3. Sync when online
                                   │
                                   ▼
┌──────┐   4. POST /api/orders    ┌────────┐
│Client│──────────────────────────▶│Backend │
└──────┘                           └────┬───┘
                                        │
                    5. Validate & Process
                                        │
                            ┌───────────┴────────┐
                            │                    │
                       ┌────▼─────┐      ┌──────▼────┐
                       │PostgreSQL│      │  Celery   │
                       │  (Save)  │      │(Async Job)│
                       └──────────┘      └───────────┘
                                              │
                                    6. Kitchen notification
                                              │
                                              ▼
                                        ┌──────────┐
                                        │  Kitchen │
                                        │   KDS    │
                                        └──────────┘
```

### 2. Authentication Flow

```
┌──────┐  1. Login Request     ┌────────┐
│Client│──────────────────────▶│Backend │
└──────┘  (username/password)  └────┬───┘
                                    │
                        2. Validate credentials
                                    │
                               ┌────▼────┐
                               │   DB    │
                               │  Users  │
                               └────┬────┘
                                    │
                        3. Generate JWT tokens
                                    │
┌──────┐  4. Return tokens     ┌───┴────┐
│Client│◀──────────────────────│Backend │
└──┬───┘  (access + refresh)   └────────┘
   │
   │ 5. Store in localStorage
   │
   ▼
┌────────────┐
│LocalStorage│
└────────────┘
   │
   │ 6. Include in headers
   │    Authorization: Bearer <token>
   │
   ▼
┌────────────┐
│API Requests│
└────────────┘
```

### 3. Multi-Tenant Request Flow

```
┌──────┐  X-Tenant-ID: 123    ┌────────┐
│Client│──────────────────────▶│ Nginx  │
└──────┘  X-Outlet-ID: 456     └────┬───┘
                                    │
                        Route to backend
                                    │
                               ┌────▼────┐
                               │TenantMw │ Middleware
                               └────┬────┘
                                    │
                      Extract & validate tenant
                                    │
                               ┌────▼────┐
                               │ Context │ Thread-local
                               │  Store  │
                               └────┬────┘
                                    │
                        Set tenant context
                                    │
                               ┌────▼────┐
                               │  Views  │
                               └────┬────┘
                                    │
                      Query with tenant filter
                                    │
                               ┌────▼────┐
                               │   ORM   │
                               │ Query   │
                               └────┬────┘
                                    │
                               ┌────▼────┐
                               │   DB    │
                               │ (WHERE  │
                               │tenant_id│
                               │  = 123) │
                               └─────────┘
```

---

## Scalability Considerations

### Horizontal Scaling

```
Load Balancer
    ├── Backend Instance 1 ─┐
    ├── Backend Instance 2 ─┼─▶ PostgreSQL (Primary)
    └── Backend Instance 3 ─┘   └─▶ Read Replicas
              │
              └─▶ Redis Cluster
```

### Caching Strategy

1. **Application Cache**: Redis untuk query results
2. **Browser Cache**: Static assets di CDN
3. **Database Cache**: PostgreSQL query cache
4. **Object Cache**: Django's cache framework

### Performance Targets

- **API Response Time**: < 200ms (P95)
- **Page Load Time**: < 2s (First Contentful Paint)
- **Offline Support**: Full functionality tanpa internet
- **Concurrent Users**: 1000+ per instance
- **Transaction Rate**: 100+ orders/minute

---

## Security Architecture

### Defense in Depth

```
Layer 1: Network
  ├── CloudFlare DDoS protection
  ├── Nginx rate limiting
  └── IP whitelisting (admin)

Layer 2: Application
  ├── JWT authentication
  ├── RBAC authorization
  ├── Input validation & sanitization
  └── SQL injection prevention (ORM)

Layer 3: Data
  ├── Encryption at rest (DB)
  ├── Encryption in transit (SSL/TLS)
  ├── Data isolation per tenant
  └── Audit logging
```

### Authentication Layers

1. **Public API**: No auth (product browsing)
2. **Kiosk API**: JWT token (customer orders)
3. **Staff API**: JWT + RBAC (cashier, kitchen)
4. **Admin API**: JWT + RBAC + Admin role

---

## Monitoring & Observability

### Metrics to Track

```yaml
Application Metrics:
  - Request rate (req/sec)
  - Response time (latency)
  - Error rate (%)
  - Active users

Business Metrics:
  - Orders per hour
  - Average order value
  - Payment success rate
  - Kitchen processing time

Infrastructure Metrics:
  - CPU usage
  - Memory usage
  - Disk I/O
  - Network bandwidth
```

### Logging Strategy

```python
# Structured logging
logger.info('order_created', extra={
    'order_id': order.id,
    'tenant_id': tenant.id,
    'outlet_id': outlet.id,
    'total': order.total,
    'items_count': order.items.count()
})
```

---

## Next Steps

Setelah memahami arsitektur sistem, lanjutkan ke:

1. **[BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md)** - Detail implementasi backend
2. **[FRONTEND_ARCHITECTURE.md](FRONTEND_ARCHITECTURE.md)** - Detail implementasi frontend
3. **[MULTI_TENANT_DEEP_DIVE.md](MULTI_TENANT_DEEP_DIVE.md)** - Deep dive multi-tenant

---

**Last Updated**: January 3, 2026
