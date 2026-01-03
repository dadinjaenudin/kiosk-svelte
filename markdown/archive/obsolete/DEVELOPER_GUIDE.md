# Panduan Developer Komprehensif

Panduan ini ditujukan untuk developer baru yang akan bekerja pada sistem Enterprise F&B POS (multi-tenant, offline-first, real-time). Dokumen ini menjelaskan arsitektur, alur program, detail implementasi, serta workflow pengembangan end-to-end.

---

## Ringkasan Sistem

- Backend: Django 4.2 + Django REST Framework (DRF) dengan Celery dan Redis
- Frontend (Kiosk/POS/Kitchen): SvelteKit + TailwindCSS + DaisyUI, PWA, IndexedDB, Service Worker
- Admin Panel: SvelteKit dengan Playwright untuk E2E testing
- Database: PostgreSQL 15
- Cache/Queue: Redis 7
- Infrastruktur: Docker Compose + Nginx sebagai reverse proxy
- Pembayaran: Midtrans/Xendit/Stripe (QRIS, e-wallet, kartu, tunai)

Referensi cepat:
- Komposisi layanan: lihat [docker-compose.yml](../../docker-compose.yml)
- Ringkasan arsitektur: lihat [markdown/ARCHITECTURE.md](ARCHITECTURE.md)
- Fitur & jalur cepat: lihat [README.md](../README.md)

---

## Arsitektur Sistem

### Komponen Utama

- Backend API (Django/DRF): autentikasi JWT, multi-tenant isolation, endpoints POS, webhook pembayaran, sinkronisasi data
- Celery Worker & Beat: background jobs (sinkronisasi, rekonsiliasi pembayaran, batch tasks)
- Frontend SvelteKit (Kiosk/POS/Kitchen): UI operasional, offline-first, IndexedDB, background sync
- Admin SvelteKit: manajemen produk, promosi, outlet, pengguna, monitoring
- Nginx: reverse proxy untuk frontend/admin/backend, melayani static/media
- PostgreSQL: basis data utama
- Redis: cache dan message broker untuk Celery

### Jaringan & Port (default Docker Compose)

- Backend API: http://localhost:8001
- Frontend (Kiosk/POS/Kitchen): http://localhost:5174
- Admin Panel: http://localhost:5175
- Nginx (reverse proxy): http://localhost:8082 (HTTP), https://localhost:8443 (HTTPS)
- PostgreSQL: localhost:5433
- Redis: localhost:6380

Detail pemetaan port dan volume: lihat [docker-compose.yml](../../docker-compose.yml).

### Pola Multi-Tenant (Shared DB + Row-Level Isolation)

- Identifikasi tenant melalui subdomain/header/token (`X-Tenant-ID` atau claim `tenant_id` dalam JWT)
- Middleware men-set konteks tenant pada setiap request dan mem-filter query secara otomatis
- Semua model bisnis turunan dari `TenantAwareModel` dengan `tenant_id` sebagai foreign key
- Rekomendasi: tambahan kebijakan row-level security (opsional) dan audit trail per tenant

### Offline-First (PWA + IndexedDB)

- Data penting (produk, kategori, cart, orders, payments) di-cache pada IndexedDB
- Operasi saat offline disimpan dalam `sync_queue`, dieksekusi saat koneksi kembali (background sync)
- Konflik: Last-Write-Wins untuk update produk; server-authority untuk harga & stok; merge untuk item cart
- Service Worker untuk caching aset, strategi cache-first pada menu; network-first pada transaksi

---

## Alur Program

### Backend Request Lifecycle

1. HTTP Request masuk melalui Nginx → Backend (Gunicorn/Django)
2. Middleware autentikasi JWT memvalidasi token dan meng-attach user + tenant context
3. Middleware tenant meng-inject filter `tenant_id` ke ORM (DRF viewset/queryset)
4. View/Serializer DRF memproses bisnis logic (products, orders, payments, kitchen, dsb.)
5. Response JSON sesuai kontrak API, dengan status dan metadata yang konsisten
6. Event tertentu men-trigger tugas Celery (contoh: webhook pembayaran, sinkronisasi batch)

