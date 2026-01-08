# 🧪 Offline-First Testing Guide

Complete manual testing guide for Hybrid Offline-First Architecture implementation.

---

## 📋 Prerequisites

### Required Setup:
1. ✅ Docker containers running (backend, frontend)
2. ✅ Local Sync Server ready (`local-sync-server/`)
3. ✅ Browser with DevTools (Chrome/Edge recommended)
4. ✅ Test data seeded (tenants, stores, outlets, products)

### Test Environment:
```bash
# Check Docker containers
docker-compose ps

# Should see:
kiosk_pos_backend   (port 8001)
kiosk_pos_frontend  (port 5174)
postgres            (port 5432)
redis               (port 6379)
```

---

## 🚀 Phase 1: Local Sync Server Testing

### 1.1 Start Local Sync Server

```bash
# Navigate to local-sync-server directory
cd D:\YOGYA-Kiosk\kiosk-svelte\local-sync-server

# Install dependencies (first time only)
npm install

# Start server
npm start
```

**Expected Output:**
```
╔════════════════════════════════════════════════════════════╗
║     Kitchen Sync Server - RUNNING                          ║
║     Socket.IO + Express                                    ║
╚════════════════════════════════════════════════════════════╝

✅ Socket.IO Server: http://localhost:3001
✅ WebSocket Path:   ws://localhost:3001/socket.io/
✅ Health Check:     http://localhost:3001/health
✅ Outlet Stats:     http://localhost:3001/outlets

📡 Waiting for connections from POS and Kitchen displays...
```

### 1.2 Test Health Endpoint

```bash
# Test health check (PowerShell)
curl http://localhost:3001/health

# Expected Response:
{
  "status": "ok",
  "timestamp": "2026-01-09T...",
  "connections": 0,
  "rooms": {},
  "uptime": 12.345
}
```

### 1.3 Test Outlet Stats Endpoint

```bash
curl http://localhost:3001/outlets

# Expected Response:
{
  "outlets": []
}
```

✅ **Checkpoint:** Local Sync Server is running and responding to HTTP requests.

---

## 🔌 Phase 2: Network Detection Service Testing

### 2.1 Open Kitchen Display

1. Open browser: http://localhost:5174/kitchen/display
2. Open DevTools (F12) → Console tab
3. Look for initialization logs:

```
🍳 Kitchen Display initialized...
📡 Network status: Online
✅ Sync service started
🟢 Central Server: Online (123ms)
```

### 2.2 Test Network Status Component

**Visual Check:**
- Top-right corner: ConnectionStatus component visible
- Badge color: 🟢 Green = "Online (Central + Local)"
- Network status: "Online"
- Socket mode: "dual" or "local"

### 2.3 Simulate Offline Mode

**Method 1: Browser Offline Mode**
1. Open DevTools → Network tab
2. Check "Offline" checkbox (throttling dropdown)
3. Wait 2-5 seconds

**Expected Behavior:**
- Console log: `🔴 Browser: Network offline`
- Badge changes to: 🟡 Yellow = "Offline (LAN Mode)"
- Toast notification: "Switched to Offline Mode"

**Method 2: Disconnect Internet**
1. Physically disconnect ethernet cable OR disable WiFi
2. Wait for health check timeout (2 seconds)

**Expected Behavior:**
- Console log: `🔴 Central Server: Unreachable`
- Badge: 🟡 Yellow
- Connection mode: "offline"
- Socket mode: "local" (if Local Server running)

### 2.4 Restore Online Mode

1. Re-enable network (uncheck "Offline" or reconnect internet)
2. Wait 2-5 seconds for auto-detection

**Expected Behavior:**
- Console log: `🟢 Network restored, reconnecting to Central Socket...`
- Badge: 🟢 Green
- Toast notification: "Back Online - Syncing..."
- Auto-sync triggers

✅ **Checkpoint:** Network detection and auto-failover working correctly.

---

## 📦 Phase 3: Offline Order Flow Testing

### 3.1 Create Order While Online (Baseline)

1. Open Kiosk page: http://localhost:5174/kiosk/products
2. Add products to cart (multiple outlets if possible)
3. Proceed to checkout
4. Fill customer info
5. Complete payment

