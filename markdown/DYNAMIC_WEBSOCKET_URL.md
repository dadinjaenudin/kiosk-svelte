# 🌐 Dynamic WebSocket URL per Outlet

**Date:** January 3, 2026  
**Feature:** Configure WebSocket URL untuk setiap outlet secara dinamis

---

## 🎯 Problem Statement

### Sebelumnya:
- WebSocket URL hardcoded: `ws://localhost:3001`
- Tidak bisa untuk multi-outlet dengan LAN berbeda
- Setiap outlet harus edit code untuk ganti IP

### Masalah Multi-Outlet:
```
Outlet A (Yogya Mall Malioboro):
  LAN: 192.168.1.x
  Kitchen Sync Server: 192.168.1.10:3001
  Problem: Hardcoded localhost tidak bisa diakses!

Outlet B (Yogya Solo):
  LAN: 192.168.2.x
  Kitchen Sync Server: 192.168.2.15:3001
  Problem: Beda jaringan, beda IP!

Outlet C (Yogya Semarang):
  LAN: 192.168.3.x
  Kitchen Sync Server: 192.168.3.20:3001
  Problem: Setiap outlet butuh custom build!
```

---

## ✅ Solusi: Dynamic WebSocket URL

Sekarang setiap outlet bisa setting WebSocket URL sendiri di **Admin Panel**.

### Architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      ADMIN PANEL                            │
│                                                             │
│  Outlet Settings:                                           │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Outlet: Yogya Mall Malioboro                        │   │
│  │ WebSocket URL: ws://192.168.1.10:3001              │   │
│  │ [Save]                                              │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Outlet: Yogya Solo                                  │   │
│  │ WebSocket URL: ws://192.168.2.15:3001              │   │
│  │ [Save]                                              │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ API: /api/tenants/outlets/{id}/
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATABASE (PostgreSQL)                      │
│                                                             │
│  outlets:                                                   │
│  ┌─────┬──────────────┬─────────────────────────────┐     │
│  │ id  │ name         │ websocket_url               │     │
│  ├─────┼──────────────┼─────────────────────────────┤     │
│  │ 1   │ Yogya Mall   │ ws://192.168.1.10:3001      │     │
│  │ 2   │ Yogya Solo   │ ws://192.168.2.15:3001      │     │
│  │ 3   │ Yogya Smg    │ ws://192.168.3.20:3001      │     │
│  └─────┴──────────────┴─────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ On Load: Fetch outlet settings
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (POS/Kitchen)                     │
│                                                             │
│  1. Load outlet settings from API                           │
│  2. Get websocket_url from settings                         │
│  3. Connect to dynamic WebSocket URL                        │
│                                                             │
│  localSync.js / kitchenSync.js:                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ const wsUrl = outletSettings?.websocket_url;       │   │
│  │ ws = new WebSocket(wsUrl);                         │   │
│  │ // Connects to: ws://192.168.1.10:3001            │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Implementation Details

### 1. Backend Changes

**Model: `apps/tenants/models.py`**
```python
class Outlet(models.Model):
    # ... existing fields ...
    
    # Network Configuration
    websocket_url = models.CharField(
        max_length=255, 
        blank=True, 
        default='ws://localhost:3001',
        help_text='WebSocket URL for Kitchen Sync Server (e.g., ws://192.168.1.10:3001)'
    )
```

**Serializer: `apps/tenants/serializers.py`**
```python
class OutletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outlet
        fields = [
            # ... existing fields ...
            'websocket_url',  # ← NEW
            # ...
        ]
```

**API Endpoint:**
```
GET  /api/tenants/outlets/{id}/
POST /api/tenants/outlets/
PUT  /api/tenants/outlets/{id}/
```

Response example:
```json
{
  "id": 1,
  "name": "Yogya Mall Malioboro",
  "websocket_url": "ws://192.168.1.10:3001",
  "address": "Jl. Malioboro No.1",
  "is_active": true
}
```

---

### 2. Frontend Changes

**File: `frontend/src/lib/stores/localSync.js`** (POS Side)
```javascript
import { writable, get } from 'svelte/store';

export const outletSettings = writable(null);

// Load outlet settings
export async function loadOutletSettings(outletId) {
  const response = await fetch(`/api/tenants/outlets/${outletId}/`);
  const data = await response.json();
  outletSettings.set(data);
  return data;
}

// Get dynamic WebSocket URL
function getWebSocketURL() {
  const settings = get(outletSettings);
  return settings?.websocket_url || 'ws://localhost:3001';
}

// Connect using dynamic URL
export function connectToSyncServer() {
  const SYNC_SERVER_URL = getWebSocketURL(); // ← Dynamic!
  ws = new WebSocket(SYNC_SERVER_URL);
  // ...
}
```