### Frontend (Kiosk/POS/Kitchen)

1. App bootstrap: load konfigurasi tenant/outlet, cek status online
2. Prefetch menu/kategori ke IndexedDB; render grid produk dan panel cart
3. Aksi user (tambah item, modifier, bayar) meng-update store Svelte dan IndexedDB
4. Saat online: API call langsung + optimistik UI; Saat offline: enqueue ke `sync_queue`
5. Sinkronisasi background: commit orders/payments; reconcile status; update indikator offline/online
6. WebSocket (opsional) untuk status kitchen/order (lihat `PUBLIC_WS_URL` jika diaktifkan)

### Pembayaran QRIS (contoh alur)

1. User pilih metode QRIS → frontend memanggil `POST /payments/qris/generate/`
2. Backend mengembalikan payload QR, transaksi id; frontend menampilkan QR
3. Polling status setiap beberapa detik; webhook backend mengkonfirmasi pembayaran
4. Order menjadi `PAID`; UI menampilkan receipt; data disinkronkan ke server

---

## Detail Implementasi

### Backend (Django/DRF)

Struktur apps: [backend/apps](../backend/apps)
- `tenants/`: manajemen tenant, outlet, branding
- `products/`: produk, kategori, modifier, pricing per outlet
- `orders/`: header/detail order, status (NEW/COOKING/READY/SERVED/PAID), hold/recall
- `payments/`: integrasi gateway (Midtrans/Xendit/Stripe), webhook, rekonsiliasi
- `kitchen/`: antrean dapur, alur status, notifikasi
- `promotions/`: engine promo/discount
- `users/`: akun pengguna, RBAC (owner/admin/cashier/kitchen)
- `core/`: utilitas umum, middleware, helpers

Dependensi utama: lihat [backend/requirements.txt](../backend/requirements.txt)

Poin penting:
- Autentikasi: `djangorestframework-simplejwt` (access 15 menit, refresh 7 hari), CORS diaktifkan
- Dokumentasi API: `drf-spectacular` (opsional, endpoint schema)
- Caching: `django-redis` untuk data menu panas (TTL pendek)
- Tugas latar: `celery` + `django-celery-beat` untuk scheduled jobs
- Logging/Monitoring: `sentry-sdk` jika dikonfigurasi

### Frontend (SvelteKit)

Repo `frontend/`:
- Struktur umum:
  - `src/routes/` → `kiosk/`, `pos/`, `kitchen/`, `admin/`
  - `src/lib/stores/` → Svelte stores (cart, user, online status, dsb.)
  - `src/lib/db/` → wrapper IndexedDB (Dexie/IDB)
  - `src/lib/api/` → klien API (fetch), handle JWT dan error
- Dev scripts: lihat [frontend/package.json](../frontend/package.json)
- PWA: `vite-plugin-pwa`; offline cache dan background sync

### Admin Panel (SvelteKit + Playwright)

Repo `admin/`:
- Fokus: manajemen entitas (produk, promosi, outlet, pengguna), laporan, grafik
- Playwright untuk E2E/UI testing (`npm run test`, `test:ui`, `test:report`)
- Dev scripts: lihat [admin/package.json](../admin/package.json)

---

## API Kontrak (Ringkasan)

Contoh endpoint (lihat detail di [README.md](../README.md) dan [ARCHITECTURE.md](ARCHITECTURE.md)):
- Autentikasi: `POST /api/auth/login/`, `POST /api/auth/refresh/`, `POST /api/auth/logout/`
- Produk: `GET /api/products/`, `GET /api/products/:id/`, `POST /api/products/`
- Order: `POST /api/orders/`, `GET /api/orders/:id/`, `PATCH /api/orders/:id/`
- Pembayaran: `POST /api/payments/qris/generate/`, `POST /api/payments/callback/`, `GET /api/payments/:id/status/`

