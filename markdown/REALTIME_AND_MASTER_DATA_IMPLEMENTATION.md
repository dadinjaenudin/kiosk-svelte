# Real-time Updates & Master Data Pre-fetching Implementation

## Overview

Implementasi solusi real-time updates dengan fallback mechanism dan master data pre-fetching untuk memastikan integritas data saat offline.

## Arsitektur

```
┌─────────────────────────────────────────────────────────────┐
│                        ONLINE MODE                           │
│  Kiosk/Kitchen ←→ Django Channels (WebSocket) ←→ Backend    │
│        ↓                                                     │
│  Real-time order updates (push-based)                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       OFFLINE MODE                           │
│  Kiosk/Kitchen ←→ Local Sync Server (HTTP Polling)          │
│        ↓                                                     │
│  Poll setiap 3 detik untuk order baru (pull-based)          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   MASTER DATA SYNC                           │
│  App Start → Check Internet → Pre-fetch (Menu, Harga, Promo)│
│        ↓                                                     │
│  Simpan ke IndexedDB untuk akses offline                    │
└─────────────────────────────────────────────────────────────┘
```

## Komponen yang Dibuat

### 1. Master Data Service (`frontend/src/lib/services/masterDataService.ts`)

**Fitur:**
- Pre-fetching menu, kategori, dan promosi saat app dibuka (jika online)
- Versioning untuk incremental updates (hanya download perubahan)
- IndexedDB caching untuk akses offline
- Auto-retry mechanism jika fetch gagal

**API yang Dibutuhkan:**
```typescript
GET /api/products/?since_version=0
GET /api/categories/?since_version=0
GET /api/promotions/?since_version=0
```

**Penggunaan:**
```typescript
import { masterDataService } from '$lib/services/masterDataService';

// Di +page.ts atau +layout.ts (app entry point)
onMount(async () => {
  try {
    await masterDataService.preFetchData();
    console.log('Master data synced!');
  } catch (error) {
    console.error('Failed to sync master data:', error);
  }
});

// Akses cached data
const products = await masterDataService.getProducts();
const categories = await masterDataService.getCategories();
const promotions = await masterDataService.getActivePromotions();
```

### 2. Socket Service dengan Polling (`frontend/src/lib/services/socketService.ts`)

**Update:**
- Tambah `mode: 'polling'` untuk fallback mechanism
- Method `startPolling(outletId)` untuk polling ke Local Server
- Method `stopPolling()` untuk stop polling
- Auto fallback: WebSocket gagal → Polling aktif

**Penggunaan:**
```typescript
import { socketService } from '$lib/services/socketService';

// Coba connect WebSocket dulu
socketService.connectLocal();

// Jika gagal, start polling sebagai fallback
setTimeout(() => {
  if (!socketService.isConnected()) {
    socketService.startPolling(outletId);
  }
}, 5000);
```

### 3. Local Sync Server Polling Endpoint (`local-sync-server/server.js`)

**Endpoint Baru:**
```
GET /api/orders?outlet_id=1&since_id=100
```

**Response:**
```json
[
  {
    "id": 101,
    "order_number": "ORD-2024-001",
    "outlet_id": 1,
    "status": "pending",
    "items": [...],
    "total_amount": "150000",
    "created_at": "2024-01-11T10:30:00Z"
  }
]
```

**Fitur:**
- In-memory cache (100 order terakhir per outlet)
- Incremental fetch (hanya order baru sejak `since_id`)
- Auto-cleanup order lama

### 4. Django Channels Setup (Backend)

**File Baru:**
- `backend/apps/realtime/consumers.py` - WebSocket consumer
- `backend/apps/realtime/routing.py` - WebSocket URL routing
- `backend/apps/realtime/utils.py` - Helper untuk broadcast events
- `backend/config/asgi.py` - ASGI config (updated)
- `backend/config/settings.py` - Settings (updated)