**File: `frontend/src/lib/stores/kitchenSync.js`** (Kitchen Side)
```javascript
// Same implementation as localSync.js
export async function loadOutletSettings(outletId) {
  // Fetch outlet settings including websocket_url
}

function getWebSocketURL() {
  return outletSettings?.websocket_url || 'ws://localhost:3001';
}
```

---

### 3. Admin Panel Changes

**File: `admin/src/routes/outlets/+page.svelte`**

Added form field:
```html
<!-- WebSocket Configuration -->
<div>
  <label for="outlet-websocket" class="form-label">
    WebSocket URL
    <span class="text-xs text-gray-500 ml-2">(Kitchen Sync Server)</span>
  </label>
  <input
    id="outlet-websocket"
    type="text"
    bind:value={outletForm.websocket_url}
    class="form-input"
    placeholder="ws://192.168.1.10:3001"
  />
  <p class="text-xs text-gray-500 mt-1">
    Example: ws://192.168.1.10:3001 (use local network IP for multi-outlet)
  </p>
</div>
```

---

## 📋 Usage Guide

### Step 1: Setup Kitchen Sync Server per Outlet

**Outlet A - Yogya Mall:**
```bash
# Install Kitchen Sync Server di PC/Server outlet
# IP LAN: 192.168.1.10
cd local-sync-server
START_KITCHEN_SYNC.bat

# Server running on:
# - WebSocket: ws://192.168.1.10:3001
# - Health Check: http://192.168.1.10:3002/health
```

**Outlet B - Yogya Solo:**
```bash
# Install di PC/Server outlet Solo
# IP LAN: 192.168.2.15
cd local-sync-server
START_KITCHEN_SYNC.bat

# Server running on:
# - WebSocket: ws://192.168.2.15:3001
# - Health Check: http://192.168.2.15:3002/health
```

---

### Step 2: Configure Outlet Settings di Admin

1. Login ke Admin Panel: `http://localhost:5173/admin`
2. Menu: **Settings → Outlets**
3. Edit outlet **"Yogya Mall Malioboro"**
4. Set **WebSocket URL**: `ws://192.168.1.10:3001`
5. Save

Repeat untuk setiap outlet dengan IP masing-masing.

---

### Step 3: Frontend Auto-Load Settings

**Di POS/Kiosk:**
```javascript
// On page load
import { loadOutletSettings, connectToSyncServer } from '$lib/stores/localSync';

onMount(async () => {
  const outletId = getOutletIdFromUrl(); // atau dari localStorage
  await loadOutletSettings(outletId);
  connectToSyncServer(); // Automatically uses outlet's websocket_url
});
```

**Di Kitchen Display:**
```javascript
import { loadOutletSettings, connectToSyncServer } from '$lib/stores/kitchenSync';

onMount(async () => {
  const outletId = getOutletIdFromUrl();
  await loadOutletSettings(outletId);
  connectToSyncServer(); // Connects to outlet-specific WebSocket server
});
```

---

## 🎯 Benefits

### ✅ Advantages:

1. **No Code Changes**
   - Tidak perlu rebuild frontend untuk setiap outlet
   - Cukup configure di admin panel

2. **Centralized Management**
   - Manage semua outlet WebSocket URL di 1 tempat
   - Easy to update jika IP berubah

3. **Multi-Outlet Ready**
   - Setiap outlet punya Kitchen Sync Server sendiri
   - Isolated network per outlet

4. **Flexible Deployment**
   - Development: `ws://localhost:3001`
   - Staging: `ws://192.168.1.10:3001`
   - Production: `ws://10.20.30.40:3001`

5. **Backward Compatible**
   - Default: `ws://localhost:3001` (tetap works untuk single outlet)
   - Upgrade path smooth

---

## 🔐 Security Considerations

### Network Security:

1. **WebSocket Server Access**
   ```
   ✅ ALLOWED: Same LAN only (192.168.x.x)
   ❌ BLOCKED: Public internet access
   ```