Konvensi:
- Semua response JSON memiliki `status`, `data`, `error` (jika ada)
- Paginasi default (DRF) dan filter via query string
- JWT Bearer di header `Authorization`

---

## Setup & Workflow Pengembangan

### Prasyarat
- Windows (PowerShell), Docker & Docker Compose
- Node.js 18+, Python 3.11+

### Jalankan dengan Docker (disarankan)

1) Siapkan environment:
- Backend: salin `.env` dari contoh jika tersedia (lihat README)
- Frontend/Admin: set `PUBLIC_API_URL` ke `http://localhost:8001/api`

2) Start services:

```powershell
# Dari root proyek
docker-compose up -d
```

3) Inisialisasi database:

```powershell
docker-compose exec backend python manage.py makemigrations --noinput
docker-compose exec backend python manage.py migrate --noinput
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py seed_demo_data
```

4) Akses aplikasi:
- Frontend: http://localhost:5174
- Backend API: http://localhost:8001/api
- Admin Panel: http://localhost:5175
- Nginx: http://localhost:8082

### Pengembangan Lokal Tanpa Docker (opsional)

Backend:
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8001
```

Frontend:
```powershell
cd frontend
npm install
npm run dev -- --port 5174 --host
```

Admin:
```powershell
cd admin
npm install
npm run dev:local
```

Set variabel lingkungan sesuai `.env` contoh di README.

### Testing

Backend:
```powershell
docker-compose exec backend pytest
```

Frontend:
```powershell
cd frontend
npm run check
# tambahkan test sesuai kebutuhan
```

Admin (Playwright):
```powershell
cd admin
npm run test
npm run test:ui
npm run test:report
```

---

## Keamanan & RBAC

- JWT: access (±15 menit), refresh (±7 hari), simpan aman
- RBAC: role `owner`, `admin`, `cashier`, `kitchen` dengan permissions granular
- Rate limiting untuk endpoint sensitif
- Verifikasi signature webhook pembayaran
- CORS & `ALLOWED_HOSTS` sesuai environment produksi

---

## Observability & Skalabilitas

- Metrics: p50/p95/p99, payment success rate, panjang `sync_queue`, cache hit-rate
- Logging terstruktur per tenant & outlet
- Caching bertingkat: Service Worker → Redis → DB
- Horizontal scaling: beberapa instance API, read replicas DB, worker Celery paralel

---

## Troubleshooting

- Container tidak naik (`docker-compose up` gagal):
  - Cek port bentrok (lihat pemetaan di [docker-compose.yml](../../docker-compose.yml))
  - Pastikan `db` dan `redis` sehat (healthcheck hijau)
  - Backend healthcheck: `http://localhost:8001/api/health/`
- Frontend tidak bisa memanggil API:
  - Pastikan `PUBLIC_API_URL` mengarah ke `http://localhost:8001/api`
  - Periksa CORS pada backend
- Webhook pembayaran tidak masuk:
  - Verifikasi URL publik (melalui Nginx), cek signature dan log payment

---

## Kontribusi

1. Buat branch fitur (`feature/...`)
2. Tambahkan test dan dokumentasi bila relevan
3. Ikuti gaya kode (Black/Flake8/ESLint/Prettier)
4. PR dengan ringkasan perubahan dan dampak ke arsitektur

---

## Referensi Tambahan

- [markdown/FRONTEND_INTEGRATION_GUIDE.md](FRONTEND_INTEGRATION_GUIDE.md)
- [markdown/ADMIN_QUICK_START.md](ADMIN_QUICK_START.md)
- [markdown/FEATURE_ROADMAP.md](FEATURE_ROADMAP.md)
- [markdown/IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)