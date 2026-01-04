# 00 - APPLICATION OVERVIEW

## What is Kiosk POS?

**Kiosk POS** adalah sistem Point of Sale (POS) modern untuk Food & Beverage (F&B) industry dengan fokus pada **Multi-Tenant Architecture** dan **Role-Based Access Control (RBAC)**. Sistem ini dirancang untuk mendukung multiple brands/franchises dengan outlet yang berbeda-beda, sambil menjaga isolasi data yang ketat antar tenant.

### Tagline
> "Multi-Tenant F&B POS System with Smart RBAC & Kitchen Integration"

---

## Core Problem Solved

### Business Challenges
1. **Multi-Brand Management**: Satu sistem untuk mengelola multiple restoran/franchise
2. **Outlet Scalability**: Setiap brand bisa punya banyak outlet dengan data terpisah
3. **Role Management**: Berbagai level user dengan permission berbeda
4. **Kitchen Operations**: Integrasi real-time order dengan kitchen display system
5. **Data Security**: Isolasi data ketat antar tenant untuk privacy & security
6. **Promotion Engine**: Flexible promotion system untuk berbagai jenis diskon

### Technical Challenges
1. Data isolation per tenant
2. Cross-tenant admin access (super admin)
3. Real-time synchronization
4. Performance dengan banyak tenant
5. Scalable architecture

---

## Main Objectives

### 1. Multi-Tenancy
- ✅ Multiple tenants (brands/franchises) dalam satu aplikasi
- ✅ Data isolation: Setiap tenant tidak bisa akses data tenant lain
- ✅ Centralized management untuk super admin
- ✅ Tenant-specific branding (logo, colors)

### 2. Multi-Outlet Support
- ✅ Setiap tenant bisa punya multiple outlets
- ✅ Outlet-specific inventory & operations
- ✅ Cross-outlet reporting untuk owner
- ✅ Per-outlet user assignment

### 3. Role-Based Access Control (RBAC)
- ✅ 6 tipe role: Super Admin, Admin, Tenant Owner, Manager, Cashier, Kitchen Staff
- ✅ Granular permissions per role
- ✅ Tenant-bound permissions
- ✅ Outlet-bound permissions

### 4. Kitchen Integration
- ✅ Real-time order synchronization ke kitchen
- ✅ Kitchen Display System (KDS)
- ✅ Order status tracking
- ✅ WebSocket-based communication

### 5. Promotion Engine
- ✅ 4 tipe promosi: Percentage, Fixed Amount, Buy X Get Y, Bundle Deal
- ✅ Product-specific promotions
- ✅ Time-based activation
- ✅ Tenant-specific promotions

---

## Target Users

### 1. Super Admin
**Who**: System administrator
**Access**: All tenants & outlets
**Use Cases**:
- Manage all tenants
- Create new tenants/outlets
- System configuration
- Monitor all activities

### 2. Tenant Owner
**Who**: Franchise/Restaurant owner
**Access**: All outlets within their tenant
**Use Cases**:
- Manage outlets
- View all outlet reports
- Manage managers & staff
- Configure products & promotions

### 3. Manager
**Who**: Store/Outlet manager
**Access**: Assigned outlet(s)
**Use Cases**:
- Manage outlet operations
- Manage cashiers & kitchen staff
- Configure products for outlet
- View outlet reports

### 4. Cashier
**Who**: Front-line staff
**Access**: Assigned outlet (cashier terminal)
**Use Cases**:
- Process orders
- Handle payments
- Print receipts
- Basic customer service

### 5. Kitchen Staff
**Who**: Kitchen personnel
**Access**: Kitchen Display System
**Use Cases**:
- View incoming orders
- Update order status
- Mark items complete
- Communicate with cashier

---

## Key Capabilities

### For Customers (End Users)
- 🛒 Self-service ordering via kiosk
- 📱 Product browsing with images
- 💰 Multiple payment methods
- 🎁 Automatic promotion application
- 🧾 Digital receipt

### For Cashiers
- ⚡ Fast order processing
- 🔍 Product search & filtering
- 💳 Multi-payment handling (cash, card, QRIS)
- 📊 Real-time order tracking
- 🎯 Quick access interface

### For Kitchen
- 📺 Kitchen Display System (KDS)
- 🔔 Real-time order notifications
- ✅ Order status management
- 📝 Order details & special requests
- 🎨 Color-coded priority

### For Managers
- 📊 Sales reports & analytics
- 📦 Product management
- 👥 Staff management
- 🎁 Promotion configuration
- 🏪 Outlet configuration

