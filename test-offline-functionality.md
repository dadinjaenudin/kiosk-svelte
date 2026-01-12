# 🧪 Offline Functionality Testing Guide

**Date:** 2026-01-12  
**Testing:** Service Worker, Master Data Cache, Offline Orders

---

## 📋 Test Checklist

### ✅ Pre-Testing Setup
- [x] Dev server running: http://localhost:5173
- [ ] Browser DevTools open (F12)
- [ ] Application tab visible
- [ ] Network tab available
- [ ] Console tab for logs

---

## 🧪 Test 1: Service Worker Registration

### Steps:
1. Open: http://localhost:5173/kiosk
2. Open DevTools → Application → Service Workers
3. Check for registered service worker

### Expected Results:
```
✅ Service worker status: Activated and running
✅ Source: /service-worker.js
✅ Scope: /
✅ Console log: "Service Worker: Activated"
```

### How to Check:
```javascript
// In browser console:
navigator.serviceWorker.getRegistration().then(reg => {
  console.log('Service Worker:', reg?.active?.state);
});
```

---

## 🧪 Test 2: Master Data Caching

### Steps:
1. Open: http://localhost:5173/kiosk
2. Open DevTools → Application → IndexedDB
3. Check for `kiosk_master_data` database

### Expected Results:
```
✅ Database: kiosk_master_data exists
✅ Stores: products, categories, promotions, metadata
✅ Console log: "📦 Master Data Service: Initializing..."
✅ Console log: "💾 Loading master data from cache..."
✅ Console log: "✅ Master data initialized"
```

### How to Check:
```javascript
// In browser console:
const dbs = await indexedDB.databases();
console.log('Databases:', dbs.map(db => db.name));

// Check master data service state
window.masterDataState = {};
// Check console for logs
```

---

## 🧪 Test 3: Cache Storage (PWA Assets)

### Steps:
1. DevTools → Application → Cache Storage
2. Expand all cache entries

### Expected Results:
```
✅ workbox-precache-v2-* (33 entries)
   - /, /kiosk, /kitchen routes
   - CSS, JS bundles
   - Images, fonts

✅ api-cache (if online)
   - /api/public/products/
   - /api/public/categories/
   - /api/public/promotions/

✅ master-data-cache
   - Static master data responses
```

---

## 🧪 Test 4: Kiosk Offline Mode

### Steps:
1. **Online First:** Open http://localhost:5173/kiosk
2. Wait for page to load completely
3. **Go Offline:**
   - DevTools → Network tab
   - Select "Offline" from throttling dropdown
   - OR disable network in Application → Service Workers
4. **Refresh page** (Ctrl+R or F5)
5. **Test interactions:**
   - Browse menu items
   - Select products
   - Add to cart
   - Attempt to create order

### Expected Results:
```
✅ Page loads from cache (instant load)
✅ Menu items visible (from master data cache)
✅ Categories loaded
✅ Can add items to cart
✅ Can create order (stored locally)
✅ Sync button shows pending orders count
✅ No blank screens or errors
✅ Console: "📴 Offline: Using cached data"
```

### How to Test:
```javascript
// Check offline detection
console.log('Online:', navigator.onLine);

// Check pending orders
const db = await indexedDB.open('kiosk_offline_orders');
// Check orders store count
```

---

## 🧪 Test 5: Kitchen Offline Mode

### Steps:
1. **Online First:** Open http://localhost:5173/kitchen
2. Wait for page to load
3. **Go Offline:** DevTools → Network → Offline
4. **Refresh page**
5. **Test interactions:**
   - View existing orders (if any cached)
   - Try to update order status

### Expected Results:
```
✅ Page loads from cache
✅ Kitchen interface visible
✅ Shows message if no cached orders
✅ Status updates queued (if service supports)
✅ No blank screens
```

---

## 🧪 Test 6: Offline Order Creation & Storage

### Steps:
1. **Go Offline:** Network → Offline
2. **Create Order in Kiosk:**
   - Add 2-3 products to cart
   - Fill customer info (optional)
   - Click "Place Order" or submit
3. **Check IndexedDB:**
   - DevTools → Application → IndexedDB
   - Open `kiosk_offline_orders` database
   - Check `orders` store

### Expected Results:
```
✅ Order saved to IndexedDB
✅ Order has ULID (unique ID)
✅ Order status: "pending" or "pending_sync"
✅ Order timestamp: correct
✅ Order items: complete with prices (snapshot)
✅ Console: "💾 Order saved offline: [ULID]"
✅ Sync button badge: shows "1" (pending count)
```