2. **Firewall Rules**
   ```bash
   # Allow port 3001 hanya dari LAN
   netsh advfirewall firewall add rule ^
     name="Kitchen Sync - LAN Only" ^
     dir=in action=allow protocol=TCP ^
     localport=3001 ^
     remoteip=192.168.0.0/16,172.16.0.0/12,10.0.0.0/8
   ```

3. **Database Security**
   - WebSocket URL stored in database
   - Only accessible by authenticated admin users
   - No public API endpoint

---

## 🧪 Testing

### Test Dynamic WebSocket URL:

**1. Update outlet settings:**
```bash
# Via Admin UI atau API
curl -X PATCH http://localhost:8000/api/tenants/outlets/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "websocket_url": "ws://192.168.1.99:3001"
  }'
```

**2. Reload POS/Kitchen:**
```bash
# Open browser console
# Check connection logs:
# [LocalSync] Outlet settings loaded: {outlet: "Yogya Mall", websocket_url: "ws://192.168.1.99:3001"}
# [LocalSync] Using WebSocket URL: ws://192.168.1.99:3001
# [LocalSync] Connecting to ws://192.168.1.99:3001...
# [LocalSync] ✅ Connected to Kitchen Sync Server
```

**3. Test order broadcast:**
```bash
# Create order di kiosk
# Check kitchen display receives order
# Verify using correct WebSocket server
```

---

## 📊 Migration Path

### For Existing Installations:

**1. Database Migration (AUTO):**
```bash
docker exec -it kiosk_pos_backend python manage.py migrate
# Adds websocket_url column with default: ws://localhost:3001
```

**2. Update Existing Outlets (OPTIONAL):**
```sql
-- If you want custom URLs for existing outlets
UPDATE outlets 
SET websocket_url = 'ws://192.168.1.10:3001' 
WHERE name = 'Yogya Mall Malioboro';

UPDATE outlets 
SET websocket_url = 'ws://192.168.2.15:3001' 
WHERE name = 'Yogya Solo';
```

**3. Frontend Auto-Upgrade:**
- No code changes needed
- Will use default `ws://localhost:3001` if not configured
- Works immediately after backend migration

---

## 🚀 Deployment Checklist

### Per Outlet Setup:

- [ ] Install Kitchen Sync Server di PC/server outlet
- [ ] Note down LAN IP address (e.g., 192.168.1.10)
- [ ] Configure firewall allow port 3001
- [ ] Test server: `curl http://192.168.1.10:3002/health`
- [ ] Login admin panel
- [ ] Update outlet websocket_url: `ws://192.168.1.10:3001`
- [ ] Test POS connection
- [ ] Test Kitchen Display connection
- [ ] Test order broadcast end-to-end

---

## 🐛 Troubleshooting

### Issue: Connection refused

**Symptom:**
```
[LocalSync] ❌ WebSocket error: Error: connect ECONNREFUSED
```

**Solution:**
1. Check Kitchen Sync Server running:
   ```bash
   curl http://192.168.1.10:3002/health
   ```

2. Verify WebSocket URL correct di admin
3. Check firewall allows port 3001
4. Test from POS machine:
   ```bash
   ping 192.168.1.10
   telnet 192.168.1.10 3001
   ```

---

### Issue: Using wrong WebSocket server

**Symptom:**
```
[LocalSync] Using WebSocket URL: ws://localhost:3001
# But outlet configured with ws://192.168.1.10:3001
```

**Solution:**
1. Clear browser cache
2. Reload page (hard refresh: Ctrl+F5)
3. Check outletId parameter correct
4. Verify API returns correct websocket_url

---

## 📝 Summary

**What Changed:**
- ✅ Added `websocket_url` field to Outlet model
- ✅ Frontend loads WebSocket URL from outlet settings (dynamic)
- ✅ Admin panel dapat configure WebSocket URL per outlet
- ✅ Backward compatible (default: localhost)

**Why It Matters:**
- Multi-outlet dengan LAN berbeda sekarang supported
- No code changes untuk deploy ke outlet baru
- Centralized configuration di admin panel
- Scalable untuk unlimited outlets

**Next Steps:**
- Configure WebSocket URL untuk setiap outlet
- Test end-to-end di production network
- Monitor WebSocket connection logs
- Update deployment documentation per outlet

---

**Status:** ✅ IMPLEMENTED & TESTED
**Date:** January 3, 2026
**Version:** 2.0.0