**Expected Behavior:**
- Order submits to Central Server (HTTP POST)
- Order appears in Kitchen Display within 0-10 seconds (HTTP Polling)
- If WebSocket enabled: Instant update (<1 second)
- Console log: `📦 Socket: New order received ORD-...`

### 3.2 Create Order While Offline

**Setup:**
1. Enable offline mode (DevTools → Network → Offline)
2. Verify ConnectionStatus badge is 🟡 Yellow
3. Ensure Local Sync Server is running

**Test Steps:**
1. Open Kiosk: http://localhost:5174/kiosk/products
2. Browse products (should load from cache/local)
3. Add products to cart
4. Proceed to checkout
5. Fill customer info
6. Submit order

**Expected Behavior:**
- Order saves to **IndexedDB** (not Central Server)
- Console log: `💾 Order saved offline: ORD-...`
- Order emits to **Local Socket.IO**
- Kitchen Display receives order via Local Socket
- Kitchen Display shows order immediately
- ConnectionStatus shows: "Pending Orders: 1"
- Sync Queue size: 1 item

**Verification:**
1. Open DevTools → Application tab → IndexedDB
2. Expand `KioskOfflineDB` database
3. Check `orders` table → should have 1 unsaved order
4. Check `syncQueue` table → should have 1 pending sync item

### 3.3 Automatic Sync on Network Restore

**Setup:**
- At least 1 pending order in offline queue
- Kitchen Display open

**Test Steps:**
1. Re-enable network (uncheck Offline mode)
2. Wait 2-3 seconds

**Expected Behavior:**
- Console log: `🟢 Network online, checking for pending orders...`
- Console log: `📤 Starting sync: 1 items in queue`
- Console log: `📤 Syncing order: ORD-...`
- Console log: `✅ Synced: ORD-...`
- Toast notification: "All Orders Synced Successfully"
- ConnectionStatus: "Pending Orders: 0"
- Sync Queue: empty
- Order appears in Central Server database

**Verification:**
1. Check backend logs: `docker logs kiosk_pos_backend`
2. Should see POST request to `/api/orders/groups/`
3. Check database:
```bash
docker exec -it postgres psql -U kioskadmin -d kioskdb -c "SELECT order_number, status FROM orders_order ORDER BY created_at DESC LIMIT 5;"
```

✅ **Checkpoint:** Offline order creation and auto-sync working correctly.

---

## 🍳 Phase 4: Kitchen Display Dual Mode Testing

### 4.1 Test HTTP Polling (Default)

1. Open Kitchen Display: http://localhost:5174/kitchen/display
2. Create order from Kiosk (online mode)

**Expected Behavior:**
- Console log (every 10 seconds): `📡 Fetching orders...`
- Order appears within 0-10 seconds
- No Socket.IO logs

### 4.2 Test Real-Time Updates

1. Kitchen Display should show ConnectionStatus widget in top-right
2. Create order from Kiosk

**Expected Behavior:**
- Console log (immediate): `📦 Socket: New order received ORD-...`
- Order appears **instantly** (<1 second)
- Sound notification plays
- HTTP Polling continues as fallback

### 4.3 Test Dual Socket Mode (Central + Local)

**Setup:**
1. Ensure internet is online
2. Enable WebSocket Mode
3. Verify both sockets connected:

```javascript
// In Console, check socket status
$socketStatus
// Should show:
{
  centralConnected: false,  // Central socket may not exist yet
  localConnected: true,
  mode: "local",
  lastConnectTime: [Date],
  reconnectAttempts: 0
}
```

**Test:**
1. Create order from Kiosk (online)
2. Order emits to **both** Central + Local Socket.IO
3. Kitchen Display receives via Local Socket (faster)

**Expected Behavior:**
- Instant update via Local Socket (<50ms latency)
- Backup via HTTP Polling (10s interval)
- No duplicate orders

### 4.4 Test Offline Kitchen Display

**Setup:**
1. Start Local Sync Server
2. Disconnect internet (offline mode)
3. Kitchen Display should show:
   - Badge: 🟡 Yellow
   - Mode: "Offline (LAN Mode)"
   - Socket: "local"