**WebSocket URL:**
```
ws://backend-url/ws/outlet/{outlet_id}/
```

**Events:**
- `new_order` - Order baru dibuat
- `order_updated` - Order diupdate
- `order_completed` - Order selesai
- `order_cancelled` - Order dibatalkan
- `kitchen_status_changed` - Status kitchen berubah

## Installation Guide

### 1. Install Django Channels Dependencies

```bash
cd backend
pip install -r requirements-channels.txt
```

Isi `requirements-channels.txt`:
```
channels==4.0.0
channels-redis==4.1.0
daphne==4.0.0
```

### 2. Update Django Settings

File `backend/config/settings.py` sudah diupdate dengan:
- `'daphne'` di INSTALLED_APPS (harus paling atas)
- `'channels'` di INSTALLED_APPS
- `'apps.realtime'` di INSTALLED_APPS
- `ASGI_APPLICATION = 'config.asgi.application'`
- `CHANNEL_LAYERS` config untuk Redis

### 3. Migrate Database (jika ada model baru)

```bash
cd backend
python manage.py migrate
```

### 4. Run Backend dengan Daphne (ASGI Server)

**Development:**
```bash
# Cara 1: Daphne (recommended untuk WebSocket)
daphne -b 0.0.0.0 -p 8000 config.asgi:application

# Cara 2: Django dev server (WebSocket tidak work)
python manage.py runserver
```

**Production (Docker):**
Update `backend/Dockerfile`:
```dockerfile
# Ganti CMD dari gunicorn ke daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
```

### 5. Ensure Redis is Running

Django Channels butuh Redis untuk channel layer:
```bash
# Docker
docker-compose up -d redis

# Or standalone
redis-server
```

### 6. Update Local Sync Server

File `local-sync-server/server.js` sudah diupdate dengan polling endpoint.

Restart server:
```bash
cd local-sync-server
npm run dev
```

### 7. Update Frontend to Use Master Data Service

**Di `frontend/src/routes/+layout.svelte` atau app entry point:**

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { masterDataService } from '$lib/services/masterDataService';
  import { networkService } from '$lib/services/networkService';

  onMount(async () => {
    // Start network monitoring
    networkService.startMonitoring();

    // Pre-fetch master data jika online
    const status = networkService.getStatus();
    if (status.mode === 'online') {
      try {
        console.log('🔄 Pre-fetching master data...');
        await masterDataService.preFetchData();
        console.log('✅ Master data synced successfully');
      } catch (error) {
        console.error('❌ Master data sync failed:', error);
        // App tetap jalan, gunakan cached data
      }
    } else {
      console.log('📴 Offline mode - using cached master data');
    }
  });
</script>
```

### 8. Integrate Broadcasting in Order Views

**Contoh di `backend/apps/orders/views_order_group.py`:**

```python
from apps.realtime.utils import broadcast_new_order

class PublicOrderGroupViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        # Broadcast via Django Channels
        if response.status_code == 201:
            order_data = {
                'id': response.data['id'],
                'order_number': response.data['order_number'],
                'outlet_id': response.data['outlet'],
                'status': 'pending',
                'items': response.data['items'],
                'total_amount': str(response.data['total_amount']),
                'created_at': response.data['created_at']
            }
            broadcast_new_order(order_data)
        
        return response
```

## Testing

### 1. Test Master Data Pre-fetching

```bash
# Buka browser DevTools → Application → IndexedDB
# Cek database: kiosk_master_data
# Stores: products, categories, promotions, metadata
```

### 2. Test WebSocket Connection (Online)

```javascript
// Browser console
const ws = new WebSocket('ws://localhost:8000/ws/outlet/1/');
ws.onmessage = (e) => console.log('Received:', JSON.parse(e.data));
ws.onopen = () => console.log('Connected!');

