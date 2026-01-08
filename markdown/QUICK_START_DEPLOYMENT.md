# 🚀 Quick Start Deployment Guide - Offline-First Kitchen Display

**Target Audience:** System Administrators, IT Staff, Store Managers

**Estimated Setup Time:** 30-45 minutes per store

---

## 📋 Pre-Deployment Checklist

### Hardware Requirements (Per Store)

**Local Server (Choose One):**

✅ **Option 1: Mini PC (Recommended)**
- Intel NUC / HP ProDesk / Dell OptiPlex Micro
- CPU: Intel i3 or better
- RAM: 8GB minimum
- Storage: 128GB SSD minimum
- Ports: Ethernet, USB 3.0
- Cost: ~Rp 3,500,000

✅ **Option 2: Raspberry Pi 4 (Budget)**
- Raspberry Pi 4 Model B (8GB RAM)
- MicroSD Card 64GB (Class 10)
- Official Power Supply (5V 3A)
- Ethernet cable
- Case with cooling fan
- Cost: ~Rp 1,700,000

**Network Equipment:**
- ✅ Router/Switch with available LAN ports
- ✅ UPS (400VA minimum) for power backup
- ✅ Cat6 Ethernet cables
- ✅ Internet connection (10 Mbps minimum for sync)

**Kiosk & Kitchen Display:**
- ✅ Touchscreen display or tablet (existing)
- ✅ Connected to same LAN network

### Software Requirements

- ✅ Node.js 18+ (for Local Server)
- ✅ Docker & Docker Compose (for Central Server)
- ✅ Git (for code updates)
- ✅ Browser: Chrome/Edge latest version

---

## 🏗️ Part 1: Central Server Setup (One-Time, HQ/Cloud)

### Step 1.1: Deploy Backend (Django + PostgreSQL)

```bash
# Clone repository
git clone https://github.com/dadinjaenudin/kiosk-svelte.git
cd kiosk-svelte

# Start Docker containers
docker-compose up -d

# Check containers running
docker-compose ps

# Expected output:
# kiosk_pos_backend   (port 8001)
# kiosk_pos_frontend  (port 5174)
# postgres            (port 5432)
# redis               (port 6379)
```

### Step 1.2: Run Database Migrations

```bash
# Enter backend container
docker exec -it kiosk_pos_backend bash

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed test data (optional)
python setup_complete_test_data.py

# Exit container
exit
```

### Step 1.3: Verify Backend API

```bash
# Test health endpoint
curl http://localhost:8001/api/health/

# Expected: {"status": "ok"}

# Test admin panel
# Open browser: http://localhost:8001/admin/
# Login with superuser credentials
```

✅ **Checkpoint:** Central Server is running and accessible.

---

## 🏪 Part 2: Local Server Setup (Per Store)

### Step 2.1: Prepare Local Server Hardware

**For Mini PC:**
1. Install Windows 10/11 or Ubuntu 22.04 LTS
2. Connect to store LAN via Ethernet
3. Assign static IP (e.g., 192.168.1.100)
4. Install Node.js 18+: https://nodejs.org/

**For Raspberry Pi:**
1. Flash Raspberry Pi OS Lite (64-bit)
2. Configure static IP in `/etc/dhcpcd.conf`
3. Install Node.js:
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### Step 2.2: Clone Repository on Local Server

```bash
# Clone to local server
git clone https://github.com/dadinjaenudin/kiosk-svelte.git
cd kiosk-svelte/local-sync-server

# Install dependencies
npm install

# Test run
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
```

Press `Ctrl+C` to stop for now.

### Step 2.3: Build Executable (Windows)

**For Windows Production:**

```bash
# Build .exe file
npm run build:win

# Check output
dir dist

# Should see: kitchen-sync-server-win.exe (~39 MB)
```

### Step 2.4: Install as Windows Service (Auto-Start)

```bash
# Run installation script (as Administrator)
# Right-click PowerShell → Run as Administrator
cd D:\kiosk-svelte\local-sync-server
.\INSTALL_AUTOSTART_EXE.bat

# Follow prompts
```

**Manual Installation (Alternative):**

1. Open Task Scheduler
2. Create Basic Task:
   - Name: `Kitchen Sync Server`
   - Trigger: `At startup`
   - Action: `Start a program`
   - Program: `D:\kiosk-svelte\local-sync-server\dist\kitchen-sync-server-win.exe`
3. Properties → General:
   - Check: "Run whether user is logged on or not"
   - Check: "Run with highest privileges"
