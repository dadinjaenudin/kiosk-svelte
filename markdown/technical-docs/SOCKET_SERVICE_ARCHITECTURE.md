# Socket Service Architecture

## ⚠️ CRITICAL: Centralized Socket Management

**DO NOT create manual socket connections in components!**

### Architecture Rules

#### ✅ CORRECT: Use socketService
```typescript
// In any component (kiosk, kitchen, admin, etc.)
import { socketService, socketStatus } from '$lib/services/socketService';

onMount(async () => {
  // Connect to Local Sync Server (LAN)
  await socketService.connectLocal();
  
  // Connect to Central Server (Internet)
  await socketService.connectCentral();
  
  // Setup event listeners
  socketService.onLocal('order:created:offline', (data) => {
    console.log('Offline order received:', data);
  });
  
  socketService.onCentral('new_order', (data) => {
    console.log('New order from central:', data);
  });
});

// Emit events
socketService.emitToLocal('event-name', data);
socketService.emitToCentral('event-name', data);

// Check connection status
$: localConnected = $socketStatus.localConnected;
$: centralConnected = $socketStatus.centralConnected;
$: mode = $socketStatus.mode; // 'none' | 'local' | 'central' | 'dual'
```

#### ❌ WRONG: Manual socket.io connection
```typescript
// ❌ DO NOT DO THIS!
import { io, Socket } from 'socket.io-client';

let socket: Socket | null = null;

function initSocket() {
  socket = io('http://localhost:3001', { ... });
  socket.on('connect', () => { ... });
  socket.on('disconnect', () => { ... });
}
```

### Why Centralized Socket Management?

1. **Single Source of Truth**
   - ConnectionStatus widget dapat menampilkan status yang akurat
   - Semua component melihat connection state yang sama
   - Tidak ada duplicate connections

2. **Consistent Behavior**
   - Auto-reconnect logic terpusat
   - Error handling uniform
   - Connection lifecycle managed di satu tempat

3. **Easy Debugging**
   - Semua socket logs di satu service
   - Status tracking di Svelte store
   - Tidak ada hidden socket connections

4. **Performance**
   - Tidak ada duplicate connections ke same server
   - Connection pooling otomatis
   - Memory efficient

### Socket Service API

#### Connection Methods
```typescript
// Connect to Local Sync Server (port 3001)
await socketService.connectLocal();

// Connect to Central Server (port 8001)
await socketService.connectCentral();

// Disconnect
socketService.disconnectLocal();
socketService.disconnectCentral();
```

#### Event Listeners
```typescript
// Listen to Local Sync Server events
socketService.onLocal('event-name', (data) => { ... });

// Listen to Central Server events
socketService.onCentral('event-name', (data) => { ... });
```

#### Emit Events
```typescript
// Emit to Local Sync Server
socketService.emitToLocal('event-name', data);

// Emit to Central Server
socketService.emitToCentral('event-name', data);
```

#### Connection Status (Svelte Store)
```typescript
import { socketStatus } from '$lib/services/socketService';

// Subscribe to status
$: {
  console.log('Local:', $socketStatus.localConnected);
  console.log('Central:', $socketStatus.centralConnected);
  console.log('Mode:', $socketStatus.mode);
}
```

### Event Naming Convention

#### Local Sync Server Events (LAN)
- `order:created:offline` - Kiosk broadcast offline order
- `order:synced` - Order berhasil sync ke backend
- `join-kitchen` - Kitchen display join room

#### Central Server Events (Internet)
- `new_order` - New order dari backend
- `order_updated` - Order status updated
- `join-kitchen` - Kitchen display join room

### Components Using socketService

#### ✅ Kiosk Layout (`frontend/src/routes/kiosk/+layout.svelte`)
```typescript
onMount(async () => {
  await socketService.connectLocal();
  await socketService.connectCentral();
});
```

#### ✅ Kitchen Display (`frontend/src/routes/kitchen/display/+page.svelte`)
```typescript
onMount(async () => {
  await socketService.connectLocal();
  await socketService.connectCentral();
  
  setupSocketListeners();
  
  socketService.emitToLocal('join-kitchen', { outletId, deviceId });
  socketService.emitToCentral('join-kitchen', { outletId, deviceId });
});

function setupSocketListeners() {
  socketService.onLocal('order:created:offline', handleOfflineOrder);
  socketService.onLocal('order:synced', handleOrderSynced);
  socketService.onCentral('new_order', handleNewOrder);
  socketService.onCentral('order_updated', handleOrderUpdated);
}
```

#### ✅ Connection Status Widget (`frontend/src/lib/components/ConnectionStatus.svelte`)
```typescript
import { socketStatus } from '$lib/services/socketService';

$: socketMode = $socketStatus.mode;
$: localConnected = $socketStatus.localConnected;
$: centralConnected = $socketStatus.centralConnected;
```

### Offline Mode Flow

1. **Kiosk creates offline order**
   - Saved to IndexedDB
   - Broadcast via `socketService.emitToLocal('order:created:offline', data)`

2. **Kitchen Display receives broadcast**
   - Listener: `socketService.onLocal('order:created:offline', ...)`
   - Display yellow card with "📴 Pending Sync"

3. **Order synced to backend**
   - Kiosk emits: `socketService.emitToLocal('order:synced', data)`
   - Kitchen removes yellow card, fetches normal order from backend

### Troubleshooting

#### Socket: None in ConnectionStatus
**Cause**: Component not using socketService or not connected
**Fix**: 
```typescript
// Make sure component calls:
await socketService.connectLocal();
await socketService.connectCentral();
```

#### Offline orders not showing in Kitchen Display
**Cause**: Kitchen Display tidak connect ke Local Sync Server
**Fix**: 
```typescript
// Kitchen Display must connect to Local Sync Server:
await socketService.connectLocal();
socketService.onLocal('order:created:offline', handleOfflineOrder);
```

#### Duplicate socket connections
**Cause**: Component creating manual socket instead of using socketService
**Fix**: Remove manual `io()` calls, use `socketService` instead

### Testing Checklist

- [ ] ConnectionStatus shows correct socket mode (Local/Central/Dual)
- [ ] Kiosk can broadcast offline orders
- [ ] Kitchen Display receives offline order broadcasts
- [ ] Yellow offline order cards appear in Kitchen Display
- [ ] Offline orders disappear after sync
- [ ] No duplicate socket connections in browser DevTools
- [ ] Console logs show socket events from socketService

### Files Modified (January 2026)

1. **frontend/src/routes/kitchen/display/+page.svelte**
   - ❌ Removed: Manual `io()` connection and `initSocket()`
   - ✅ Added: `socketService.connectLocal()` and `socketService.connectCentral()`
   - ✅ Added: `setupSocketListeners()` using socketService event handlers

2. **frontend/src/routes/kiosk/checkout/+page.svelte**
   - ✅ Added: `socketService.emitToLocal('order:created:offline', data)`

3. **frontend/src/lib/services/socketService.ts**
   - ✅ Added: `emitToLocal()` and `emitToCentral()` methods
   - ✅ Added: `onLocal()` and `onCentral()` event listener methods

### References

- Socket Service: `frontend/src/lib/services/socketService.ts`
- Local Sync Server: `local-sync-server/server.js`
- Offline Mode: `markdown/technical-docs/OFFLINE_FIRST_IMPLEMENTATION.md`
- Kitchen Station: `markdown/KITCHEN_STATION_TYPE_RELATIONSHIP.md`

---

**Last Updated**: January 10, 2026  
**Author**: Development Team  
**Status**: ✅ Production Ready
