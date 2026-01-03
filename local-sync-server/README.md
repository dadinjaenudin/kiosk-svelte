# 🔄 Kitchen Sync Server

Local network WebSocket server untuk komunikasi real-time antara POS dan Kitchen Display saat offline (tanpa internet).

## 📋 Fitur

- ✅ WebSocket server untuk broadcast order real-time
- ✅ HTTP health check endpoint
- ✅ Auto-reconnect jika koneksi terputus
- ✅ Package sebagai standalone executable (.exe)
- ✅ Tidak perlu Node.js di production
- ✅ Auto-start on Windows boot (optional)

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
- **HTTP**: `http://localhost:3002`
- **Health Check**: `http://localhost:3002/health`

### 2️⃣ Production Mode (Standalone Executable)

#### Build Executable

```bash
# Install dependencies (hanya sekali)
npm install

# Build untuk Windows
npm run build:win
```

Output: `dist/kitchen-sync-server-win.exe` (~30 MB)

#### Deploy ke Production

1. **Copy files** ke PC kasir/dapur:
   ```
   local-sync-server/
   ├── dist/
   │   └── kitchen-sync-server-win.exe
   └── START_KITCHEN_SYNC.bat
   ```

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
  "timestamp": "2026-01-03T10:30:00.000Z",
  "connections": 0,
  "uptime": 123.456
}
```

### Test WebSocket Connection

Buka browser console dan jalankan:

```javascript
const ws = new WebSocket('ws://localhost:3001');

ws.onopen = () => {
  console.log('Connected!');
  ws.send(JSON.stringify({ type: 'test', message: 'Hello' }));
};

ws.onmessage = (event) => {
  console.log('Received:', event.data);
};
```

## 📊 Architecture

```
┌─────────────┐                    ┌──────────────────┐                    ┌─────────────┐
│  POS Kiosk  │                    │  Sync Server     │                    │   Kitchen   │
│  (Svelte)   │◄──────────────────►│  (Node.js)       │◄──────────────────►│  Display    │
│             │   WebSocket        │  ws://localhost  │   WebSocket        │  (Svelte)   │
│  Checkout   │   Port 3001        │  :3001           │   Port 3001        │  Receives   │
│  Broadcast  │                    │                  │                    │  Orders     │
└─────────────┘                    └──────────────────┘                    └─────────────┘
                                            │
                                            │ HTTP Health Check
                                            │ Port 3002
                                            ▼
                                   ┌─────────────────┐
                                   │  Monitoring     │
                                   │  (Optional)     │
                                   └─────────────────┘
```

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
netstat -ano | findstr :3001
netstat -ano | findstr :3002

# Kill process
taskkill /PID <PID> /F
```

### Firewall Blocking

```bash
# Windows: Allow ports (run as Admin)
netsh advfirewall firewall add rule name="Kitchen Sync WS" dir=in action=allow protocol=TCP localport=3001
netsh advfirewall firewall add rule name="Kitchen Sync HTTP" dir=in action=allow protocol=TCP localport=3002
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
📡 Waiting for connections...

[2026-01-03T10:30:00.000Z] New connection from 192.168.1.100
[2026-01-03T10:30:05.000Z] Received: new_order
[2026-01-03T10:30:05.000Z] Client disconnected from 192.168.1.100
```

## 📚 Related Documentation

- [OFFLINE_KITCHEN_SOLUTION.md](../markdown/OFFLINE_KITCHEN_SOLUTION.md) - Complete offline solution guide
- [OFFLINE_FIRST_IMPLEMENTATION.md](../markdown/OFFLINE_FIRST_IMPLEMENTATION.md) - Kiosk offline-first architecture

## 📞 Support

Untuk pertanyaan atau issue, buka issue di repository atau contact team developer.

---

**Version**: 1.0.0  
**Last Updated**: January 3, 2026  
**Tested On**: Windows 11, Node.js 18.x
