# 🔄 Kitchen Sync Server

Local network **Socket.IO** server untuk komunikasi real-time antara POS dan Kitchen Display saat offline (tanpa internet).

## 📋 Fitur

- ✅ **Socket.IO** untuk reliable WebSocket connections
- ✅ **Room-based broadcasting** per outlet
- ✅ **Auto-reconnect** jika koneksi terputus
- ✅ HTTP health check & statistics endpoints
- ✅ Package sebagai standalone executable (.exe)
- ✅ Tidak perlu Node.js di production
- ✅ Auto-start on Windows boot (optional)
- ✅ Support multiple outlets dengan room isolation

## 🚀 Quick Start

### 1️⃣ Development Mode (dengan Node.js)

```bash
# Install dependencies
npm install

# Start server
npm start
```

Server akan berjalan di:
- **WebSocket**: `ws://localhost:3001`
- **Socket.IO**: `http://localhost:3001` 
- **Health Check**: `http://localhost:3001/health`
- **Outlet Stats**: `http://localhost:3001/outlets`

### 2️⃣ Production Mode - EXE (Recommended ✅)

**PALING MUDAH - One-Click Install:**

1. **Right-click** `BUILD_AND_INSTALL.bat`
2. **Select** "Run as Administrator"
3. **Wait** ~2 menit (npm install + build + install auto-start)
4. **Done!** Server otomatis jalan saat Windows boot

**Script ini akan:**
- ✅ Install dependencies (npm install)
- ✅ Build .exe file (~39 MB)
- ✅ Install auto-start ke Windows Task Scheduler
- ✅ Start server di background

**File yang dihasilkan:**
- `dist/kitchen-sync-server-win.exe` - Standalone executable
- Auto-start configured - Jalan otomatis saat boot

### 3️⃣ Manual Build & Install

#### Opsi A: Build + Install Auto-Start

```bash
# 1. Install dependencies
npm install

# 2. Build executable
npm run build:win

# 3. Install auto-start (Right-click as Administrator)
INSTALL_AUTOSTART_EXE.bat
```

#### Opsi B: Build untuk Development

```bash
# Build Windows executable
npm run build:win

# Output: dist/kitchen-sync-server-win.exe (~39 MB)
```

#### Opsi C: Build Semua Platform

```bash
# Build untuk Windows, Mac, dan Linux
npm run build:all

# Output:
# - dist/kitchen-sync-server-win.exe (Windows)
# - dist/kitchen-sync-server-mac (macOS)
# - dist/kitchen-sync-server-linux (Linux)
```

### 4️⃣ Manual Start / Testing

**Start Server (will use .exe if available, otherwise Node.js):**
```bash
# Double-click atau run:
START_KITCHEN_SYNC.bat
```

**Start in Background (Windows):**
```bash
# Right-click as Administrator:
INSTALL_AUTOSTART_EXE.bat
```

### 5️⃣ Uninstall Auto-Start

```bash
# Right-click as Administrator:
UNINSTALL_AUTOSTART.bat
```

### 6️⃣ Deploy ke Production (Store/Outlet)

**Cara 1: Copy Folder Lengkap**
```
local-sync-server/
├── dist/
│   └── kitchen-sync-server-win.exe
├── BUILD_AND_INSTALL.bat          ← Run this as Admin
├── START_KITCHEN_SYNC.bat
├── INSTALL_AUTOSTART_EXE.bat
└── UNINSTALL_AUTOSTART.bat
```

**Cara 2: Copy Hanya EXE + Scripts**
```
local-sync-server/
├── dist/
│   └── kitchen-sync-server-win.exe (~39 MB)
├── START_KITCHEN_SYNC.bat
└── INSTALL_AUTOSTART_EXE.bat
```