**Test:**
1. Create order from Kiosk (offline mode)
2. Order saves to IndexedDB
3. Order emits to Local Socket.IO
4. Kitchen Display receives via Local Socket

**Expected Behavior:**
- Order appears instantly on Kitchen Display
- No Central Server communication
- Everything works via LAN only
- Sound notification plays

✅ **Checkpoint:** Kitchen Display receives orders in all modes (Polling, WebSocket, Offline).

---

## 🔄 Phase 5: Background Sync Service Testing

### 5.1 Test Auto-Sync Interval

**Setup:**
1. Create 3 orders offline
2. Verify ConnectionStatus shows: "Pending Orders: 3"
3. Check console: `📥 Added to sync queue: ORDER_CREATE ORD-...` (3 times)

**Test:**
1. Re-enable network
2. **Do NOT manually click "Sync Now"**
3. Wait 30 seconds

**Expected Behavior:**
- Console log (after 30s): `🟢 Network online, checking for pending orders...`
- Console log: `📤 Starting sync: 3 items in queue`
- Progress bar appears in ConnectionStatus
- Items sync one by one:
  ```
  📤 Syncing order: ORD-001 (ORDER_CREATE)
  ✅ Synced: ORD-001
  📤 Syncing order: ORD-002 (ORDER_CREATE)
  ✅ Synced: ORD-002
  ...
  ```
- Toast: "All Orders Synced Successfully"
- ConnectionStatus: "Pending Orders: 0"

### 5.2 Test Manual Sync Button

**Setup:**
1. Create 1 order offline
2. Re-enable network
3. **Before** auto-sync triggers (within 30s)

**Test:**
1. Click "Sync Now" button in ConnectionStatus component

**Expected Behavior:**
- Immediate sync trigger
- Console log: `🔄 Manual sync triggered by user`
- Progress bar updates
- Sync completes within 2-3 seconds
- Success toast

### 5.3 Test Sync Priority Queue

**Setup:**
1. Create 3 orders offline with different priorities:
   - Critical: Order creation
   - Normal: Status update
   - Low: Cache update

**Test:**
1. Re-enable network
2. Trigger sync

**Expected Behavior:**
- Orders sync in priority order: **Critical → Normal → Low**
- Console log shows order:
  ```
  📤 Syncing order: ORD-001 (ORDER_CREATE) [priority: critical]
  ✅ Synced: ORD-001
  📤 Syncing order: ORD-002 (ORDER_CREATE) [priority: critical]
  ...
  ```

### 5.4 Test Sync Retry Logic

**Setup:**
1. Create 1 order offline
2. **Keep offline mode** (simulate Central Server unreachable)
3. Click "Sync Now"

**Expected Behavior:**
- Sync attempt fails
- Console log: `❌ syncOrderCreate failed: [error]`
- Retry count increments: `🔄 Retry #1 for sync item: ORD-...`
- Error appears in ConnectionStatus error list
- Item remains in sync queue

**Test Retry:**
1. Re-enable network
2. Auto-sync will retry

**Expected Behavior:**
- Retry succeeds
- Item removed from queue
- Success message

### 5.5 Test Max Retries

**Setup:**
1. Modify max_retries to 3 (for faster testing)
2. Create 1 order offline
3. Keep offline for 5 sync attempts

**Expected Behavior:**
- After 3 retries, item removed from queue
- Console log: `⚠️ Max retries reached for sync item: ORD-...`
- Order marked as "failed sync" in stats

✅ **Checkpoint:** Background sync service handling all scenarios correctly.

---

## 📊 Phase 6: Connection Status UI Testing

### 6.1 Visual Status Badges

**Test all 3 states:**

| Mode | Badge | Status Text | Trigger |
|------|-------|-------------|---------|
| Online (Dual) | 🟢 Green | "Online (Central + Local)" | Both sockets connected |
| Online (Local) | 🟡 Yellow | "Online (Local Only)" | Only local socket |
| Offline (LAN) | 🟡 Yellow | "Offline (LAN Mode)" | Browser offline + local socket |
| Disconnected | 🔴 Red | "No Signal" | No connections at all |