### How to Check:
```javascript
// In browser console:
const db = await indexedDB.open('kiosk_offline_orders', 1);
const tx = db.transaction('orders', 'readonly');
const store = tx.objectStore('orders');
const orders = await store.getAll();
console.log('Pending orders:', orders);
```

---

## 🧪 Test 7: Background Sync (When Back Online)

### Steps:
1. **Create offline orders** (from Test 6)
2. **Go back online:**
   - DevTools → Network → No throttling
   - OR re-enable network
3. **Wait or trigger sync:**
   - Click sync button in UI
   - OR wait for automatic sync
4. **Check results:**
   - Monitor Network tab for POST requests
   - Check IndexedDB for removed orders
   - Check backend for received orders

### Expected Results:
```
✅ Sync button activated
✅ Network request: POST /api/orders/ (for each pending order)
✅ Order sent with correct data
✅ Response: 201 Created
✅ Order removed from IndexedDB
✅ Sync button badge: shows "0"
✅ Console: "✅ Order synced: [ULID]"
✅ Console: "🎉 All pending orders synced"
```

### How to Check:
```javascript
// Watch network requests
// DevTools → Network → Filter: "Fetch/XHR"
// Look for POST /api/orders/

// Check remaining pending orders
const db = await indexedDB.open('kiosk_offline_orders', 1);
const tx = db.transaction('orders', 'readonly');
const count = await tx.objectStore('orders').count();
console.log('Pending orders:', count); // Should be 0
```

---

## 🧪 Test 8: Cache Staleness Detection

### Steps:
1. **Check current cache time:**
   - DevTools → Application → IndexedDB
   - Open `kiosk_master_data` → `metadata` store
   - Find `last_sync_time` entry
2. **Simulate stale cache** (optional):
   - Modify `last_sync_time` to 2 days ago
   - OR wait 24+ hours (not practical)
3. **Refresh app:**
   - Check console for staleness warning

### Expected Results:
```
✅ If cache < 24 hours: No warning
⚠️  If cache > 24 hours: 
   - Console: "⚠️ Cache is stale (>24 hours old)"
   - masterData.isStale = true
   - UI shows warning (if implemented)
```

---

## 🧪 Test 9: Background Refresh (Master Data)

### Steps:
1. Open kiosk app
2. Keep tab open for 1+ hour
3. Monitor console for background refresh logs

### Expected Results:
```
After 1 hour:
✅ Console: "⏰ Background refresh triggered"
✅ Console: "🔄 Syncing master data..."
✅ Network: Requests to /api/public/products/?since_version=X
✅ Console: "✅ Sync complete: X products, Y categories, Z promotions updated"
✅ No UI interruption (silent update)
```

**Note:** To test faster, modify REFRESH_INTERVAL in masterDataService.ts:
```typescript
const REFRESH_INTERVAL = 60 * 1000; // 1 minute for testing
```

---

## 🧪 Test 10: Incremental Updates

### Steps:
1. **Load app with cached data**
2. **In backend:** Add/modify a product
3. **In app:** Wait for background refresh OR trigger manual sync
4. **Check Network tab:** Look at API request