**Di PC Toko:**
1. Copy folder ke `C:\KitchenSync\` atau lokasi lain
2. Right-click `INSTALL_AUTOSTART_EXE.bat` → Run as Administrator
3. Done! Server otomatis jalan

2. **Double-click** `START_KITCHEN_SYNC.bat`

3. **Done!** Server running di background

#### Optional: Auto-Start on Boot

1. **Right-click** `INSTALL_AUTOSTART.bat`
2. **Run as Administrator**
3. Server akan auto-start setiap Windows boot

## 🔧 Scripts

| Script | Keterangan |
|--------|------------|
| `npm start` | Start server (development) |
| `npm run build:win` | Build executable untuk Windows |
| `npm run build:mac` | Build executable untuk macOS |
| `npm run build:linux` | Build executable untuk Linux |
| `npm run build:all` | Build untuk semua platform |

## 📁 Batch Files

| File | Keterangan |
|------|------------|
| `START_KITCHEN_SYNC.bat` | Double-click untuk start server |
| `CHECK_KITCHEN_SYNC.bat` | Cek status server (health check) |
| `INSTALL_AUTOSTART.bat` | Install auto-start on boot (admin) |

## 🌐 Network Configuration

Server ini berjalan di **Local Network (LAN)** dan tidak memerlukan internet.

**IP Configuration:**
- Pastikan POS dan Kitchen Display terhubung ke network yang sama
- POS akan broadcast order ke `ws://<SERVER_IP>:3001`
- Kitchen akan listen ke `ws://<SERVER_IP>:3001`

**Firewall Settings:**
Jika ada firewall, allow ports:
- `3001` (WebSocket)
- `3002` (HTTP/Health Check)

## 🧪 Testing

### Test Health Check

```bash
curl http://localhost:3002/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2026-01-04T10:30:00.000Z",
  "connections": 2,
  "rooms": {
    "outlet_1": 2
  },
  "uptime": 123.456
}
```

### Test Outlet Statistics

```bash
curl http://localhost:3002/outlets
```

Expected response:
```json
{
  "outlets": [
    {
      "outletId": "1",
      "connections": 2,
      "clients": [
        {
          "socketId": "abc123",
          "type": "pos",
          "connectedAt": "2026-01-04T10:30:00.000Z"
        },
        {
          "socketId": "def456",
          "type": "kitchen",
          "connectedAt": "2026-01-04T10:31:00.000Z"
        }
      ]
    }
  ]
}
```

### Test Socket.IO Connection (Frontend)

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:3002', {
  transports: ['websocket', 'polling']
});

socket.on('connect', () => {
  console.log('✅ Connected:', socket.id);
  
  // Subscribe to outlet
  socket.emit('subscribe_outlet', 1);
  
  // Identify as POS or Kitchen
  socket.emit('identify', { type: 'pos' });
});

socket.on('subscribed', (data) => {
  console.log('📍 Subscribed to outlet:', data.outletId);
});

// Send new order
socket.emit('new_order', {
  id: 123,
  order_number: 'ORD-001',
  outlet_id: 1,
  items: [{ name: 'Nasi Goreng', quantity: 2 }],
  total: 50000
});

// Listen for order updates
socket.on('order_created', (order) => {
  console.log('📦 New order:', order);
});

socket.on('order_updated', (update) => {
  console.log('🔄 Order updated:', update);
});
```

## 📊 Socket.IO Events

### Client → Server

| Event | Payload | Description |
|-------|---------|-------------|
| `subscribe_outlet` | `outletId: number` | Join outlet-specific room |
| `identify` | `{ type: 'pos' \| 'kitchen' }` | Identify client type |
| `new_order` | `Order` object | Broadcast new order |
| `update_status` | `{ id, order_number, outlet_id, status }` | Update order status |
| `complete_order` | `{ id, order_number, outlet_id }` | Mark order completed |
| `cancel_order` | `{ id, order_number, outlet_id }` | Cancel order |
| `broadcast` | `any` | Generic broadcast to outlet |

### Server → Client

| Event | Payload | Description |
|-------|---------|-------------|
| `connected` | `{ message, socketId, timestamp }` | Connection established |
| `subscribed` | `{ outletId, timestamp }` | Successfully subscribed to outlet |
| `order_created` | `Order` object | New order broadcasted |
| `order_updated` | `{ id, status, timestamp }` | Order status updated |
| `order_completed` | `{ id, order_number }` | Order completed |
| `order_cancelled` | `{ id, order_number }` | Order cancelled |
| `order_sent` | `{ orderId, timestamp }` | Acknowledgment |
| `status_updated` | `{ orderId, timestamp }` | Acknowledgment |
| `message` | `any` | Generic message |

## 📊 Architecture

```
┌─────────────┐                    ┌──────────────────┐                    ┌─────────────┐
│  POS Kiosk  │                    │  Sync Server     │                    │   Kitchen   │
│  (Svelte)   │◄──────────────────►│  (Socket.IO)     │◄──────────────────►│  Display    │
│             │   Socket.IO        │  Node.js         │   Socket.IO        │  (Svelte)   │
│  Checkout   │   Port 3002        │  Port 3002       │   Port 3002        │  Receives   │
│  Broadcast  │                    │                  │                    │  Orders     │
└─────────────┘                    └──────────────────┘                    └─────────────┘
       │                                    │                                      │
       │                                    │                                      │
       └────── outlet_1 room ───────────────┴──────────────────────────────────────┘
                (isolated broadcast)

                                            │
                                            │ HTTP Endpoints
                                            │ /health, /outlets
                                            ▼
                                   ┌─────────────────┐
                                   │  Monitoring     │
                                   │  (Optional)     │
                                   └─────────────────┘