4. Properties → Settings:
   - Check: "Run task as soon as possible after a scheduled start is missed"

### Step 2.5: Verify Local Server

```bash
# Test health check (from any device on LAN)
curl http://192.168.1.100:3001/health

# Expected Response:
{
  "status": "ok",
  "timestamp": "2026-01-09T...",
  "connections": 0,
  "rooms": {},
  "uptime": 12.345
}
```

**From Browser:**
- Navigate to: `http://192.168.1.100:3001/health`
- Should see JSON response

✅ **Checkpoint:** Local Server running and accessible on LAN.

---

## 🖥️ Part 3: Frontend Configuration

### Step 3.1: Update Environment Variables

**File:** `frontend/.env`

```bash
# Production environment
PUBLIC_API_URL=http://YOUR_CENTRAL_SERVER_IP:8001/api
PUBLIC_LOCAL_SOCKET_URL=ws://192.168.1.100:3001

# Example for cloud deployment:
# PUBLIC_API_URL=https://api.yogya-kiosk.com/api
# PUBLIC_LOCAL_SOCKET_URL=ws://192.168.1.100:3001
```

### Step 3.2: Build Frontend

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Preview build
npm run preview
```

### Step 3.3: Deploy Frontend

**Option A: Docker (Recommended)**
```bash
# Already running via docker-compose
# Access at: http://localhost:5174
```

**Option B: Static Hosting (Nginx/Apache)**
```bash
# Copy build output
cp -r frontend/build /var/www/kiosk-frontend

# Configure Nginx
# /etc/nginx/sites-available/kiosk
server {
    listen 80;
    server_name kiosk.yourstore.com;
    root /var/www/kiosk-frontend;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8001;
    }
}
```

✅ **Checkpoint:** Frontend accessible and configured.

---

## 🧪 Part 4: Testing Deployment

### Test 4.1: Network Detection

1. Open Kitchen Display: `http://YOUR_FRONTEND/kitchen`
2. Check top-right ConnectionStatus widget
3. Should show: 🟢 Green "Online (Central + Local)"

### Test 4.2: Create Test Order (Online)

1. Open Kiosk: `http://YOUR_FRONTEND/kiosk`
2. Add products to cart
3. Complete checkout
4. Check Kitchen Display → order appears within 10 seconds

**Verify:**
- Order in Kitchen Display
- Console logs show: `📦 Socket: New order received`
- Central Server has order in database

### Test 4.3: Offline Mode Simulation

1. Disconnect internet on Local Server
2. Wait 5 seconds
3. ConnectionStatus should show: 🟡 Yellow "Offline (LAN Mode)"
4. Create order from Kiosk
5. Order should:
   - Save to IndexedDB
   - Appear on Kitchen Display via Local Socket
   - Show "Pending Orders: 1" in ConnectionStatus

### Test 4.4: Auto-Sync Recovery

1. Reconnect internet
2. Wait 30 seconds (auto-sync interval)
3. ConnectionStatus should show:
   - "Syncing... X%"
   - "All Orders Synced Successfully"
   - Badge changes to 🟢 Green

**Verify:**
- Order now in Central Server database
- IndexedDB queue empty
- Kitchen Display still shows order

### Test 4.5: Local Server Restart

1. Stop Local Server: `Ctrl+C` or restart service
2. Kitchen Display shows: 🔴 Red "No Signal"
3. Start Local Server again
4. Within 5 seconds, badge should reconnect: 🟢 or 🟡

✅ **Checkpoint:** All modes tested and working.

---

## 📱 Part 5: Kiosk & Kitchen Display Setup

### Kiosk Configuration

1. **Open Kiosk Page:**
   - URL: `http://YOUR_FRONTEND/kiosk`
   - First time: Shows setup screen

2. **Configure Store:**
   - Enter Store Code (e.g., `YOGYA-KAPATIHAN`)
   - Select Tenant
   - System loads outlets for that store
   - Configuration saved to localStorage

3. **Enable Fullscreen (Optional):**
   - Press F11 for fullscreen mode
   - Or configure browser kiosk mode

### Kitchen Display Configuration

1. **Open Kitchen Display:**
   - URL: `http://YOUR_FRONTEND/kitchen`
   - Or direct: `http://YOUR_FRONTEND/kitchen?outlet=1&tenant=1`

2. **Select Filters:**
   - Outlet: Choose brand (e.g., Chicken Sumo)
   - Tenant: Choose store (e.g., YOGYA)
   - Kitchen Station: Choose station or "All Stations"

