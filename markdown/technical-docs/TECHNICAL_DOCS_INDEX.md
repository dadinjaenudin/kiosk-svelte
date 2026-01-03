# 📚 Dokumentasi Teknikal - Enterprise F&B POS System

## Daftar Isi

Dokumentasi ini dibagi menjadi beberapa bagian untuk memudahkan developer baru memahami sistem secara menyeluruh.

### 🏗️ Arsitektur & Konsep Dasar
1. **[SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md)** - Arsitektur sistem keseluruhan
   - High-level architecture
   - Tech stack & justifikasi
   - Design patterns yang digunakan
   - Service architecture (Docker containers)
   - Network & deployment topology

### 🔧 Backend (Django)
2. **[BACKEND_ARCHITECTURE.md](./BACKEND_ARCHITECTURE.md)** - Arsitektur Backend Django
   - Struktur project Django
   - Apps & responsibilities
   - Middleware chain & request flow
   - Database models & relationships
   - Authentication & Authorization

3. **[BACKEND_API_REFERENCE.md](./BACKEND_API_REFERENCE.md)** - Referensi API Lengkap
   - REST API endpoints
   - Request/Response formats
   - Authentication headers
   - Error handling
   - Rate limiting

### 🎨 Frontend (SvelteKit)
4. **[FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md)** - Arsitektur Frontend SvelteKit
   - Struktur project Svelte
   - Routing & navigation
   - State management (Stores)
   - Offline-first strategy
   - Component architecture

5. **[FRONTEND_FLOW.md](./FRONTEND_FLOW.md)** - Alur Program Frontend
   - User journey & flow
   - Kiosk mode flow
   - Kitchen display flow
   - Admin panel flow
   - Offline sync mechanism

### 🏢 Multi-Tenant System
6. **[MULTI_TENANT_DEEP_DIVE.md](./MULTI_TENANT_DEEP_DIVE.md)** - Deep Dive Multi-Tenant
   - Multi-tenant strategy (Shared DB)
   - Tenant isolation mechanism
   - URL-based vs Header-based routing
   - Multi-outlet implementation
   - Context management

### 🔐 Security & Authentication
7. **[SECURITY_IMPLEMENTATION.md](./SECURITY_IMPLEMENTATION.md)** - Implementasi Security
   - JWT authentication flow
   - Token-based auth (Admin)
   - RBAC (Role-Based Access Control)
   - Permission matrix
   - Security best practices

### 📊 Database & Data Flow
8. **[DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)** - Database Schema & ERD
   - Entity Relationship Diagram
   - Table structures
   - Indexes & constraints
   - Data migration strategy
   - Query optimization tips

### 💳 Payment Integration
9. **[PAYMENT_INTEGRATION.md](./PAYMENT_INTEGRATION.md)** - Integrasi Payment Gateway
   - Midtrans/Xendit integration
   - Payment flow sequence
   - Webhook handling
   - Split payment implementation
   - Reconciliation process

### 🍳 Kitchen & Order Management
10. **[KITCHEN_ORDER_FLOW.md](./KITCHEN_ORDER_FLOW.md)** - Kitchen Display & Order Flow
    - Order lifecycle
    - Kitchen display system
    - Real-time updates (WebSocket/Polling)
    - Order status transitions
    - Receipt printing

### 🛠️ Development Guide
11. **[DEVELOPMENT_SETUP.md](./DEVELOPMENT_SETUP.md)** - Setup Development Environment
    - Prerequisites
    - Installation steps
    - Environment configuration
    - Running locally (Docker & Non-Docker)
    - Debugging tips

12. **[CODING_STANDARDS.md](./CODING_STANDARDS.md)** - Coding Standards & Best Practices
    - Python/Django conventions
    - JavaScript/Svelte conventions
    - Git workflow
    - Code review checklist
    - Testing requirements

### 🚀 Deployment
13. **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Panduan Deployment
    - Production setup
    - Environment variables
    - Docker compose production
    - Nginx configuration
    - SSL/TLS setup
    - Monitoring & logging

### 🧪 Testing
14. **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - Panduan Testing
    - Unit testing (Backend)
    - Integration testing
    - E2E testing (Playwright)
    - API testing
    - Test data setup

### 🔍 Troubleshooting
15. **[TROUBLESHOOTING_COMMON_ISSUES.md](./TROUBLESHOOTING_COMMON_ISSUES.md)** - Common Issues & Solutions
    - CORS issues
    - Authentication problems
    - Database connection errors
    - Docker container issues
    - Performance optimization

---

## 🚀 Quick Start untuk Developer Baru

Jika Anda developer baru, ikuti urutan ini:

1. **Hari 1-2**: Pahami arsitektur
   - Baca [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md)
   - Setup environment: [DEVELOPMENT_SETUP.md](./DEVELOPMENT_SETUP.md)
   - Run project pertama kali

2. **Hari 3-5**: Deep dive backend
   - Pelajari [BACKEND_ARCHITECTURE.md](./BACKEND_ARCHITECTURE.md)
   - Pahami [MULTI_TENANT_DEEP_DIVE.md](./MULTI_TENANT_DEEP_DIVE.md)
   - Eksplorasi [BACKEND_API_REFERENCE.md](./BACKEND_API_REFERENCE.md)

3. **Hari 6-8**: Eksplorasi frontend
   - Baca [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md)
   - Ikuti flow di [FRONTEND_FLOW.md](./FRONTEND_FLOW.md)
   - Coba modify UI components

4. **Hari 9-10**: Hands-on
   - Buat feature kecil (bug fix atau improvement)
   - Ikuti [CODING_STANDARDS.md](./CODING_STANDARDS.md)
   - Submit PR pertama

## 📖 Konvensi dalam Dokumentasi

- 🏗️ Arsitektur & konsep
- 🔧 Backend implementation
- 🎨 Frontend implementation
- 📊 Data & database
- 🔐 Security
- 🚀 Deployment & ops
- 🧪 Testing
- 💡 Tips & best practices
- ⚠️ Warning atau catatan penting

## 🤝 Kontribusi

Dokumentasi ini adalah living document. Jika ada yang perlu diperbaiki atau ditambahkan:

1. Update dokumentasi yang relevan
2. Update index ini jika menambah file baru
3. Submit PR dengan label `documentation`

---

**Last Updated**: January 3, 2026  
**Version**: 1.0.0  
**Maintained by**: Development Team
