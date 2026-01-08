# 🔌 Offline-First Architecture - Multi-Store Kiosk System

**Document Version:** 1.0  
**Date:** January 8, 2026  
**Status:** Planning & Design Phase

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture Design](#architecture-design)
3. [Local Server Setup](#local-server-setup)
4. [Offline Capabilities](#offline-capabilities)
5. [Synchronization Strategy](#synchronization-strategy)
6. [Implementation Plan](#implementation-plan)
7. [Testing Scenarios](#testing-scenarios)

---

## 🎯 Overview

### Business Requirements

**Problem:**
- Internet outages should NOT stop store operations
- Kiosk must accept orders even when offline
- Kitchen Display must continue showing orders
- Data must sync when connection restored

**Solution:**
Each store has a **Local Server** (LAN) that acts as:
- Primary data source when offline
- Sync agent to Central Server when online
- Real-time hub for store devices (Kiosk + Kitchen)

### Key Principles

1. **Offline-First:** App works offline by default
2. **Local Authority:** Local Server is source of truth for the store
3. **Eventually Consistent:** Data syncs when connection available
4. **Zero Downtime:** Operations continue during internet outage
5. **Conflict Resolution:** Smart merge strategies for data conflicts

---

## 🏗️ Architecture Design

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    CENTRAL CLOUD SERVER                          │
│             (Internet - Cloud/Data Center)                       │
├─────────────────────────────────────────────────────────────────┤
│  • Central PostgreSQL Database (all stores data)                │
│  • Central Django Backend (master copy)                         │
│  • Admin Portal (multi-store management)                        │
│  • Analytics & Reporting                                        │
│  • Backup & Disaster Recovery                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Internet (HTTPS)
                         │ Bi-directional Sync
                         │
        ┌────────────────┴────────────────┐
        │                                  │
        ▼                                  ▼
┌─────────────────┐              ┌─────────────────┐
│  Store 1 LAN    │              │  Store 2 LAN    │
│  (192.168.1.x)  │              │  (192.168.2.x)  │
└─────────────────┘              └─────────────────┘
        │                                  │
        │                                  │
        ▼                                  ▼

════════════════════════════════════════════════════════════════════
         LOCAL SERVER SETUP (Per Store)
════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│                  LOCAL SERVER (Raspberry Pi / Mini PC)           │
│                    IP: 192.168.1.100 (Store 1)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  PostgreSQL (Local Database)                               │ │
│  │  • Store-specific data (orders, products, customers)      │ │
│  │  • Read/Write when offline                                │ │
│  │  • Sync with central when online                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Django Backend (Local Copy)                               │ │
│  │  Port: 8001                                                │ │
│  │  • Same APIs as Central Server                            │ │
│  │  • Serves Kiosk & Kitchen Display                         │ │
│  │  • Queues transactions for sync                           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Redis (Cache & Queue)                                     │ │
│  │  • Session storage                                         │ │
│  │  • Sync queue (pending uploads)                           │ │
│  │  • Cache frequently accessed data                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Socket.IO Server (Real-time Local)                       │ │
│  │  Port: 3001                                                │ │
│  │  • Kitchen Display updates (instant)                      │ │
│  │  • Order notifications                                    │ │
│  │  • Works offline (LAN only)                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Sync Service (Background)                                │ │
│  │  • Check internet connectivity (every 30s)                │ │
│  │  • Upload pending transactions                            │ │
│  │  • Download updates from central                          │ │
│  │  • Conflict resolution                                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Nginx (Reverse Proxy)                                     │ │
│  │  Port: 80/443                                              │ │
│  │  • Route to Django/Socket.IO                              │ │
│  │  • SSL termination                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
└───────────────────────┬───────────────────────────────────────────┘
                        │
                        │ LAN Network (WiFi/Ethernet)
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Kiosk 1   │ │  Kitchen    │ │   Kiosk 2   │
│   (iPad)    │ │  Display    │ │   (iPad)    │
│ 192.168.1.10│ │  (Tablet)   │ │ 192.168.1.11│
│             │ │192.168.1.20 │ │             │
│ Port: 5174  │ │ Port: 5174  │ │ Port: 5174  │
└─────────────┘ └─────────────┘ └─────────────┘
```

---

## 🖥️ Local Server Setup

### Hardware Options

#### Option 1: Raspberry Pi 4/5 (Recommended for Small-Medium Stores)
```
Specs:
• CPU: Quad-core ARM Cortex-A72 @ 1.8GHz
• RAM: 4GB or 8GB
• Storage: 64GB+ microSD / SSD
• Network: Gigabit Ethernet + WiFi
• Power: 5V/3A USB-C
• Cost: ~$75-$100

Pros:
✅ Low power consumption (~5-15W)
✅ Silent operation (no fans)
✅ Compact size
✅ Low cost
✅ Easy to replace

Cons:
⚠️ Limited performance for >5 kiosks
⚠️ SD card can fail (use SSD)
```

#### Option 2: Mini PC (Intel NUC / Beelink) (Recommended for Large Stores)
```
Specs:
• CPU: Intel i3/i5 or AMD Ryzen 3/5
• RAM: 8GB-16GB DDR4
• Storage: 256GB+ NVMe SSD
• Network: Gigabit Ethernet + WiFi
• Power: 65W
• Cost: ~$200-$400

Pros:
✅ Better performance (>10 kiosks)
✅ Faster database operations
✅ More reliable storage (SSD)
✅ Can run more services

Cons:
⚠️ Higher cost
⚠️ More power consumption
⚠️ May need active cooling
```

### Software Stack

```yaml
Operating System:
  - Ubuntu Server 22.04 LTS (headless)
  - OR Raspberry Pi OS Lite

Services:
  PostgreSQL: 15.x
    - Database: store_local_db
    - Max connections: 50
    - Shared buffers: 256MB (Pi) / 1GB (NUC)
  
  Redis: 7.x
    - Max memory: 256MB (Pi) / 1GB (NUC)
    - Persistence: AOF enabled
  
  Django: 4.2.x
    - Gunicorn workers: 2 (Pi) / 4 (NUC)
    - ASGI for WebSocket support
  
  Socket.IO: 4.x
    - Node.js 18 LTS
    - Redis adapter for clustering
  
  Nginx: 1.24.x
    - Reverse proxy
    - Static file serving
  
  Sync Service: Python 3.11
    - Systemd service
    - Runs every 30 seconds
    - Automatic retry on failure
```

### Network Configuration

```
Local Server IP: 192.168.1.100 (Static)
Subnet Mask: 255.255.255.0
Gateway: 192.168.1.1 (Router)
DNS: 8.8.8.8, 8.8.4.4

Firewall Rules:
- Allow: 80/443 (HTTP/HTTPS) from LAN
- Allow: 8001 (Django API) from LAN
- Allow: 3001 (Socket.IO) from LAN
- Allow: 5432 (PostgreSQL) from localhost only
- Allow: 6379 (Redis) from localhost only
- Block: All external access except sync to Central

Port Forwarding (if needed):
- None (Local Server is LAN-only)
- Sync happens via outbound HTTPS to Central
```

---

## 🔌 Offline Capabilities

### What Works Offline

#### Kiosk (Full Functionality)
```
✅ Product browsing (cached from local DB)
✅ Add to cart (localStorage)
✅ Customer checkout
✅ Order creation (saved to local DB)
✅ Payment processing (cash/card terminal)
✅ Receipt printing
✅ QR code scanning

Backend:
- Products loaded from Local Server
- Orders written to Local PostgreSQL
- Queued for sync when online
```

#### Kitchen Display (Full Functionality)
```
✅ View pending orders
✅ Start preparing
✅ Mark ready
✅ Serve order
✅ Real-time updates via Socket.IO (LAN)
✅ Sound notifications
✅ Statistics

Backend:
- Orders fetched from Local Server
- Status updates via Socket.IO (instant)
- No internet needed
```

### What Requires Online (Central Server)

```
❌ Admin panel (multi-store management)
❌ Cross-store reporting
❌ Central analytics
❌ Master data updates (products, pricing)
❌ Tenant/outlet management
❌ User authentication (first time)

Workaround:
- Cache admin credentials locally
- Schedule master data sync during off-peak hours
- Reports generated locally, uploaded later
```

---

## 🔄 Synchronization Strategy

### Data Sync Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    SYNC SERVICE (Runs Every 30s)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    [Check Internet Connectivity]
                              │
                ┌─────────────┴─────────────┐
                │                           │
         ONLINE │                           │ OFFLINE
                ▼                           ▼
      ┌──────────────────┐         ┌──────────────────┐
      │  START SYNC      │         │  QUEUE MODE      │
      │  PROCESS         │         │  • Add to queue  │
      └──────────────────┘         │  • Retry later   │
                │                   └──────────────────┘
                ▼
    ┌────────────────────────┐
    │  STEP 1: UPLOAD        │
    │  (Local → Central)     │
    ├────────────────────────┤
    │  • Pending Orders      │
    │  • Payment records     │
    │  • Status updates      │
    │  • Kitchen logs        │
    │  • Customer data       │
    └────────────────────────┘
                │
                ▼
    ┌────────────────────────┐
    │  STEP 2: DOWNLOAD      │
    │  (Central → Local)     │
    ├────────────────────────┤
    │  • Product updates     │
    │  • Price changes       │
    │  • New promotions      │
    │  • Configuration       │
    │  • System settings     │
    └────────────────────────┘
                │
                ▼
    ┌────────────────────────┐
    │  STEP 3: RECONCILE     │
    │  (Conflict Resolution) │
    ├────────────────────────┤
    │  • Check timestamps    │
    │  • Merge strategies    │
    │  • Error handling      │
    │  • Log conflicts       │
    └────────────────────────┘
                │
                ▼
        [Mark Sync Complete]
                │
                ▼
        [Wait 30 seconds]
                │
                └──────────┐
                           │
                   (Loop) ◄─┘
```

### Sync Priorities

```python
# Priority Queue for Sync
SYNC_PRIORITIES = {
    'CRITICAL': 1,    # Orders, payments (sync immediately)
    'HIGH': 2,        # Customer data, kitchen logs
    'MEDIUM': 3,      # Statistics, analytics
    'LOW': 4,         # Cache updates, non-essential
}

# Sync Order
1. Orders (created/updated in last hour) → CRITICAL
2. Payment records → CRITICAL
3. Kitchen status changes → HIGH
4. Customer information → HIGH
5. Statistics & logs → MEDIUM
6. Cached data → LOW
```

### Conflict Resolution Strategies

#### 1. Last-Write-Wins (LWW)
```python
# For: Product prices, settings, configurations
def resolve_lww(local_record, central_record):
    """Use the most recent timestamp"""
    if local_record['updated_at'] > central_record['updated_at']:
        return local_record  # Local is newer
    else:
        return central_record  # Central is newer
```

#### 2. Append-Only (No Conflicts)
```python
# For: Orders, payments, logs
# These records are immutable after creation
# Always upload local records, never overwrite
def resolve_append_only(local_records):
    """Upload all local records that don't exist in central"""
    for record in local_records:
        if not exists_in_central(record['id']):
            upload_to_central(record)
```

#### 3. Manual Resolution (Rare Cases)
```python
# For: Inventory conflicts, product availability
def resolve_manual(local_record, central_record):
    """Flag for admin review"""
    create_conflict_log({
        'type': 'inventory_mismatch',
        'local': local_record,
        'central': central_record,
        'requires_review': True
    })
    # Use central value temporarily
    return central_record
```

### Data Models with Sync Support

```python
# Add sync metadata to all models
class SyncMixin(models.Model):
    """Mixin for offline sync support"""
    
    # Unique identifier across all stores
    global_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    
    # Source tracking
    created_at_store = models.ForeignKey('Store', on_delete=SET_NULL, null=True)
    
    # Sync metadata
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Sync'),
            ('synced', 'Synced'),
            ('conflict', 'Conflict'),
            ('error', 'Error'),
        ],
        default='pending',
        db_index=True
    )
    sync_error = models.TextField(blank=True)
    sync_attempts = models.IntegerField(default=0)
    
    # Change tracking
    updated_at = models.DateTimeField(auto_now=True)
    version = models.IntegerField(default=1)  # Optimistic locking
    
    class Meta:
        abstract = True

# Example: Order model with sync
class Order(SyncMixin):
    order_number = models.CharField(max_length=50, unique=True)
    # ... other fields ...
    
    def mark_for_sync(self):
        """Mark this order for upload to central"""
        self.sync_status = 'pending'
        self.save()
```

---

## 📱 Frontend Offline Support

### Service Worker (PWA)

```javascript
// public/service-worker.js
const CACHE_NAME = 'kiosk-v1';
const OFFLINE_CACHE = 'kiosk-offline-v1';

// Files to cache for offline use
const STATIC_ASSETS = [
  '/',
  '/kiosk',
  '/kitchen/display',
  '/offline.html',
  '/manifest.json',
  // CSS, JS, images
];

// Install: Cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
});

// Fetch: Network-first, fallback to cache
self.addEventListener('fetch', (event) => {
  const { request } = event;
  
  // API requests: Try network, queue if offline
  if (request.url.includes('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          return response;
        })
        .catch((error) => {
          // Queue for sync when online
          if (request.method === 'POST') {
            queueRequest(request);
          }
          // Return cached response if available
          return caches.match(request);
        })
    );
  } else {
    // Static assets: Cache-first
    event.respondWith(
      caches.match(request).then((cached) => {
        return cached || fetch(request);
      })
    );
  }
});

// Background Sync
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-orders') {
    event.waitUntil(syncPendingOrders());
  }
});
```

### IndexedDB for Offline Storage

```typescript
// lib/db/indexeddb.ts
import { openDB, DBSchema, IDBPDatabase } from 'idb';

interface KioskDB extends DBSchema {
  orders: {
    key: string; // order_number
    value: {
      order_number: string;
      customer_name: string;
      items: any[];
      total: number;
      created_at: string;
      synced: boolean;
    };
    indexes: { 'by-sync': boolean };
  };
  products: {
    key: number; // product_id
    value: {
      id: number;
      name: string;
      price: number;
      image: string;
      cached_at: string;
    };
  };
}

let db: IDBPDatabase<KioskDB>;

export async function initDB() {
  db = await openDB<KioskDB>('kiosk-store', 1, {
    upgrade(db) {
      // Orders store
      const orderStore = db.createObjectStore('orders', {
        keyPath: 'order_number',
      });
      orderStore.createIndex('by-sync', 'synced');
      
      // Products store
      db.createObjectStore('products', {
        keyPath: 'id',
      });
    },
  });
  return db;
}

// Save order locally when offline
export async function saveOrderOffline(order: any) {
  const db = await initDB();
  await db.add('orders', {
    ...order,
    synced: false,
  });
}

// Get unsynced orders
export async function getUnsyncedOrders() {
  const db = await initDB();
  return db.getAllFromIndex('orders', 'by-sync', false);
}

// Mark order as synced
export async function markOrderSynced(order_number: string) {
  const db = await initDB();
  const order = await db.get('orders', order_number);
  if (order) {
    order.synced = true;
    await db.put('orders', order);
  }
}
```

### Offline Detection

```typescript
// lib/stores/networkStore.ts
import { writable, derived } from 'svelte/store';

interface NetworkStatus {
  online: boolean;
  lastOnline: Date | null;
  pendingSyncCount: number;
}

function createNetworkStore() {
  const { subscribe, set, update } = writable<NetworkStatus>({
    online: navigator.onLine,
    lastOnline: navigator.onLine ? new Date() : null,
    pendingSyncCount: 0,
  });
  
  // Listen for online/offline events
  if (typeof window !== 'undefined') {
    window.addEventListener('online', () => {
      update((state) => ({
        ...state,
        online: true,
        lastOnline: new Date(),
      }));
      // Trigger sync
      syncPendingData();
    });
    
    window.addEventListener('offline', () => {
      update((state) => ({
        ...state,
        online: false,
      }));
    });
  }
  
  return {
    subscribe,
    setPendingCount: (count: number) => {
      update((state) => ({ ...state, pendingSyncCount: count }));
    },
  };
}

export const networkStatus = createNetworkStore();

// Derived store for UI
export const isOnline = derived(networkStatus, ($network) => $network.online);
```

### Smart API Client

```typescript
// lib/api/client.ts
import { get } from 'svelte/store';
import { networkStatus } from '$lib/stores/networkStore';
import { saveOrderOffline } from '$lib/db/indexeddb';

const LOCAL_SERVER = 'http://192.168.1.100:8001';
const CENTRAL_SERVER = 'https://api.yogya-kiosk.com';

export async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const isOnline = get(networkStatus).online;
  
  // Always try Local Server first
  const baseURL = LOCAL_SERVER;
  
  try {
    const response = await fetch(`${baseURL}${endpoint}`, {
      ...options,
      timeout: 5000, // 5 second timeout
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return response;
  } catch (error) {
    console.error('Local server request failed:', error);
    
    // If POST/PUT/DELETE, save for later sync
    if (['POST', 'PUT', 'DELETE'].includes(options.method || 'GET')) {
      await queueForSync(endpoint, options);
      throw new OfflineError('Request queued for sync');
    }
    
    // For GET, try cache
    const cached = await getCachedResponse(endpoint);
    if (cached) {
      return new Response(cached);
    }
    
    throw error;
  }
}

class OfflineError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'OfflineError';
  }
}
```

---

## 📋 Implementation Plan

### Phase 1: Local Server Setup (Week 1-2)

**Hardware Preparation:**
- [ ] Purchase Raspberry Pi 4 (8GB) or Mini PC
- [ ] 128GB+ microSD card or SSD
- [ ] Ethernet cable (CAT6)
- [ ] UPS (Uninterruptible Power Supply) - Optional but recommended

**Software Installation:**
```bash
# 1. Install Ubuntu Server 22.04
# 2. Update system
sudo apt update && sudo apt upgrade -y

# 3. Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y
sudo -u postgres createdb store_local_db

# 4. Install Redis
sudo apt install redis-server -y

# 5. Install Python & Django
sudo apt install python3.11 python3-pip python3-venv -y
python3 -m venv /opt/kiosk/venv
source /opt/kiosk/venv/bin/activate
pip install django djangorestframework gunicorn psycopg2-binary redis

# 6. Install Node.js & Socket.IO
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
npm install -g socket.io

# 7. Install Nginx
sudo apt install nginx -y
```

**Configuration:**
- [ ] Configure static IP address
- [ ] Setup firewall rules
- [ ] Configure PostgreSQL for local access
- [ ] Setup Django settings for local mode
- [ ] Create systemd services

### Phase 2: Backend Modifications (Week 3-4)

**Django Changes:**
```python
# settings.py - Detect environment
import os

IS_LOCAL_SERVER = os.getenv('KIOSK_MODE') == 'local'
IS_CENTRAL_SERVER = os.getenv('KIOSK_MODE') == 'central'

if IS_LOCAL_SERVER:
    # Local server settings
    ALLOWED_HOSTS = ['192.168.1.100', 'localhost']
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'store_local_db',
            # ... local DB config
        }
    }
    # Disable some middleware
    SYNC_TO_CENTRAL = True
    SYNC_INTERVAL = 30  # seconds
else:
    # Central server settings
    ALLOWED_HOSTS = ['api.yogya-kiosk.com']
    DATABASES = {
        'default': {
            # ... central DB config
        }
    }
```

**Sync Service:**
- [ ] Create sync management command
- [ ] Implement upload queue
- [ ] Implement download updates
- [ ] Add conflict resolution
- [ ] Create systemd service for sync

```python
# management/commands/sync_store.py
from django.core.management.base import BaseCommand
from apps.sync.service import SyncService

class Command(BaseCommand):
    help = 'Sync local store data with central server'
    
    def handle(self, *args, **options):
        sync = SyncService()
        sync.run_sync_cycle()
```

**Models Changes:**
- [ ] Add SyncMixin to all models
- [ ] Add global_id field
- [ ] Add sync_status field
- [ ] Create migration

### Phase 3: Frontend PWA (Week 5)

**Service Worker:**
- [ ] Create service-worker.js
- [ ] Implement cache strategies
- [ ] Add background sync
- [ ] Test offline scenarios

**IndexedDB:**
- [ ] Setup database schema
- [ ] Implement CRUD operations
- [ ] Add sync queue management

**Network Detection:**
- [ ] Create networkStore
- [ ] Add online/offline listeners
- [ ] Update UI based on status

### Phase 4: Testing (Week 6)

**Offline Scenarios:**
- [ ] Kiosk offline order creation
- [ ] Kitchen offline operation
- [ ] Internet outage simulation
- [ ] Sync after reconnection
- [ ] Conflict resolution

**Load Testing:**
- [ ] Multiple kiosks simultaneously
- [ ] Kitchen display with many orders
- [ ] Sync with large data volumes

### Phase 5: Deployment (Week 7-8)

**Per Store:**
- [ ] Install local server hardware
- [ ] Configure network
- [ ] Deploy software
- [ ] Initial data seed
- [ ] Test connection to central
- [ ] Train staff
- [ ] Monitor first week

---

## 🧪 Testing Scenarios

### Scenario 1: Internet Outage During Service

```
1. Store operating normally (online)
2. Internet connection lost
   ✓ Kiosk continues accepting orders
   ✓ Orders saved to local DB
   ✓ Kitchen Display shows orders via local Socket.IO
   ✓ No error messages shown to customers
3. Internet restored after 2 hours
   ✓ Sync service detects online status
   ✓ 47 pending orders uploaded to central
   ✓ Product updates downloaded
   ✓ All data reconciled
   ✓ No data loss
```

### Scenario 2: Local Server Restart

```
1. Store operating normally
2. Local server power loss (sudden shutdown)
3. Server restarts automatically (UPS)
   ✓ PostgreSQL recovers (WAL replay)
   ✓ Redis recovers (AOF persistence)
   ✓ Services restart (systemd)
   ✓ Kiosks reconnect automatically
   ✓ Kitchen Display reconnects
   ✓ Orders not lost
   ✓ Downtime: < 2 minutes
```

### Scenario 3: Conflicting Price Update

```
1. Central updates product price: Rp 25,000 → Rp 27,000
2. Store offline, hasn't received update
3. Customer orders at old price Rp 25,000
4. Internet restored
5. Sync conflict detected:
   - Local order: Rp 25,000 (customer already paid)
   - Central price: Rp 27,000 (new price)
6. Resolution:
   ✓ Keep local order price (customer paid)
   ✓ Mark as price_override = true
   ✓ Flag for accounting review
   ✓ Future orders use new price
```

### Scenario 4: Multi-Store Sync

```
1. Store A creates order ORD-001
2. Store B creates order ORD-001 (same number!)
3. Sync conflict detected:
   - Both have order_number = ORD-001
   - Different global_id (UUID)
4. Resolution:
   ✓ Keep both orders (different UUIDs)
   ✓ Rename Store B order → ORD-001-B
   ✓ Update order numbering sequence
   ✓ Log conflict for review
```

---

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Check local server status
curl http://192.168.1.100:8001/health/

# Response:
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "disk_space": "78% available",
  "last_sync": "2026-01-08T14:30:00Z",
  "pending_sync": 5,
  "uptime": "15 days"
}
```

### Sync Status Dashboard

```
┌─────────────────────────────────────────┐
│  STORE: Yogya Kapatihan                 │
│  STATUS: Online ✅                       │
├─────────────────────────────────────────┤
│  Last Sync: 30 seconds ago              │
│  Pending Upload: 3 orders               │
│  Sync Errors: 0                         │
│  Local DB Size: 245 MB                  │
│  Internet: Connected (45 Mbps)          │
│  Uptime: 15 days 4 hours                │
└─────────────────────────────────────────┘
```

### Alerts

```yaml
Alerts:
  - Low disk space (< 20%)
  - Sync failure (> 5 attempts)
  - Database connection lost
  - Internet offline > 1 hour
  - High pending sync count (> 100 orders)
  - Local server unreachable

Notification Methods:
  - Email to IT team
  - SMS to store manager
  - Admin dashboard alert
```

---

## 💰 Cost Estimate (Per Store)

```
Hardware:
  Raspberry Pi 4 (8GB): $75
  128GB microSD / SSD: $25
  Power supply: $15
  Case + cooling: $20
  Network cable: $5
  UPS (optional): $100
  TOTAL: $240 (without UPS) / $340 (with UPS)

OR

  Mini PC (Intel NUC):
  - Intel i3 + 8GB RAM + 256GB SSD: $300-400

Software:
  All open-source: $0

Setup Time:
  Initial setup: 4-6 hours
  Testing: 2-3 hours
  Training: 1-2 hours

Monthly Costs:
  Electricity (Pi): ~$2/month
  Electricity (NUC): ~$5/month
  Maintenance: Minimal
```

---

## 🎯 Benefits Summary

### Business Benefits
✅ **Zero Downtime** - Operations continue during internet outages
✅ **Fast Response** - Local network = no latency
✅ **Data Security** - Local copy prevents total data loss
✅ **Customer Experience** - No "system down" messages
✅ **Cost Savings** - Less bandwidth usage (only sync deltas)

### Technical Benefits
✅ **Scalability** - Each store independent
✅ **Reliability** - Multiple points of failure eliminated
✅ **Performance** - Local database faster than cloud
✅ **Flexibility** - Can customize per store if needed

### Operational Benefits
✅ **Staff Confidence** - System always works
✅ **Reduced Support** - Fewer internet-related issues
✅ **Data Resilience** - Multiple backups (local + central)

---

## 📚 Next Steps

1. **Proof of Concept** (2 weeks)
   - Setup 1 local server at dev environment
   - Test offline scenarios
   - Validate sync mechanism

2. **Pilot Store** (1 month)
   - Deploy to 1 store
   - Monitor closely
   - Gather feedback
   - Fix issues

3. **Rollout** (3-6 months)
   - Deploy to all stores gradually
   - 1-2 stores per week
   - Provide training
   - Monitor performance

4. **Optimization** (Ongoing)
   - Tune sync intervals
   - Optimize database
   - Improve conflict resolution
   - Add features

---

**Document End**