3. **Enable WebSocket Mode:**
   - Check "WebSocket Mode" toggle
   - Enables real-time updates

4. **Verify ConnectionStatus:**
   - Top-right widget visible
   - Badge showing connection status
   - Details expanded (can toggle compact mode)

### Browser Kiosk Mode (Auto-Start)

**Windows:**

1. Create shortcut with:
```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --kiosk --app=http://YOUR_FRONTEND/kiosk
```

2. Place in Startup folder:
   - `Win+R` → `shell:startup`
   - Copy shortcut

**Linux:**

1. Edit autostart:
```bash
nano ~/.config/autostart/kiosk.desktop
```

2. Content:
```
[Desktop Entry]
Type=Application
Name=Kiosk
Exec=chromium-browser --kiosk --app=http://YOUR_FRONTEND/kiosk
```

✅ **Checkpoint:** Kiosk and Kitchen Display configured for production use.

---

## 🔧 Part 6: Monitoring & Maintenance

### Daily Checks

**Morning Checklist (5 minutes):**
- [ ] Check Local Server running: `http://192.168.1.100:3001/health`
- [ ] Check ConnectionStatus badge: Should be 🟢 Green
- [ ] Test 1 order: Kiosk → Kitchen Display
- [ ] Check pending orders: Should be 0

### Weekly Maintenance

**Every Monday (15 minutes):**
- [ ] Review Local Server logs:
```bash
# Windows: Check Event Viewer → Application Logs
# Linux: journalctl -u kitchen-sync-server -n 100
```

- [ ] Check sync queue size:
  - Open ConnectionStatus
  - Should show: "Sync Queue: 0 items"

- [ ] Clear old IndexedDB data:
  - F12 → Application → IndexedDB
  - Delete orders older than 7 days (optional)

- [ ] Restart Local Server (if needed):
```bash
# Windows: Restart service via Task Scheduler
# Linux: sudo systemctl restart kitchen-sync-server
```

### Monthly Maintenance

**First Saturday of Month (30 minutes):**
- [ ] Update software:
```bash
# Pull latest code
git pull origin main

# Rebuild Local Server
npm run build:win

# Replace exe in startup
```

- [ ] Check disk space:
```bash
# Should have > 20% free
df -h  # Linux
# Or check "This PC" → Properties (Windows)
```

- [ ] Backup configuration:
```bash
# Export kitchen config from localStorage
# F12 → Application → Local Storage → Copy "kitchen-config"
```

- [ ] Test disaster recovery:
  - Simulate internet outage (unplug for 5 min)
  - Create 3 orders
  - Reconnect → verify auto-sync

### Monitoring Dashboard (Optional)

**Setup Grafana/Prometheus:**
1. Monitor Local Server health
2. Track sync queue size
3. Alert on connection failures
4. Dashboard showing:
   - Orders per hour
   - Sync success rate
   - Network uptime
   - Local Server CPU/Memory

---

## 🚨 Troubleshooting Common Issues

### Issue 1: Orders Not Syncing

**Symptoms:**
- ConnectionStatus shows: "Pending Orders: X" (not decreasing)
- Badge: 🟡 Yellow

**Diagnosis:**
1. Check internet connection: `ping google.com`
2. Check Central Server: `curl http://YOUR_CENTRAL_SERVER/api/health`
3. Check browser console for errors

**Solution:**
- Wait for auto-sync (30s interval)
- Click "Retry" button
- Check sync errors in ConnectionStatus
- Verify X-Tenant-ID header in network requests

### Issue 2: Kitchen Display Not Receiving Orders

**Symptoms:**
- Orders created but Kitchen Display empty
- No console logs

**Diagnosis:**
1. Check Local Server running: `curl http://192.168.1.100:3001/health`
2. Check WebSocket connection in DevTools → Network → WS
3. Check outlet/tenant filters

**Solution:**
- Restart Local Server
- Verify outlet ID matches in Kiosk and Kitchen Display
- Check firewall not blocking port 3001
- Enable WebSocket Mode toggle

### Issue 3: Local Server Won't Start

**Symptoms:**
- Error: "Port 3001 already in use"

**Diagnosis:**
```bash
# Windows
netstat -ano | findstr :3001

# Linux
sudo lsof -i :3001
```

**Solution:**
- Kill process using port 3001
- Or change port in server.js (line 16)
- Restart service

### Issue 4: Badge Always Red 🔴

**Symptoms:**
- ConnectionStatus: "No Signal"
- Orders not appearing

**Diagnosis:**
1. Check Local Server status
2. Check network connectivity (LAN)
3. Check browser console for errors