**Verification:**
1. Screenshot each state
2. Verify colors match design
3. Check text is readable

### 6.2 Connection Details Display

**Check all fields visible:**
- ✅ Network: Online/Offline
- ✅ Latency: [X]ms (when available)
- ✅ Socket: dual/central/local/none
- ✅ Last Check: [timestamp]
- ✅ Pending Orders: [count] (when > 0)
- ✅ Sync Queue: [count] items (when > 0)
- ✅ Last Sync: [timestamp]

### 6.3 Progress Bar Testing

**Test:**
1. Create 5 orders offline
2. Re-enable network
3. Trigger sync

**Expected Behavior:**
- Progress bar appears during sync
- Percentage updates: 0% → 20% → 40% → 60% → 80% → 100%
- Progress text: "Syncing... [X]%"
- Progress bar disappears when complete

### 6.4 Button Interactions

**Test "Retry" button:**
1. Go offline
2. Click "Retry" button
3. Should attempt reconnection
4. Button shows: "⏳ Retrying..."
5. After timeout, shows result

**Test "Sync Now" button:**
1. Create order offline
2. Re-enable network
3. Click "Sync Now"
4. Should trigger immediate sync
5. Button disabled during sync

### 6.5 Error List Display

**Test:**
1. Create order offline
2. Keep offline
3. Click "Sync Now" (will fail)
4. Check error list appears

**Expected:**
- Error title: "Sync Errors (1):"
- Error item shows:
  - Order number: "ORD-..."
  - Error message: "HTTP timeout"
  - Retry count displayed

✅ **Checkpoint:** Connection Status UI displaying all information correctly.

---

## 🚨 Phase 7: Edge Case & Stress Testing

### 7.1 Rapid Online/Offline Switching

**Test:**
1. Toggle offline mode ON/OFF rapidly (10 times in 30 seconds)

**Expected Behavior:**
- No crashes
- Status updates correctly each time
- No duplicate sync attempts
- Console logs clean (no errors)

### 7.2 Multiple Offline Orders

**Test:**
1. Go offline
2. Create 20 orders from Kiosk
3. Re-enable network
4. Wait for auto-sync

**Expected Behavior:**
- All 20 orders save to IndexedDB
- All 20 orders sync successfully
- No order loss
- Kitchen Display shows all orders
- Sync completes within 60 seconds

### 7.3 Internet Dropout During Sync

**Test:**
1. Create 10 orders offline
2. Re-enable network
3. Start sync
4. After 5 orders synced, disconnect internet again

**Expected Behavior:**
- Sync stops gracefully (no crash)
- 5 orders marked as synced
- 5 orders remain in queue
- When online resumes, remaining 5 sync automatically

### 7.4 Local Server Restart During Operation

**Test:**
1. Kitchen Display connected via Local Socket
2. Stop Local Sync Server: `Ctrl+C`
3. Create order from Kiosk

**Expected Behavior:**
- Socket disconnects gracefully
- ConnectionStatus badge: 🔴 Red "No Signal"
- Order saves to IndexedDB (no crash)
- Kitchen Display falls back to HTTP Polling

**Recovery Test:**
1. Restart Local Server: `npm start`
2. Wait 5 seconds

**Expected Behavior:**
- Auto-reconnect
- Badge: 🟢 Green or 🟡 Yellow
- Orders start appearing again

### 7.5 Browser Refresh with Pending Orders

**Test:**
1. Create 3 orders offline
2. Verify "Pending Orders: 3"
3. Refresh browser (F5)

**Expected Behavior:**
- IndexedDB persists across refresh
- After reload, ConnectionStatus shows: "Pending Orders: 3"
- Orders still in sync queue
- Auto-sync resumes

### 7.6 Multiple Kitchen Displays (Same Outlet)

**Test:**
1. Open Kitchen Display in 2 browser windows
2. Both subscribe to same outlet
3. Create order from Kiosk

**Expected Behavior:**
- **Both** Kitchen Displays receive order via Socket.IO
- No duplicate orders (each window filters correctly)
- Both display same data
- Room-based broadcasting working