```

### Room-Based Broadcasting

Each outlet has its own room (`outlet_1`, `outlet_2`, etc.):
- Orders from Outlet 1 only go to Kitchen Display subscribed to Outlet 1
- Complete isolation between outlets
- Scalable to hundreds of outlets

## 🔐 Security Notes

- Server hanya listen di local network (tidak exposed ke internet)
- Tidak ada authentication (asumsi trusted local network)
- Untuk production dengan security requirement, tambahkan:
  - JWT token authentication
  - TLS/SSL encryption (wss://)
  - IP whitelist

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Windows: Check port usage
netstat -ano | findstr :3002

# Kill process
taskkill /PID <PID> /F
```

### Firewall Blocking

```bash
# Windows: Allow port (run as Admin)
netsh advfirewall firewall add rule name="Kitchen Sync" dir=in action=allow protocol=TCP localport=3002
```

### Cannot Connect from Other PC

1. Check server IP: `ipconfig`
2. Update POS/Kitchen to use server IP instead of `localhost`
3. Test connection: `curl http://<SERVER_IP>:3002/health`

## 📝 Logs

Server logs akan ditampilkan di console:

```
✅ WebSocket Server: ws://localhost:3001
✅ HTTP Server:      http://localhost:3002
╔════════════════════════════════════════════════════════════╗
║     Kitchen Sync Server - RUNNING                          ║
║     Socket.IO + Express                                    ║
╚════════════════════════════════════════════════════════════╝

✅ Socket.IO Server: http://localhost:3002
✅ WebSocket Path:   ws://localhost:3002/socket.io/
✅ Health Check:     http://localhost:3002/health
✅ Outlet Stats:     http://localhost:3002/outlets

📡 Waiting for connections from POS and Kitchen displays...

Events Supported:
  - subscribe_outlet  : Join outlet-specific room
  - new_order        : Broadcast new order to kitchen
  - update_status    : Update order status
  - complete_order   : Mark order as completed
  - cancel_order     : Cancel order

[2026-01-04T10:30:00.000Z] ✅ New connection: abc123 from 192.168.1.100
[2026-01-04T10:30:05.000Z] 📍 abc123 subscribed to outlet_1
[2026-01-04T10:30:10.000Z] 🏷️  abc123 identified as pos
[2026-01-04T10:31:00.000Z] 📦 New order #ORD-001 from outlet 1
[2026-01-04T10:32:00.000Z] 🔄 Order #ORD-001 status: preparing
[2026-01-04T10:35:00.000Z] ✅ Order #ORD-001 completed
## 📚 Related Documentation

- [OFFLINE_KITCHEN_SOLUTION.md](../markdown/OFFLINE_KITCHEN_SOLUTION.md) - Complete offline solution guide
- [OFFLINE_FIRST_IMPLEMENTATION.md](../markdown/OFFLINE_FIRST_IMPLEMENTATION.md) - Kiosk offline-first architecture

## 📞 Support

Untuk pertanyaan atau issue, buka issue di repository atau contact team developer.

---

**Version**: 1.0.0  
**Last Updated**: January 3, 2026  
**Tested On**: Windows 11, Node.js 18.x
