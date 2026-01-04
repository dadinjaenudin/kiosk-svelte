# 🚀 BUILD & INSTALL KITCHEN SYNC SERVER

## 📋 Ringkasan Cara Build & Install

### ✅ Cara Paling Mudah (ONE-CLICK)

**Right-click** `BUILD_AND_INSTALL.bat` → **Run as Administrator**

Script ini akan otomatis:
1. Install dependencies (npm install)
2. Build executable (npm run build:win)
3. Install auto-start ke Windows Task Scheduler
4. Start server di background

**Selesai!** Server akan jalan otomatis setiap Windows boot.

---

## 📦 File yang Dihasilkan

```
local-sync-server/
├── dist/
│   └── kitchen-sync-server-win.exe    (~39 MB) ✅
│
└── Scheduled Task: "Kitchen Sync Server" ✅
```

---

## 🛠️ Manual Build (Step by Step)

### 1. Install Dependencies

```bash
npm install
```

### 2. Build Executable

```bash
npm run build:win
```

Output: `dist/kitchen-sync-server-win.exe` (~39 MB)

### 3. Install Auto-Start

**Right-click as Administrator:**
```
INSTALL_AUTOSTART_EXE.bat
```

---

## 🎯 Deploy ke Production (Toko/Store)

### Opsi 1: Copy Folder Lengkap

**Copy folder ini ke PC toko:**
```
local-sync-server/
├── dist/
│   └── kitchen-sync-server-win.exe
├── BUILD_AND_INSTALL.bat
├── START_KITCHEN_SYNC.bat
├── INSTALL_AUTOSTART_EXE.bat
└── UNINSTALL_AUTOSTART.bat
```

**Di PC Toko:**
- Right-click `BUILD_AND_INSTALL.bat` → Run as Administrator
- Atau right-click `INSTALL_AUTOSTART_EXE.bat` → Run as Administrator

### Opsi 2: Copy Hanya EXE

**Minimal files untuk deploy:**
```
local-sync-server/
├── dist/
│   └── kitchen-sync-server-win.exe    (~39 MB)
├── START_KITCHEN_SYNC.bat
└── INSTALL_AUTOSTART_EXE.bat
```

**Di PC Toko:**
1. Copy ke `C:\KitchenSync\` atau lokasi lain
2. Right-click `INSTALL_AUTOSTART_EXE.bat` → Run as Administrator
3. Done!

---

## 🔧 Perintah Management

### Start Server Manual

```bash
# Double-click:
START_KITCHEN_SYNC.bat

# Atau via command:
dist\kitchen-sync-server-win.exe
```

### Check Server Status

```powershell
# Check process
tasklist | findstr "kitchen-sync-server-win.exe"

# Check port
netstat -ano | findstr ":3001"

# Test health endpoint
curl http://localhost:3001/health
```

### Stop Server

```powershell
# Stop executable
taskkill /F /IM kitchen-sync-server-win.exe
```

### View Scheduled Task

```powershell
# View details
schtasks /query /tn "Kitchen Sync Server" /fo LIST /v

# Run task manually
schtasks /run /tn "Kitchen Sync Server"

# Delete task
schtasks /delete /tn "Kitchen Sync Server" /f
```

### Uninstall Auto-Start

```bash
# Right-click as Administrator:
UNINSTALL_AUTOSTART.bat
```

---

## 🌐 Network Setup

**Port yang digunakan:**
- **3001** - WebSocket Server (ws://localhost:3001)

**Firewall:**
- Allow inbound port 3001 TCP
- Allow program: `kitchen-sync-server-win.exe`

**LAN Setup:**
- POS dan Kitchen Display harus di network yang sama
- POS broadcast ke: `ws://<SERVER_IP>:3001`
- Kitchen listen dari: `ws://<SERVER_IP>:3001`

---

## ✅ Verification

**Server berhasil jalan jika:**

1. ✅ Process running:
   ```
   tasklist | findstr "kitchen-sync-server-win.exe"
   ```

2. ✅ Port listening:
   ```
   netstat -ano | findstr ":3001"
   ```

3. ✅ Health check OK:
   ```
   curl http://localhost:3001/health
   ```
   Response:
   ```json
   {
     "status": "ok",
     "timestamp": "2026-01-04T...",
     "connections": 0,
     "rooms": {},
     "uptime": 12.34
   }
   ```

4. ✅ Scheduled task exists:
   ```
   schtasks /query /tn "Kitchen Sync Server"
   ```

---

## 🐛 Troubleshooting

### Problem: Port 3001 already in use

**Solution:**
```powershell
# Find process using port 3001
netstat -ano | findstr ":3001"

# Kill process (replace PID with actual PID)
taskkill /F /PID <PID>
```

### Problem: Executable not found

**Solution:**
```bash
# Build executable first
npm run build:win

# Check if file exists
dir dist\kitchen-sync-server-win.exe
```

### Problem: Auto-start not working

**Solution:**
```powershell
# Check scheduled task
schtasks /query /tn "Kitchen Sync Server" /fo LIST /v

# Delete and recreate
schtasks /delete /tn "Kitchen Sync Server" /f

# Reinstall
# Right-click INSTALL_AUTOSTART_EXE.bat as Administrator
```

### Problem: Server crashes on start

**Check logs:**
- Task Scheduler → Task Scheduler Library → "Kitchen Sync Server"
- Right-click → Properties → History tab

---

## 📚 Additional Resources

- **README.md** - Full documentation
- **server.js** - Source code
- **package.json** - Build configuration

---

## 🎉 Success!

Jika semua langkah berhasil:
- ✅ Server auto-start setiap Windows boot
- ✅ No Node.js required (standalone .exe)
- ✅ Berjalan di background
- ✅ Ready untuk production

**Test dengan:**
1. Restart PC
2. Check process: `tasklist | findstr "kitchen-sync-server-win.exe"`
3. Test health: `curl http://localhost:3001/health`

**Server siap digunakan!** 🚀