// Send ping
ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
```

### 3. Test Polling (Offline)

```bash
# Stop Local Sync Server WebSocket
# Kitchen display akan auto-switch ke polling mode
# Cek console: "🔄 Starting polling to Local Server..."
```

### 4. Test Local Server Polling Endpoint

```bash
# Get orders untuk outlet 1
curl "http://localhost:3001/api/orders?outlet_id=1"

# Get orders since ID 100
curl "http://localhost:3001/api/orders?outlet_id=1&since_id=100"
```

## Monitoring

### 1. Django Channels Status

```python
# Django shell
python manage.py shell

from channels.layers import get_channel_layer
channel_layer = get_channel_layer()

# Test send
from asgiref.sync import async_to_sync
async_to_sync(channel_layer.group_send)(
    'outlet_1',
    {'type': 'new_order', 'data': {'test': 'message'}}
)
```

### 2. Master Data Status

```typescript
// Frontend console
import { masterDataService } from '$lib/services/masterDataService';

// Get status
masterDataService.status.subscribe(s => console.log('Status:', s));

// Get version
masterDataService.version.subscribe(v => console.log('Version:', v));

// Manual sync
await masterDataService.preFetchData();
```

### 3. Socket Service Status

```typescript
import { socketService } from '$lib/services/socketService';

socketService.status.subscribe(s => {
  console.log('Mode:', s.mode);
  console.log('Central connected:', s.centralConnected);
  console.log('Local connected:', s.localConnected);
  console.log('Polling:', s.isPolling);
});
```

## Troubleshooting

### WebSocket Connection Failed

**Error:** `WebSocket connection to 'ws://...' failed`

**Solutions:**
1. Pastikan backend running dengan Daphne (bukan Gunicorn)
2. Cek CORS settings di Django
3. Cek firewall/network rules
4. Test dengan `wscat -c ws://localhost:8000/ws/outlet/1/`

### Master Data Not Syncing

**Error:** `Failed to fetch products`

**Solutions:**
1. Cek API endpoint exists: `GET /api/products/`
2. Tambahkan `since_version` parameter support di backend
3. Cek CORS credentials
4. Check browser DevTools Network tab

### Polling Not Working

**Error:** `Polling failed: 404`

**Solutions:**
1. Pastikan Local Sync Server running
2. Cek endpoint: `http://localhost:3001/api/orders`
3. Restart Local Sync Server
4. Check console logs di server

### Redis Connection Error

**Error:** `Error connecting to Redis`

**Solutions:**
1. Start Redis: `redis-server` or `docker-compose up -d redis`
2. Cek REDIS_URL di `.env`
3. Test: `redis-cli ping` (should return PONG)

## Benefits

### ✅ Real-time Updates When Online
- Instant order notifications via WebSocket
- Low latency (<100ms)
- Push-based (server actively sends updates)

### ✅ Reliable Updates When Offline
- Polling fallback mechanism
- Works tanpa internet (local network only)
- Pull-based (client checks for updates)

### ✅ Data Integrity
- Menu & harga always up-to-date
- Versioned cache (incremental updates)
- Offline-first with sync on app start

### ✅ Graceful Degradation
- WebSocket failed → Auto fallback ke polling
- Internet lost → Use cached master data
- Server down → Queue orders for later sync

## Next Steps

1. **Implement Backend API for Master Data:**
   - Add `since_version` parameter di products/categories/promotions endpoints
   - Return incremental updates based on version

2. **Add UI Indicators:**
   - Show sync status di UI (syncing, synced, error)
   - Display last sync time
   - Warning jika data outdated

3. **Optimize Polling:**
   - Adaptive polling interval (3s saat ada activity, 10s saat idle)
   - Stop polling when tab not visible
   - WebSocket reconnect attempt saat online kembali

4. **Add Master Data Refresh:**
   - Manual refresh button di admin
   - Auto-refresh setiap X jam
   - Background sync saat idle

5. **Monitor & Logging:**
   - Track sync success/failure rate
   - Monitor WebSocket connection quality
   - Alert jika data outdated > 24 jam