✅ **Checkpoint:** System handles edge cases without crashes or data loss.

---

## 🎯 Phase 8: Performance Validation

### 8.1 Latency Testing

**HTTP Polling:**
- Expected: 0-10 seconds (average: 5 seconds)
- Test: Create order, measure time until Kitchen Display shows it
- Acceptable: ≤ 10 seconds

**Socket.IO (Local):**
- Expected: < 100ms
- Test: Create order, measure time with DevTools Performance tab
- Acceptable: ≤ 200ms

**Socket.IO (Central):**
- Expected: < 500ms (depends on internet)
- Test: Create order, measure latency
- Acceptable: ≤ 1 second

### 8.2 Sync Performance

**Test:**
- Create 50 orders offline
- Measure sync time

**Expected:**
- 50 orders sync in < 60 seconds
- Average: 1-2 seconds per order
- No timeouts or failures

### 8.3 Memory Usage

**Test:**
1. Open Kitchen Display
2. Let run for 1 hour with orders coming in
3. Check DevTools → Memory tab

**Expected:**
- No memory leaks
- Memory usage stable (< 200MB)
- No continuous growth

### 8.4 CPU Usage

**Test:**
1. Monitor Task Manager during heavy load
2. Create 20 orders in 1 minute

**Expected:**
- CPU usage spikes during sync
- Returns to normal (< 5%) when idle
- No continuous high CPU

✅ **Checkpoint:** Performance meets targets.

---

## ✅ Test Sign-Off Checklist

### Core Functionality
- [ ] Local Sync Server starts and responds to health checks
- [ ] Network detection auto-switches online/offline
- [ ] Orders save to IndexedDB when offline
- [ ] Orders sync to Central Server when online
- [ ] Kitchen Display receives orders via Socket.IO
- [ ] Kitchen Display falls back to HTTP Polling

### Connection Modes
- [ ] Online (Dual): Central + Local sockets work
- [ ] Online (Local): Local socket only works
- [ ] Offline (LAN): Local socket continues working
- [ ] Disconnected: Graceful degradation to HTTP Polling

### Background Sync
- [ ] Auto-sync every 30 seconds when online
- [ ] Manual sync button works
- [ ] Priority queue processes critical items first
- [ ] Retry logic handles failures (max 5 attempts)
- [ ] Sync progress displayed correctly

### UI/UX
- [ ] ConnectionStatus badge shows correct colors
- [ ] All connection details visible
- [ ] Progress bar animates during sync
- [ ] Retry and Sync buttons functional
- [ ] Error list displays failed syncs

### Edge Cases
- [ ] Rapid online/offline switching handled
- [ ] Multiple offline orders sync correctly
- [ ] Internet dropout during sync recovers
- [ ] Local Server restart auto-reconnects
- [ ] Browser refresh persists pending orders
- [ ] Multiple Kitchen Displays receive same orders

### Performance
- [ ] HTTP Polling latency < 10s
- [ ] Socket.IO latency < 200ms
- [ ] 50 orders sync in < 60s
- [ ] No memory leaks after 1 hour
- [ ] CPU usage normal when idle

---

## 📝 Bug Reporting Template

If you find issues during testing:

```markdown
**Issue:** [Brief description]

**Environment:**
- Browser: Chrome/Edge/Firefox [version]
- OS: Windows/Mac/Linux
- Internet: Online/Offline/Unstable

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happened]

**Console Logs:**
```
[Paste relevant console logs]
```

**Screenshots:**
[Attach if applicable]

**Severity:**
- [ ] Critical (system crash, data loss)
- [ ] High (major feature broken)
- [ ] Medium (minor feature issue)
- [ ] Low (cosmetic issue)
```

---

## 🎓 Next Steps After Testing

1. **Document all test results** in `test-results.md`
2. **Fix critical and high-severity bugs**
3. **Create staff training video** (5-10 minutes)
4. **Prepare deployment checklist**
5. **Schedule pilot deployment** (1 store)
6. **Monitor for 1 week**
7. **Rollout to remaining stores**

---

**Testing Complete? Congratulations! 🎉**

Your Hybrid Offline-First Kitchen Display System is production-ready!
