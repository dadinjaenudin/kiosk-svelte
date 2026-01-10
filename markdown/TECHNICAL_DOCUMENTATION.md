# Technical Documentation - YOGYA Kiosk System
**Last Updated:** January 10, 2026  
**Version:** 2.0 (Offline-First Implementation)

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Offline-First Implementation](#offline-first-implementation)
4. [Workarounds for Browser Cache Issues](#workarounds-for-browser-cache-issues)
5. [Socket.IO Communication](#socketio-communication)
6. [Order Flow: Online vs Offline](#order-flow-online-vs-offline)
7. [Kitchen Display System](#kitchen-display-system)
8. [Connection Status Management](#connection-status-management)
9. [Critical Code Sections](#critical-code-sections)
10. [Setup and Configuration](#setup-and-configuration)
11. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    YOGYA Kiosk System                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Kiosk UI   │    │   Kitchen    │    │    Admin     │  │
│  │  (Customer)  │    │   Display    │    │    Panel     │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                    │          │
│         └───────────────────┼────────────────────┘          │
│                             │                               │
│                    ┌────────▼────────┐                      │
│                    │  Frontend (Vite) │                      │
│                    │  SvelteKit       │                      │
│                    └────────┬────────┘                      │
│                             │                               │
│         ┌───────────────────┼───────────────────┐          │
│         │                   │                   │          │
│   ┌─────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐    │
│   │  Backend  │      │   Local   │      │  Network  │    │
│   │  Django   │      │   Sync    │      │  Service  │    │
│   │  :8001    │      │  Server   │      │  (Health) │    │
│   └───────────┘      │  :3001    │      └───────────┘    │
│                      └───────────┘                         │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Storage Layer                                        │  │
│  │  - PostgreSQL (Backend Data)                         │  │
│  │  - IndexedDB (Offline Orders - Browser)              │  │
│  │  - LocalStorage (Config - Browser)                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Network Modes

**1. Online Mode (Normal Operation)**
```
Kiosk → Django Backend (HTTP) → PostgreSQL
Kitchen ← Django Backend (HTTP Polling)
```

**2. Offline Mode (No Internet)**
```
Kiosk → IndexedDB → Local Sync Server (Socket.IO)
Kitchen ← Local Sync Server (Socket.IO) [LAN only]
```

**3. Dual Mode (Hybrid)**
```
Kiosk → IndexedDB + Django Backend
Kitchen ← Local Sync Server + Django Backend
```

---

## Core Components

### 1. Frontend Services

#### a. Network Service (`frontend/src/lib/services/networkService.ts`)
**Purpose:** Detect online/offline status and measure latency

**Key Methods:**
- `performHealthCheck()` - Check backend availability every 30s
- `updateStatus()` - Update network status store
- `retryConnection()` - Manual retry

**Store:** `networkStatus`
```typescript
{
  mode: 'online' | 'offline' | 'checking' | 'error',
  isOnline: boolean,
  latency: number | null,
  lastCheckTime: Date | null
}
```

**⚠️ CRITICAL:** Health check runs on `document.visibilitychange` and interval (30s)

---

#### b. Socket Service (`frontend/src/lib/services/socketService.ts`)
**Purpose:** Manage Socket.IO connections to Central and Local servers

**Key Methods:**
- `connectCentral()` - Connect to Django backend (if Socket.IO enabled)
- `connectLocal()` - Connect to Local Sync Server (port 3001)
- `emitToLocal(event, data)` - Send to Local Sync Server
- `emitToCentral(event, data)` - Send to Central Server
- `onLocal(event, handler)` - Listen to Local events
- `onCentral(event, handler)` - Listen to Central events

**Store:** `socketStatus`
```typescript
{
  centralConnected: boolean,
  localConnected: boolean,
  mode: 'dual' | 'central' | 'local' | 'none',
  lastConnectTime: Date | null
}
```

**⚠️ CRITICAL BEHAVIOR:**
- Central Server connection errors are **suppressed** (Django doesn't have Socket.IO)
- Local Server connection **auto-retries** in background
- `emitToLocal()` will attempt reconnect if not connected

---

#### c. Offline Order Service (`frontend/src/lib/services/offlineOrderService.ts`)
**Purpose:** Store orders locally in IndexedDB and manage sync queue

**Database Schema (Dexie.js):**
```typescript
db.version(1).stores({
  orders: '++id, order_number, store_id, synced, created_at',
  syncQueue: '++id, action, order_number, synced, created_at'
});
```

**Key Methods:**
- `saveOrder(order)` - Save to IndexedDB + broadcast to Local Sync Server
- `getSyncQueue()` - Get pending sync items
- `markAsSynced(id)` - Mark order as synced
- `rebuildSyncQueue()` - Rebuild queue from unsynced orders
- `getStats()` - Get offline order statistics

**⚠️ CRITICAL:** When saving offline order, it **MUST** broadcast via Local Sync Server:
```typescript
// After saving to IndexedDB
socketService.emitToLocal('order:created:offline', offlineOrder);
```

---

#### d. Sync Service (`frontend/src/lib/services/syncService.ts`)
**Purpose:** Auto-sync offline orders when online

**Key Methods:**
- `startSync()` - Begin sync process
- `syncPendingOrders()` - Sync all from queue
- `manualSync()` - User-triggered sync

**Store:** `syncProgress`
```typescript
{
  isRunning: boolean,
  totalItems: number,
  processedItems: number,
  successCount: number,
  failureCount: number,
  errors: Array<{orderNumber, errorMessage}>
}
```

**⚠️ CRITICAL FIX:** Line 150-160 - Fixed ReferenceError with unsubscribe:
```typescript
// WRONG (causes error):
const unsubscribe = networkStatus.subscribe(status => {
  resolve(status);
  unsubscribe(); // ReferenceError!
});

// CORRECT:
let unsubscribeFn: (() => void) | undefined;
unsubscribeFn = networkStatus.subscribe(status => {
  resolve(status);
  if (unsubscribeFn) unsubscribeFn();
});
```

---

### 2. Local Sync Server (`local-sync-server/server.js`)
**Port:** 3001  
**Purpose:** Enable LAN communication when internet is down

**Tech Stack:**
- Express.js (HTTP endpoints)
- Socket.IO (WebSocket communication)

**Key Events Handled:**

| Event | Source | Target | Purpose |
|-------|--------|--------|---------|
| `join-kitchen` | Kitchen | Server | Kitchen joins outlet room |
| `order:created:offline` | Kiosk | Kitchen | Broadcast offline order to kitchen |
| `new_order` | Backend | Kitchen | Broadcast online order |
| `update_status` | Kitchen | Backend | Update order status |
| `complete_order` | Kitchen | Backend | Mark order complete |
| `cancel_order` | Kitchen | Backend | Cancel order |

**Room Management:**
```javascript
// Rooms are organized by outlet ID
`outlet_${outletId}` -> Set of socket IDs
```

**⚠️ CRITICAL EVENT:** `order:created:offline` handler
```javascript
socket.on('order:created:offline', (order) => {
  const outletId = order.checkout_data?.carts?.[0]?.outlet_id || order.store_id;
  
  // Broadcast to kitchen displays in same outlet
  io.to(`outlet_${outletId}`).emit('order:created:offline', order);
});
```

**Health Check Endpoint:**
```
GET http://localhost:3001/health
Returns: { status, connections, rooms, uptime }
```

---

### 3. Backend (Django)
**Port:** 8001  
**Purpose:** Main API for online operations

**Key Endpoints:**
- `POST /api/order-groups/` - Create order
- `GET /api/kitchen/orders/pending/` - Get pending orders
- `PATCH /api/kitchen/orders/{id}/` - Update order status
- `GET /api/products/` - Get products
- `POST /api/auth/login/` - Authentication

**⚠️ IMPORTANT:** Backend does **NOT** have Socket.IO server. Uses HTTP-only.

---

## Offline-First Implementation

### Order Creation Flow

#### **ONLINE MODE:**
```
1. User fills cart
2. Checkout page validates
3. POST to /api/order-groups/
4. Backend saves to PostgreSQL
5. Navigate to /kiosk/success/[groupNumber]
6. Kitchen polls and gets new order
```

#### **OFFLINE MODE:**
```
1. User fills cart
2. Checkout page detects offline (networkStatus.isOnline = false)
3. Save to IndexedDB via offlineOrderService.saveOrder()
4. Broadcast to Local Sync Server: socketService.emitToLocal('order:created:offline')
5. Local Sync Server broadcasts to kitchen displays in same outlet
6. Kitchen receives via socketService.onLocal('order:created:offline')
7. Kitchen transforms offline order format and adds to display
8. Show inline success (NOT navigation) with amber/orange theme
9. When online returns, syncService auto-syncs to backend
```

### Offline Order Format

**Kiosk saves:**
```typescript
{
  order_number: 'OFFLINE-{timestamp}-{random}',
  store_id: number,
  customer_name: string,
  customer_phone: string,
  total_amount: number,
  payment_method: 'cash' | 'qris' | 'transfer',
  checkout_data: {
    carts: [...],
    customerName: string,
    customerPhone: string,
    // ... full checkout data
  },
  created_at: ISO timestamp,
  synced: false
}
```

**Kitchen transforms to:**
```typescript
{
  id: 'offline-{timestamp}',
  order_number: 'OFFLINE-...',
  status: 'pending',
  tenant: number,
  outlet: number,
  store: number,
  customer_name: string,
  customer_phone: string,
  items: [...], // Extracted from checkout_data.carts
  total_amount: number,
  payment_method: string,
  is_offline: true,
  created_at: ISO timestamp
}
```

---

## Workarounds for Browser Cache Issues

### Problem: Svelte Reactive Bindings Broken

**Root Cause:** Vite HMR + Browser cache corruption causes Svelte `$store` reactive bindings to permanently disconnect.

**Symptoms:**
- `$kitchenOrders` not updating UI
- `$networkStatus` stuck on "Checking..."
- Orders fetched but not displayed

### Solution 1: Local Component Variables (Kitchen Display)

**File:** `frontend/src/routes/kitchen/display/+page.svelte`

**Lines 19-22:**
```typescript
// WORKAROUND: Local copy for reactivity (since $store binding is broken)
let localPendingOrders: any[] = [];
let localPreparingOrders: any[] = [];
let localReadyOrders: any[] = [];
```

**Update Pattern:**
```typescript
async function fetchAllOrders() {
  const pendingRes = await fetch(`${API_BASE}/kitchen/orders/pending/`);
  const pending = await pendingRes.json();
  
  // Update local variables directly (not via store)
  localPendingOrders = pending;
  
  // Also update store (for other subscribers)
  setPendingOrders(pending);
}
```

**UI Binding:**
```svelte
<!-- Use local variables, NOT $store -->
{#each localPendingOrders as order (order.id)}
  <KitchenOrderCard {order} />
{/each}
```

**⚠️ CRITICAL:** Always update both:
1. Local variable (for UI)
2. Store (for consistency)

---

### Solution 2: Polling with `get()` (Network Status)

**File:** `frontend/src/routes/kitchen/display/+page.svelte`

**Lines 31-50:**
```typescript
// Manual network status tracking
let networkOnline = true;
let networkMode = 'checking';
let networkLatency: number | null = null;
let socketMode = 'none';

// Polling function to force update
function updateNetworkStatus() {
  const netStatus = get(networkStatus);
  const sockStatus = get(socketStatus);
  
  networkOnline = netStatus.isOnline;
  networkMode = netStatus.mode;
  networkLatency = netStatus.latency;
  socketMode = sockStatus.mode;
}

// Poll every 2 seconds
statusPollInterval = setInterval(() => {
  updateNetworkStatus();
}, 2000);
```

**⚠️ CRITICAL:** 
- Use `get(store)` to force read current value
- Do NOT rely on `$store` reactive syntax
- Poll frequently (2s) for real-time updates

---

### Solution 3: Skip Polling When Offline

**Lines 216-222:**
```typescript
polling = setInterval(async () => {
  // Skip polling if offline to avoid error spam
  if (!networkOnline) {
    console.log('⏸️ Skipping poll - System offline');
    return;
  }
  await fetchAllOrders();
}, 10000);
```

**⚠️ CRITICAL:** Always check `networkOnline` before HTTP requests in polling

---

## Socket.IO Communication

### Connection Flow

#### Kiosk Connection
**File:** `frontend/src/routes/kiosk/+layout.svelte`

**Lines 23-27:**
```typescript
onMount(() => {
  // Always connect to Local Sync Server
  socketService.connectLocal();
  
  // Connect to Central if online
  if (networkStatus.isOnline) {
    socketService.connectCentral();
  }
});
```

#### Kitchen Connection
**File:** `frontend/src/routes/kitchen/display/+page.svelte`

**Lines 186-194:**
```typescript
onMount(async () => {
  await socketService.connectLocal();
  
  // Join kitchen room
  socketService.emitToLocal('join-kitchen', {
    outletId: $kitchenConfig.outletId,
    deviceId: $kitchenConfig.deviceId
  });
});
```

### Event Listeners

#### Kitchen Listens for Offline Orders
**Lines 87-146:**
```typescript
socketService.onLocal('order:created:offline', async (data) => {
  console.log('🔔 Offline order received:', data);
  
  // Transform to backend format
  const offlineOrder = {
    id: `offline-${Date.now()}`,
    order_number: data.order_number,
    status: 'pending',
    is_offline: true,
    // ... map all fields
  };
  
  // Add to local pending orders
  localPendingOrders = [offlineOrder, ...localPendingOrders];
  
  // Play sound
  playNewOrderSound();
});
```

**⚠️ CRITICAL:** Order format transformation is REQUIRED because:
- Kiosk sends raw checkout data
- Kitchen expects backend API format
- Must extract items from `checkout_data.carts`

---

## Order Flow: Online vs Offline

### Online Order Success Page

**File:** `frontend/src/routes/kiosk/success/[groupNumber]/+page.svelte`

**Features:**
- Purple/Blue gradient background
- Animated green checkmark
- Full receipt with all order details
- Auto countdown (10s) to return
- "Order Successful!" heading
- Shows: customer info, items, payment, total

**Colors:**
- Background: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- Checkmark: Green (`#4caf50`)
- Receipt: White card

---

### Offline Order Success (Inline)

**File:** `frontend/src/routes/kiosk/checkout/+page.svelte`

**Lines 252-295 (Template):**

**Features:**
- Amber/Orange/Yellow gradient background
- Save/Download icon (NOT checkmark)
- Warning badge "📴 OFFLINE MODE"
- "Order Saved Locally! 💾" heading
- Subtitle: "⏳ Will sync to kitchen when internet returns"
- Order number with "🔄 Not synced yet"
- Warning section: "⚠️ IMPORTANT: This order is NOT synced yet!"
- Bottom warning: "⚡ Please keep internet connection stable"

**Colors:**
- Background: `bg-gradient-to-br from-amber-500 via-orange-500 to-yellow-500`
- Badge: Amber background with border
- Icon: Amber/Orange with pulse animation
- Payment: Amber boxes (not green)

**⚠️ CRITICAL DIFFERENCES:**

| Aspect | Online | Offline |
|--------|--------|---------|
| Background | Purple/Blue | Amber/Orange/Yellow |
| Icon | Green checkmark | Amber save icon (pulse) |
| Heading | "Order Successful!" | "Order Saved Locally! 💾" |
| Badge | None | "📴 OFFLINE MODE" |
| Message | "Sent to kitchen" | "Will sync when online" |
| Order Number | Gray box | Amber box + "Not synced" |
| Payment Box | Green | Amber/Orange |
| Warning | None | Multiple warnings |
| Navigation | Redirect to separate page | Inline display |

---

## Kitchen Display System

### Status Badge (Collapsible)

**Component:** `frontend/src/lib/components/ConnectionStatus.svelte`

**Default State:** Icon only (collapsed)
```svelte
<!-- Collapsed: Only shows colored icon -->
<button class="status-badge clickable icon-only">
  🟢 <!-- or 🟡 or 🔴 -->
  <span class="toggle-arrow">▶</span>
</button>
```

**Expanded State:** Full details
```svelte
<button class="status-badge clickable expanded">
  🟢 <span>Online (Local Only)</span>
  <span class="toggle-arrow">▼</span>
</button>
<!-- Details shown below -->
<div class="status-details">
  Network: Online
  Latency: 19ms
  Socket: Local
</div>
```

**Styling:**
```css
.badge.icon-only {
  padding: 8px;
  border-radius: 50%; /* Circle */
  font-size: 16px;
}
```

**⚠️ CRITICAL:** Badge must be collapsible by default to not block UI

---

### Kitchen Display Header Badge

**File:** `frontend/src/routes/kitchen/display/+page.svelte`

**Lines 448-474 (Template):**
```svelte
<div class="header-actions">
  <!-- Inline Connection Status (Collapsible) -->
  <button 
    class="status-badge clickable" 
    class:online={networkOnline} 
    class:offline={!networkOnline}
    class:expanded={statusExpanded}
    on:click={toggleStatus}
  >
    <span class="status-dot"></span>
    <span class="status-label">{networkOnline ? 'Online' : 'Offline'}</span>
    {#if statusExpanded}
      <div class="status-details-inline">
        <span>Socket: {socketMode}</span>
        <span>{networkLatency}ms</span>
      </div>
    {/if}
    <span class="toggle-icon">{statusExpanded ? '▼' : '▶'}</span>
  </button>
</div>
```

**State Management:**
```typescript
let statusExpanded = false;
function toggleStatus() {
  statusExpanded = !statusExpanded;
}
```

---

### Order Display Logic

**Pending Column Shows:**
1. Offline orders (from Local Sync Server) - with "📴 Pending Sync" badge
2. Online orders (from Django backend)

**Code:**
```svelte
<div class="order-list">
  <!-- Offline Orders First -->
  {#each offlineOrders as order}
    <div class="offline-order-card">
      <div class="offline-badge">📴 Pending Sync</div>
      <!-- ... order details -->
    </div>
  {/each}
  
  <!-- Online Orders -->
  {#each localPendingOrders as order}
    <KitchenOrderCard {order} />
  {/each}
</div>
```

**⚠️ CRITICAL:** Offline orders display BEFORE online orders for visibility

---

## Connection Status Management

### Status Badge Color Logic

**File:** `frontend/src/lib/components/ConnectionStatus.svelte`

**Lines 67-89:**
```typescript
function getBadgeColor(netMode: ConnectionMode, sockMode: SocketMode): string {
  if (netMode === 'online') {
    if (sockMode === 'dual' || sockMode === 'central') {
      return 'green'; // Fully online with socket
    } else if (sockMode === 'local') {
      return 'yellow'; // Online but only local socket
    } else {
      return 'green'; // Online without socket (HTTP works)
    }
  } else if (netMode === 'offline') {
    if (sockMode === 'local') {
      return 'yellow'; // Offline but LAN works
    } else {
      return 'red'; // No connection at all
    }
  } else if (netMode === 'checking') {
    return 'yellow';
  } else {
    return 'red'; // Error state
  }
}
```

**Badge Icons:**
- 🟢 Green: Fully online
- 🟡 Yellow: Limited connectivity (LAN only or checking)
- 🔴 Red: Completely offline

**Status Text:**
- "Online (Central + Local)" - Dual connection
- "Online (Local Only)" - LAN only
- "Offline (LAN Mode)" - No internet but LAN works
- "Offline" - No connection
- "Checking..." - Initial state

---

## Critical Code Sections

### ⚠️ DO NOT MODIFY

#### 1. Kitchen Display Local Variables Pattern
**File:** `frontend/src/routes/kitchen/display/+page.svelte`  
**Lines:** 19-22, All fetch functions

**Reason:** This is the ONLY way to make orders display due to broken Svelte reactivity

---

#### 2. Offline Order Broadcast
**File:** `frontend/src/lib/services/offlineOrderService.ts`  
**Lines:** 120-130

```typescript
// MUST broadcast after saving to IndexedDB
if (typeof window !== 'undefined') {
  const { socketService } = await import('./socketService');
  socketService.emitToLocal('order:created:offline', offlineOrder);
}
```

**Reason:** Kitchen displays won't receive orders without this

---

#### 3. Local Sync Server Event Handler
**File:** `local-sync-server/server.js`  
**Lines:** 202-212

```javascript
socket.on('order:created:offline', (order) => {
  const outletId = order.checkout_data?.carts?.[0]?.outlet_id || order.store_id;
  io.to(`outlet_${outletId}`).emit('order:created:offline', order);
});
```

**Reason:** This broadcasts offline orders to kitchen displays

---

#### 4. Kitchen Offline Order Listener
**File:** `frontend/src/routes/kitchen/display/+page.svelte`  
**Lines:** 87-146

**Reason:** Transforms offline order format and adds to display

---

#### 5. Network Status Polling
**File:** `frontend/src/routes/kitchen/display/+page.svelte`  
**Lines:** 31-50, 180-185

**Reason:** Only way to get real-time network status due to broken subscriptions

---

#### 6. Offline Success UI Differentiation
**File:** `frontend/src/routes/kiosk/checkout/+page.svelte`  
**Lines:** 252-295

**Reason:** Critical UX - users must know order is local, not synced

---

## Setup and Configuration

### Starting the System

**1. Backend (Django)**
```bash
cd backend
docker-compose up -d backend
# Accessible at http://localhost:8001
```

**2. Frontend (SvelteKit + Vite)**
```bash
docker-compose up -d frontend
# Accessible at http://localhost:5173
```

**3. Local Sync Server (Socket.IO)**
```bash
cd local-sync-server
npm run dev
# Accessible at http://localhost:3001
```

### Environment Variables

**Frontend (`.env`)**
```env
VITE_API_BASE_URL=http://localhost:8001/api
VITE_CENTRAL_SOCKET_URL=http://localhost:8001
VITE_LOCAL_SOCKET_URL=http://localhost:3001
```

**Backend (`backend/.env`)**
```env
DATABASE_URL=postgresql://...
DJANGO_SECRET_KEY=...
DEBUG=True
```

---

## Troubleshooting

### Issue: Orders not displaying in kitchen

**Check:**
1. Console: Is `localPendingOrders` being updated?
2. Console: Any errors in `fetchAllOrders()`?
3. Network tab: Is `/kitchen/orders/pending/` returning data?

**Solution:** If data fetched but not displayed → Cache corruption → Use local variables pattern

---

### Issue: Offline orders not appearing in kitchen

**Check:**
1. Local Sync Server running on port 3001?
2. Console: "📤 Emitting to Local Server: order:created:offline"?
3. Console: "🔔 Offline order received from kiosk"?

**Solution:**
- Restart Local Sync Server
- Check `socket.on('order:created:offline')` handler exists
- Check kitchen joined room: `join-kitchen` event

---

### Issue: Connection status stuck on "Checking..."

**Check:**
1. Console: Is `updateNetworkStatus()` being called?
2. Is `statusPollInterval` running?

**Solution:** Broken reactive binding → Use polling with `get(networkStatus)`

---

### Issue: ReferenceError in syncService

**Check:** Line 150-160 in `syncService.ts`

**Solution:** Use pattern:
```typescript
let unsubscribeFn: (() => void) | undefined;
unsubscribeFn = networkStatus.subscribe(status => {
  resolve(status);
  if (unsubscribeFn) unsubscribeFn();
});
```

---

### Issue: Port 3001 already in use

**Solution:**
```powershell
# Find PID
netstat -ano | findstr :3001

# Kill process
Stop-Process -Id <PID> -Force

# Restart
cd local-sync-server
npm run dev
```

---

### Issue: Vite HMR errors when offline

**Behavior:** `ERR_INTERNET_DISCONNECTED` spam in console

**Reason:** Vite dev server trying to reconnect for HMR

**Impact:** None - this is cosmetic only

**Solution:** Ignore these errors OR use production build

---

## Testing Checklist

### Online Mode Test
- [ ] Create order from kiosk
- [ ] Order appears in kitchen display immediately
- [ ] Status badge shows green/online
- [ ] Success page is purple/blue gradient
- [ ] Receipt shows complete details

### Offline Mode Test
- [ ] Disconnect internet
- [ ] Status badge changes to red/offline
- [ ] Create order from kiosk
- [ ] Order saved to IndexedDB
- [ ] Order appears in kitchen display (via LAN)
- [ ] Success page is amber/orange gradient
- [ ] Warning message about "not synced yet"
- [ ] Kitchen shows "📴 Pending Sync" badge

### Reconnection Test
- [ ] While offline, create 3 orders
- [ ] All 3 appear in kitchen
- [ ] Reconnect internet
- [ ] Status badge changes to green/online
- [ ] Sync service automatically syncs orders
- [ ] Orders marked as synced in IndexedDB

---

## Important Notes

### 🚨 Critical Behaviors to Preserve

1. **Local Variables in Kitchen Display**
   - Never remove or replace with `$store` syntax
   - Always update both local vars AND stores

2. **Offline Order Broadcast**
   - Must emit to Local Sync Server after IndexedDB save
   - Event name MUST be `order:created:offline`

3. **Network Status Polling**
   - Poll with `get(store)` every 2 seconds
   - Never rely solely on reactive `$store`

4. **Offline Success UI**
   - MUST be visually distinct (amber/orange)
   - MUST show warnings about sync status

5. **Kitchen Badge Collapsible**
   - Default to collapsed (icon only)
   - Expandable on click

### 📌 Architecture Principles

1. **Offline-First:** Always save locally first, sync later
2. **LAN-Based:** Use Local Sync Server for offline communication
3. **Dual-Path:** Support both online and offline simultaneously
4. **Progressive Enhancement:** Work offline, better when online
5. **Cache Resilient:** Use workarounds for broken reactivity

### 🔧 Maintenance Guidelines

1. **Before Changing Kitchen Display:**
   - Test with cache cleared AND with cache
   - Verify local variables still update

2. **Before Changing Offline Flow:**
   - Test with internet disconnected
   - Verify Local Sync Server receives events

3. **Before Changing Socket Logic:**
   - Test both central and local connections
   - Verify auto-reconnection works

4. **Before Changing UI:**
   - Maintain visual distinction online vs offline
   - Test badge collapsible behavior

---

## Future Improvements (Suggestions Only)

1. **Production Build:** Remove Vite HMR for cleaner offline experience
2. **Sync Queue UI:** Show pending sync items in UI
3. **Manual Sync Button:** Allow user to trigger sync
4. **Receipt Printing:** Print offline orders locally
5. **Order History:** View all orders (synced and pending)
6. **Multi-Outlet:** Better support for multiple outlets
7. **Push Notifications:** Notify when offline order syncs

---

## Version History

**v2.0 - January 10, 2026**
- Offline-first implementation
- Local Sync Server for LAN communication
- IndexedDB for offline storage
- Workarounds for cache corruption
- Collapsible connection status badge
- Differentiated offline success UI

**v1.0 - Previous**
- Online-only operation
- Direct Django backend communication
- No offline support

---

## Support and Contact

For issues or questions about this implementation, refer to:
- GitHub Issues: (if applicable)
- Documentation: `/markdown` folder
- Technical Diagrams: `/markdown/technical-docs`

---

**END OF TECHNICAL DOCUMENTATION**

⚠️ **WARNING:** Any modifications to the workarounds or critical sections listed above may break functionality. Test thoroughly after any changes.