**Solution:**
- Restart Local Server
- Check static IP not changed
- Verify no network restrictions
- Update LOCAL_SOCKET_URL in .env

### Issue 5: High Sync Queue (100+ items)

**Symptoms:**
- "Sync Queue: 100+ items"
- Slow sync performance

**Diagnosis:**
- Long internet outage accumulated orders
- Sync service not running
- API rate limiting

**Solution:**
- Let auto-sync run (may take 10-15 minutes)
- Check Central Server capacity
- Manually trigger sync in batches
- Clear very old items (>7 days)

---

## 📞 Support Contacts

**Technical Support:**
- Email: support@yogya-kiosk.com
- Phone: +62 XXX XXXX XXXX
- Hours: 08:00 - 17:00 WIB (Mon-Sat)

**Emergency (After Hours):**
- On-call: +62 XXX XXXX XXXX
- WhatsApp Group: [Link]

**Documentation:**
- GitHub Repo: https://github.com/dadinjaenudin/kiosk-svelte
- Wiki: [Link]
- Video Tutorials: [YouTube Playlist]

---

## ✅ Post-Deployment Checklist

### Day 1 (Pilot Store)
- [ ] Local Server installed and running
- [ ] Kiosk configured with correct store
- [ ] Kitchen Display receiving orders
- [ ] Offline mode tested and working
- [ ] Staff trained on ConnectionStatus widget
- [ ] Support contact numbers shared

### Week 1 (Monitoring)
- [ ] Daily checks completed
- [ ] No critical issues reported
- [ ] Sync queue consistently empty
- [ ] Kitchen staff comfortable with system
- [ ] Backup procedures documented

### Week 2 (Optimization)
- [ ] Performance metrics collected
- [ ] Bottlenecks identified and resolved
- [ ] Staff feedback incorporated
- [ ] FAQ updated based on real issues
- [ ] Rollout plan for remaining stores finalized

### Month 1 (Full Rollout)
- [ ] All stores deployed
- [ ] Monitoring dashboard active
- [ ] Maintenance schedule followed
- [ ] Disaster recovery tested
- [ ] Documentation complete and accurate

---

## 🎓 Staff Training Checklist

### Kitchen Staff (10 minutes)

**What They Need to Know:**
1. ✅ How to read ConnectionStatus badge:
   - 🟢 Green = Normal (everything working)
   - 🟡 Yellow = Offline Mode (LAN only, still works)
   - 🔴 Red = Problem (call IT support)

2. ✅ What to do if badge is Red:
   - Note the time
   - Check if Local Server computer is on
   - Call IT support
   - Orders may appear slower (HTTP Polling fallback)

3. ✅ Normal operations:
   - Orders appear automatically
   - Move orders between columns (Pending → Preparing → Ready)
   - Mark orders as completed

**Training Script:**
```
"The badge in top-right shows connection status:
- Green = Internet working, fastest updates
- Yellow = Internet down, but LAN still works, orders come through
- Red = Problem, call IT

Even if Yellow or Red, you can still cook orders that appear.
System is designed to work offline!"
```

### Cashier/POS Staff (5 minutes)

**What They Need to Know:**
1. ✅ System works offline (customers won't notice)
2. ✅ Orders automatically sync when internet returns
3. ✅ If something feels slow, check ConnectionStatus
4. ✅ If badge is Red, note time and call IT

**Training Script:**
```
"If internet goes down during busy hours:
- DON'T PANIC - system keeps working
- Orders save locally and sync later
- Customers won't notice any difference
- Kitchen still gets orders via local network

Just continue taking orders normally!"
```

---

## 🎉 Deployment Complete!

**Congratulations!** Your Hybrid Offline-First Kitchen Display System is now live.

**Key Benefits Achieved:**
- ✅ Zero downtime during internet outages
- ✅ Orders never lost
- ✅ Kitchen Display always responsive
- ✅ Automatic recovery when online
- ✅ Real-time updates via LAN

**Next Steps:**
1. Monitor for first week
2. Collect staff feedback
3. Refine based on real-world usage
4. Rollout to additional stores
5. Consider future enhancements (PWA, advanced analytics)

**Need Help?**
- Check [TESTING_GUIDE_OFFLINE_FIRST.md](./TESTING_GUIDE_OFFLINE_FIRST.md)
- Review [MULTI_OUTLET_KIOSK_IMPLEMENTATION.md](./MULTI_OUTLET_KIOSK_IMPLEMENTATION.md)
- Contact technical support

**Happy Deployment! 🚀**