### For Owners
- 🏢 Multi-outlet dashboard
- 📈 Consolidated reporting
- 👨‍💼 Cross-outlet staff management
- 💼 Business insights
- ⚙️ System-wide configuration

### For Super Admins
- 🌐 Multi-tenant management
- 🔧 System configuration
- 👁️ Global monitoring
- 🔐 Security management
- 📊 Platform analytics

---

## System Characteristics

### Performance
- ⚡ Fast order processing (<2 seconds)
- 🔄 Real-time kitchen updates (WebSocket)
- 📱 Responsive UI (desktop & mobile)
- 💾 Efficient database queries
- 🚀 Optimized for high-traffic

### Reliability
- 🛡️ Data isolation per tenant
- 💪 Robust error handling
- 🔒 Secure authentication
- 📝 Audit logging
- ♻️ Automatic recovery

### Scalability
- 📈 Horizontal scaling ready
- 🏗️ Modular architecture
- 🐳 Docker containerization
- 🌍 Multi-region capable
- 📊 Database optimization

### Security
- 🔐 JWT authentication
- 🎫 Token-based sessions
- 🔒 HTTPS/WSS encryption
- 👤 Role-based permissions
- 🛡️ Tenant data isolation

---

## Business Model

### Deployment Options

#### 1. SaaS Model (Recommended)
- One instance, multiple tenants
- Subscription per tenant/outlet
- Centralized updates
- Lower maintenance cost

#### 2. On-Premise
- Dedicated installation per client
- One-time license
- Client-managed infrastructure
- Higher control

#### 3. Hybrid (Current Implementation)
- Cloud backend (Django REST API)
- Local kiosk terminals (SvelteKit PWA)
- **Offline-First Architecture**: Full POS functionality without internet
- IndexedDB for local data persistence
- Background sync when online
- Best of both worlds:
  - ✅ **Zero downtime**: Works offline 100%
  - ✅ **Real-time sync**: Data syncs automatically when online
  - ✅ **Low latency**: Instant UI response from IndexedDB
  - ✅ **Data safety**: Persistent local storage, auto-retry sync
  - ✅ **Better UX**: No "waiting for server" delays

**Offline Capabilities**:
- Product catalog (synced from server)
- Cart management (IndexedDB)
- Order creation (queued for sync)
- Payment processing (saved locally, synced later)
- Kitchen display (works with cached orders)

**Sync Strategy**:
```
┌──────────────┐
│  POS Action  │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  Save to         │
│  IndexedDB       │  ◄── Instant (5-10ms)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Sync Queue      │
└──────┬───────────┘
       │
       ▼ (when online)
┌──────────────────┐
│  POST to API     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Mark Synced     │
└──────────────────┘
```

---

## System Boundaries

### In Scope ✅
- Multi-tenant POS operations
- Order management
- Kitchen display integration
- Product catalog management
- Promotion engine
- Customer management
- Basic reporting
- User & role management
- Multi-outlet support

### Out of Scope ❌
- Accounting integration (planned)
- Inventory management (basic only)
- HR/Payroll system
- Loyalty program (planned)
- Mobile ordering app
- Delivery integration
- Advanced BI/Analytics

---

## Success Metrics

### Technical Metrics
- 🎯 Order processing time: <2s
- 🔄 Kitchen sync latency: <500ms
- 💪 System uptime: >99.9%
- 📊 API response time: <200ms
- 🐛 Critical bugs: <1 per month

### Business Metrics
- 👥 Tenants onboarded: Growth tracking
- 🏪 Outlets activated: Per tenant
- 📈 Orders processed: Daily/monthly
- 💰 Revenue per tenant: Tracking
- 😊 User satisfaction: Feedback

---

## Unique Selling Points (USP)

### 1. True Multi-Tenancy
Unlike traditional POS systems yang single-tenant, sistem ini dirancang dari ground-up untuk multi-tenancy dengan:
- Complete data isolation
- Tenant-specific customization
- Centralized management
- Cost efficiency

### 2. Smart RBAC
Sistem permission yang sophisticated:
- Tenant-level isolation
- Outlet-level isolation
- Cross-outlet access untuk managers
- Flexible role assignment

### 3. Real-Time Kitchen Integration
- WebSocket-based instant updates
- No polling, no delay
- Reliable order flow
- Kitchen staff efficiency

### 4. Flexible Promotion Engine
- 4 tipe promosi berbeda
- Product role differentiation (Buy X Get Y)
- Time-based activation
- Easy configuration

### 5. Modern Tech Stack
- SvelteKit untuk fast, reactive UI
- Django untuk robust backend
- Docker untuk easy deployment
- PostgreSQL untuk reliability

