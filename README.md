# 🍽️ Enterprise F&B POS System

Sistem Point of Sale (POS) enterprise-grade untuk Food & Beverage dengan fitur multi-tenant, offline-first, dan integrasi payment gateway.

## 🎯 Features

### Core POS
- ✅ Multi-tenant architecture (shared database + tenant isolation)
- ✅ Multiple outlets per tenant
- ✅ Role-based access control (Owner, Admin, Cashier, Kitchen)
- ✅ Product & menu management dengan modifier
- ✅ Dynamic pricing per outlet
- ✅ Tax & service charge calculation
- ✅ Promo & discount engine
- ✅ Split bill & merge bill
- ✅ Hold & recall orders
- ✅ Offline-first dengan auto sync

### Platform
- 🖥️ **Web POS** - Desktop browser
- 📱 **Mobile POS** - Progressive Web App (PWA)
- 🖥️ **Kiosk POS** - Fullscreen, touch-optimized, offline-first

### Payment Integration
- 💳 QRIS (Static & Dynamic)
- 💳 Debit/Credit Card
- 💵 Cash
- 💰 E-Wallet (Midtrans/Xendit/Stripe)
- 🔄 Split & partial payment
- 📊 Payment reconciliation

### Kitchen Operations
- 📋 Kitchen Display System (KDS)
- 🔄 Order flow: New → Cooking → Ready → Served
- 🖨️ Auto print / digital receipt
- ⏱️ Real-time order updates

## 🏗️ Tech Stack

### Frontend
- **Framework**: SvelteKit (Svelte 4)
- **Styling**: TailwindCSS + DaisyUI
- **State**: Svelte stores + IndexedDB
- **PWA**: Vite PWA plugin
- **Offline**: Service Worker + IndexedDB

### Backend
- **Framework**: Django 4.2 + Django REST Framework
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Authentication**: JWT (djangorestframework-simplejwt)

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **Payment Gateway**: Midtrans/Xendit SDK

## 📁 Project Structure

```
/home/user/webapp/
├── backend/                 # Django Backend
│   ├── config/             # Django settings
│   ├── apps/
│   │   ├── tenants/        # Multi-tenant management
│   │   ├── products/       # Product & menu
│   │   ├── orders/         # Order management
│   │   ├── payments/       # Payment processing
│   │   ├── kitchen/        # Kitchen operations
│   │   └── users/          # User & authentication
│   ├── requirements.txt
│   └── manage.py
├── frontend/               # SvelteKit Frontend
│   ├── src/
│   │   ├── routes/
│   │   │   ├── kiosk/     # Kiosk Mode UI
│   │   │   ├── pos/       # Web POS
│   │   │   ├── kitchen/   # Kitchen Display
│   │   │   └── admin/     # Admin Dashboard
│   │   ├── lib/
│   │   │   ├── stores/    # State management
│   │   │   ├── db/        # IndexedDB wrapper
│   │   │   └── api/       # API client
│   │   └── app.html
│   ├── package.json
│   └── svelte.config.js
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### 1. Clone & Setup
```bash
git clone <repository-url>
cd webapp
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2. Run with Docker
```bash
docker-compose up -d
```

### 3. Initialize Database
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py seed_demo_data
```

### 4. Access Applications
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin
- **Kiosk Mode**: http://localhost:5173/kiosk

## 🔐 Environment Variables

### Backend (.env)
```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:pass@db:5432/pos_db
REDIS_URL=redis://redis:6379/0
MIDTRANS_SERVER_KEY=your-midtrans-key
MIDTRANS_CLIENT_KEY=your-midtrans-client-key
```

### Frontend (.env)
```env
PUBLIC_API_URL=http://localhost:8000/api
PUBLIC_WS_URL=ws://localhost:8000/ws
```

## 🎨 Kiosk Mode Features

### Design Principles
- **Touch-First**: Large buttons (min 64x64px), gesture support
- **Fullscreen**: Auto fullscreen API, no browser chrome
- **High Contrast**: Easy to read in bright restaurant environments
- **Fast**: Instant response, optimistic UI updates
- **Offline-Ready**: Works without internet, auto sync when online

### UI Components
- Product grid dengan kategori filter
- Cart management dengan modifier
- Payment selection screen
- Order confirmation dengan receipt
- Offline indicator dengan sync status

### Keyboard Shortcuts
- `F11` - Toggle fullscreen
- `ESC` - Cancel/back
- `Enter` - Confirm
- `Ctrl+K` - Quick search

## 📱 PWA Features
- Install as standalone app
- Offline functionality
- Background sync
- Push notifications (order updates)
- App shortcuts

## 🔧 Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Run Tests
```bash
# Backend
docker-compose exec backend pytest

# Frontend
cd frontend && npm test
```

## 📊 Database Schema

### Key Tables
- `tenants` - Tenant/brand information
- `outlets` - Store locations
- `users` - User accounts dengan role
- `products` - Menu items
- `modifiers` - Product variants (size, toppings, etc.)
- `orders` - Order header
- `order_items` - Order details
- `payments` - Payment transactions
- `kitchen_orders` - Kitchen queue

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login/` - Login
- `POST /api/auth/refresh/` - Refresh token
- `POST /api/auth/logout/` - Logout

### Products
- `GET /api/products/` - List products
- `GET /api/products/:id/` - Product detail
- `POST /api/products/` - Create product (admin)

### Orders
- `POST /api/orders/` - Create order
- `GET /api/orders/:id/` - Order detail
- `PATCH /api/orders/:id/` - Update order status

### Payments
- `POST /api/payments/qris/generate/` - Generate QRIS
- `POST /api/payments/callback/` - Payment webhook
- `GET /api/payments/:id/status/` - Check payment status

## 🏪 Multi-Tenant Architecture

### Tenant Isolation
- Shared database dengan `tenant_id` foreign key
- Middleware untuk auto-inject tenant filter
- Row-level security policies
- Separate S3 buckets per tenant (media files)

### Tenant Features
- Custom branding (logo, colors)
- Per-outlet pricing & menu
- Multi-currency support
- Custom receipt templates

## 📈 Scalability

### Performance Optimizations
- Database indexing pada hot paths
- Redis caching untuk menu data
- Query optimization dengan select_related/prefetch_related
- CDN untuk static assets
- Image optimization & lazy loading

### Horizontal Scaling
- Stateless API servers
- Load balancer (Nginx/HAProxy)
- Database read replicas
- Celery workers untuk background jobs

## 🔒 Security

### Authentication & Authorization
- JWT dengan short expiry (15 min access, 7 day refresh)
- Role-based permissions
- IP whitelisting untuk admin panel
- Rate limiting pada API endpoints

### Payment Security
- PCI DSS compliance
- No card data storage
- Webhook signature verification
- SSL/TLS encryption

### Audit Trail
- Log setiap transaksi
- User activity tracking
- Payment reconciliation logs

## 📦 Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure allowed hosts
- [ ] Setup SSL certificates
- [ ] Configure CORS properly
- [ ] Enable database backups
- [ ] Setup monitoring (Sentry, Prometheus)
- [ ] Configure auto-scaling
- [ ] Load testing

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing
1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License
MIT License

## 👥 Authors
- Senior Software Architect & Full-Stack Engineer

## 📞 Support
- Documentation: [Wiki](https://github.com/your-repo/wiki)
- Issues: [GitHub Issues](https://github.com/your-repo/issues)
- Email: support@yourcompany.com