### Expected Results:
```
✅ Request includes version parameter:
   GET /api/public/products/?since_version=42&is_available=true

✅ Response only includes changed products:
   {
     results: [/* only modified products */],
     current_version: 43
   }

✅ IndexedDB updated with new data
✅ UI reflects changes (reactive)
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Service Worker Not Registering
**Symptoms:** No service worker in Application tab
**Solutions:**
- Check console for registration errors
- Ensure HTTPS or localhost (service workers require secure context)
- Clear cache and reload: Ctrl+Shift+R
- Check service-worker.ts for syntax errors

### Issue 2: Master Data Not Caching
**Symptoms:** No kiosk_master_data database
**Solutions:**
- Check console for initialization errors
- Verify masterDataService.init() is called in +layout.svelte
- Check network tab: Are API requests succeeding?
- Check IndexedDB permissions (not blocked by browser)

### Issue 3: Offline Orders Not Saving
**Symptoms:** Orders disappear when offline
**Solutions:**
- Check console for errors during order creation
- Verify kiosk_offline_orders database exists
- Check orderService initialization
- Verify ULID generation is working

### Issue 4: Background Sync Not Working
**Symptoms:** Orders stay in IndexedDB when online
**Solutions:**
- Check sync button functionality
- Verify network status detection (navigator.onLine)
- Check API endpoint is correct and accessible
- Look for network errors in console
- Verify service worker sync event handler

### Issue 5: Stale Cache Warning Not Showing
**Symptoms:** Old data showing without warning
**Solutions:**
- Check isCacheStale() logic in masterDataDB.ts
- Verify last_sync_time is being saved correctly
- Check CACHE_STALE_THRESHOLD constant (24 hours)
- Ensure isStale flag is propagated to UI

---

## 📊 Testing Results Template

### Test Session: [Date/Time]
**Environment:**
- Browser: Chrome/Firefox/Safari [Version]
- OS: Windows/Mac/Linux
- Network: WiFi/Mobile/Offline

**Results:**

| Test | Status | Notes |
|------|--------|-------|
| Service Worker Registration | ✅/❌ | |
| Master Data Caching | ✅/❌ | |
| Cache Storage | ✅/❌ | |
| Kiosk Offline Mode | ✅/❌ | |
| Kitchen Offline Mode | ✅/❌ | |
| Offline Order Creation | ✅/❌ | |
| Background Sync | ✅/❌ | |
| Cache Staleness | ✅/❌ | |
| Background Refresh | ✅/❌ | |
| Incremental Updates | ✅/❌ | |

**Issues Found:**
1. [Issue description]
2. [Issue description]

**Performance:**
- Initial load (online): [X]ms
- Cached load (offline): [X]ms
- Sync time: [X]ms

---

## 🚀 Quick Test Script

Run this in browser console for quick validation:

```javascript
// Quick offline test
(async function testOffline() {
  console.log('🧪 Starting offline functionality test...\n');
  
  // 1. Check service worker
  const sw = await navigator.serviceWorker.getRegistration();
  console.log('✅ Service Worker:', sw?.active?.state || '❌ Not registered');
  
  // 2. Check IndexedDB databases
  const dbs = await indexedDB.databases();
  const dbNames = dbs.map(db => db.name);
  console.log('✅ Databases:', dbNames);
  console.log('   Master data:', dbNames.includes('kiosk_master_data') ? '✅' : '❌');
  console.log('   Offline orders:', dbNames.includes('kiosk_offline_orders') ? '✅' : '❌');
  
  // 3. Check cache storage
  const cacheNames = await caches.keys();
  console.log('✅ Caches:', cacheNames.length, 'found');
  cacheNames.forEach(name => console.log('   -', name));
  
  // 4. Check network status
  console.log('✅ Online status:', navigator.onLine ? 'Online' : 'Offline');
  
  // 5. Check pending orders
  try {
    const db = await indexedDB.open('kiosk_offline_orders', 1);
    const tx = db.transaction('orders', 'readonly');
    const count = await tx.objectStore('orders').count();
    console.log('✅ Pending orders:', count);
  } catch (e) {
    console.log('⚠️  Could not check orders:', e.message);
  }
  
  // 6. Check master data cache
  try {
    const db = await indexedDB.open('kiosk_master_data', 1);
    const tx = db.transaction(['products', 'categories', 'promotions'], 'readonly');
    const productsCount = await tx.objectStore('products').count();
    const categoriesCount = await tx.objectStore('categories').count();
    const promotionsCount = await tx.objectStore('promotions').count();
    console.log('✅ Master data:');
    console.log('   Products:', productsCount);
    console.log('   Categories:', categoriesCount);
    console.log('   Promotions:', promotionsCount);
  } catch (e) {
    console.log('⚠️  Could not check master data:', e.message);
  }
  
  console.log('\n✅ Test complete!');
})();
```

---

## 📝 Manual Testing Checklist

Print this and check off as you test:

### Initial Setup
- [ ] Dev server running
- [ ] Browser DevTools open
- [ ] Cleared previous cache (if needed)

### Service Worker
- [ ] Service worker registered
- [ ] Service worker activated
- [ ] Console shows activation log

### Master Data
- [ ] Database created
- [ ] Products cached
- [ ] Categories cached
- [ ] Promotions cached
- [ ] Last sync time recorded

### Offline - Kiosk
- [ ] Page loads offline
- [ ] Menu visible
- [ ] Can browse products
- [ ] Can add to cart
- [ ] Can create order
- [ ] Order saved to IndexedDB
- [ ] Sync badge shows count

### Offline - Kitchen
- [ ] Page loads offline
- [ ] Kitchen UI visible
- [ ] Shows appropriate message

### Online Sync
- [ ] Sync button works
- [ ] Orders sent to backend
- [ ] Orders removed from IndexedDB
- [ ] Badge updated to 0
- [ ] Success message shown

### Long-term
- [ ] Background refresh works
- [ ] Stale cache detected
- [ ] Incremental updates efficient

---

**Happy Testing! 🎉**