---

## User Journey Examples

### Journey 1: Super Admin Onboards New Tenant
1. Login as super admin
2. Create new tenant "Pizza Hut"
3. Configure tenant (logo, colors, tax rate)
4. Create first outlet "Pizza Hut Mall Yogya"
5. Create tenant owner user
6. Tenant owner receives credentials
7. Tenant owner configures products

### Journey 2: Customer Orders at Kiosk
1. Customer approaches kiosk
2. Browse products by category
3. Select "Pepperoni Pizza" + "Coca Cola"
4. System applies "Buy 1 Get 1 Drink" promotion
5. Review cart, proceed to payment
6. Pay with QRIS
7. Order sent to kitchen instantly
8. Receive order number
9. Kitchen marks order complete
10. Customer picks up order

### Journey 3: Manager Creates Promotion
1. Login as manager
2. Navigate to Promotions
3. Click "Create Promotion"
4. Select type "Buy X Get Y"
5. Configure: Buy 2 Pizza, Get 1 Burger
6. Set date range (weekend only)
7. Assign products with roles
8. Activate promotion
9. Promotion appears at cashier
10. Promotion auto-applied to eligible orders

---

## Architecture Philosophy

### Design Principles
1. **Separation of Concerns**: Clear module boundaries
2. **DRY (Don't Repeat Yourself)**: Reusable components
3. **Security First**: Tenant isolation by design
4. **API First**: RESTful API for all operations
5. **Real-Time Ready**: WebSocket for live updates
6. **Scalable by Default**: Horizontal scaling support

### Data Philosophy
1. **Tenant Isolation**: Absolute data privacy
2. **Audit Trail**: All changes tracked
3. **Soft Deletes**: No permanent data loss
4. **Referential Integrity**: Foreign key constraints
5. **Optimistic Locking**: Concurrent update handling

---

## Technology Choices Rationale

### Why Django?
- ✅ Mature ORM with excellent multi-tenancy support
- ✅ Built-in admin interface
- ✅ Strong security features
- ✅ Large ecosystem
- ✅ Easy to extend

### Why SvelteKit?
- ✅ Minimal JavaScript bundle
- ✅ Fast performance
- ✅ Reactive by default
- ✅ Server-side rendering
- ✅ Modern developer experience

### Why PostgreSQL?
- ✅ ACID compliance
- ✅ JSON support
- ✅ Excellent performance
- ✅ Row-level security
- ✅ Rich indexing options

### Why Docker?
- ✅ Consistent environments
- ✅ Easy deployment
- ✅ Microservices ready
- ✅ CI/CD friendly
- ✅ Resource isolation

---

## Future Roadmap

### Phase 1: MVP (Current) ✅
- [x] Basic POS operations
- [x] Multi-tenant support
- [x] RBAC implementation
- [x] Kitchen integration
- [x] Promotion engine

### Phase 2: Enhanced Features (Q1 2026)
- [ ] Advanced reporting & analytics
- [ ] Loyalty program
- [ ] Mobile app for customers
- [ ] Inventory management
- [ ] Accounting integration

### Phase 3: Scale & Optimize (Q2 2026)
- [ ] Performance optimization
- [ ] Multi-region deployment
- [ ] Advanced caching
- [ ] Message queue integration
- [ ] Load balancing

### Phase 4: Enterprise (Q3 2026)
- [ ] White-label solution
- [ ] Advanced customization
- [ ] API marketplace
- [ ] Third-party integrations
- [ ] Enterprise SLA

---

## Getting Started

For developers new to this project:

1. **Read this overview** to understand the big picture
2. **Study [01-ARCHITECTURE.md](./01-ARCHITECTURE.md)** for system design
3. **Review [03-RBAC-MULTI-TENANT.md](./03-RBAC-MULTI-TENANT.md)** for core concepts
4. **Check [05-MODULES.md](./05-MODULES.md)** for feature details
5. **Setup development environment** (see main README.md)

---

## Quick Facts

| Aspect | Detail |
|--------|--------|
| **Type** | Multi-Tenant POS System |
| **Domain** | Food & Beverage |
| **Architecture** | Microservices-ready Monolith |
| **Frontend** | SvelteKit |
| **Backend** | Django REST Framework |
| **Database** | PostgreSQL |
| **Real-time** | Socket.IO (Kitchen Sync Server) |
| **Deployment** | Docker Compose |
| **License** | Proprietary |

---

**Last Updated**: January 4, 2026  
**Version**: 2.0  
**Status**: Production-Ready MVP  
**Next Review**: Q1 2026
