/**
 * Kitchen Sync Server - Local Network Socket.IO Server
 * Handles real-time order synchronization between POS and Kitchen displays
 * when internet is unavailable (offline-first architecture)
 * 
 * Features:
 * - Socket.IO for reliable WebSocket connections
 * - Room-based broadcasting (per outlet)
 * - Automatic reconnection support
 * - SQLite persistent storage (survives restart/power loss)
 * - Health check endpoint
 * - HTTP polling fallback
 * 
 * Version: 2.0.0 (SQLite + ULID)
 * Date: 2026-01-11
 */

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const Database = require('better-sqlite3');
const { ulid } = require('ulid');
const fs = require('fs');
const path = require('path');

const HTTP_PORT = 3001;

// ============================================================================
// SQLite Database Setup (PERSISTENT STORAGE - NO DATA LOSS)
// ============================================================================

// Ensure directories exist
const dataDir = path.join(__dirname, 'data');
const backupDir = path.join(__dirname, 'backups');

if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
  console.log('📁 Created data directory');
}

if (!fs.existsSync(backupDir)) {
  fs.mkdirSync(backupDir, { recursive: true });
  console.log('📁 Created backups directory');
}

// Initialize SQLite database
const dbPath = path.join(dataDir, 'local-sync.db');
const db = new Database(dbPath, {
  verbose: (msg) => console.log(`[SQLite] ${msg}`)
});

console.log(`📦 Opening database: ${dbPath}`);

// Configure SQLite for optimal performance
db.pragma('journal_mode = WAL');        // Write-Ahead Logging (crash-safe)
db.pragma('synchronous = NORMAL');      // Balance safety vs speed
db.pragma('cache_size = -64000');       // 64MB cache
db.pragma('temp_store = MEMORY');       // Use memory for temp tables
db.pragma('mmap_size = 30000000000');   // Memory-mapped I/O
db.pragma('page_size = 4096');          // Standard page size

console.log('⚙️  SQLite configured with WAL mode');

// Create orders table with optimized schema
db.exec(`
  CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,                -- ULID (sortable, unique)
    outlet_id INTEGER NOT NULL,
    order_data TEXT NOT NULL,           -- JSON blob
    created_at TEXT NOT NULL,           -- ISO 8601 timestamp
    synced_to_cloud INTEGER DEFAULT 0,  -- Boolean flag
    
    -- Indexes for fast queries
    CHECK (json_valid(order_data))
  ) WITHOUT ROWID;
  
  CREATE INDEX IF NOT EXISTS idx_outlet_created 
    ON orders(outlet_id, created_at DESC);
  
  CREATE INDEX IF NOT EXISTS idx_sync_status 
    ON orders(synced_to_cloud, created_at);
`);

console.log('✅ Database schema initialized');

// Create auto-cleanup trigger (maintain max 100 orders per outlet)
db.exec(`
  CREATE TRIGGER IF NOT EXISTS cleanup_old_orders
  AFTER INSERT ON orders
  BEGIN
    DELETE FROM orders
    WHERE outlet_id = NEW.outlet_id
    AND id NOT IN (
      SELECT id FROM orders
      WHERE outlet_id = NEW.outlet_id
      ORDER BY created_at DESC
      LIMIT 100
    );
  END;
`);

console.log('🧹 Auto-cleanup trigger created');

// Prepared statements (pre-compiled for speed)
const insertOrderStmt = db.prepare(`
  INSERT OR REPLACE INTO orders (id, outlet_id, order_data, created_at, synced_to_cloud)
  VALUES (?, ?, ?, ?, ?)
`);

const selectByOutletStmt = db.prepare(`
  SELECT order_data FROM orders
  WHERE outlet_id = ?
  ORDER BY created_at DESC
  LIMIT 100
`);

const selectSinceIdStmt = db.prepare(`
  SELECT order_data FROM orders
  WHERE outlet_id = ? AND id > ?
  ORDER BY created_at DESC
  LIMIT 100
`);

const markSyncedStmt = db.prepare(`
  UPDATE orders SET synced_to_cloud = 1 WHERE id = ?
`);

const getUnsyncedStmt = db.prepare(`
  SELECT order_data FROM orders
  WHERE synced_to_cloud = 0
  ORDER BY created_at ASC
  LIMIT 50
`);

const countOrdersStmt = db.prepare(`
  SELECT COUNT(*) as count FROM orders
`);

const countUnsyncedStmt = db.prepare(`
  SELECT COUNT(*) as count FROM orders WHERE synced_to_cloud = 0
`);

const dbSizeStmt = db.prepare(`
  SELECT page_count * page_size as size 
  FROM pragma_page_count(), pragma_page_size()
`);

// Database functions
function storeOrder(order) {
  try {
    // Generate ULID if not exists
    if (!order.id) {
      order.id = ulid();
    }
    
    const orderData = JSON.stringify(order);
    const createdAt = order.created_at || new Date().toISOString();
    
    insertOrderStmt.run(
      order.id,
      order.outlet_id,
      orderData,
      createdAt,
      0 // Not synced yet
    );
    
    console.log(`💾 Order ${order.id} stored in SQLite (outlet: ${order.outlet_id})`);
    return true;
  } catch (error) {
    console.error('❌ Failed to store order:', error.message);
    return false;
  }
}

function getOrders(outletId, sinceId = null) {
  try {
    const rows = sinceId
      ? selectSinceIdStmt.all(outletId, sinceId)
      : selectByOutletStmt.all(outletId);
    
    return rows.map(row => JSON.parse(row.order_data));
  } catch (error) {
    console.error('❌ Failed to get orders:', error.message);
    return [];
  }
}

function markOrderSynced(orderId) {
  try {
    markSyncedStmt.run(orderId);
    console.log(`✅ Order ${orderId} marked as synced`);
  } catch (error) {
    console.error('❌ Failed to mark order as synced:', error.message);
  }
}

function getUnsyncedOrders() {
  try {
    const rows = getUnsyncedStmt.all();
    return rows.map(row => JSON.parse(row.order_data));
  } catch (error) {
    console.error('❌ Failed to get unsynced orders:', error.message);
    return [];
  }
}

function getDatabaseStats() {
  try {
    const totalOrders = countOrdersStmt.get().count;
    const unsyncedOrders = countUnsyncedStmt.get().count;
    const dbSizeBytes = dbSizeStmt.get().size;
    const dbSizeKB = Math.round(dbSizeBytes / 1024);
    const walEnabled = db.pragma('journal_mode', { simple: true }) === 'wal';
    
    return {
      totalOrders,
      unsyncedOrders,
      dbSizeKB,
      walEnabled
    };
  } catch (error) {
    console.error('❌ Failed to get database stats:', error.message);
    return null;
  }
}

// Auto-backup every 5 minutes
setInterval(() => {
  try {
    const timestamp = Date.now();
    const backupPath = path.join(backupDir, `local-sync-${timestamp}.db`);
    
    db.backup(backupPath)
      .then(() => {
        console.log(`✅ Backup complete: ${backupPath}`);
        
        // Keep only last 10 backups
        const backups = fs.readdirSync(backupDir)
          .filter(f => f.startsWith('local-sync-') && f.endsWith('.db'))
          .map(f => ({
            name: f,
            path: path.join(backupDir, f),
            time: fs.statSync(path.join(backupDir, f)).mtime.getTime()
          }))
          .sort((a, b) => b.time - a.time);
        
        if (backups.length > 10) {
          backups.slice(10).forEach(backup => {
            fs.unlinkSync(backup.path);
            console.log(`🗑️  Deleted old backup: ${backup.name}`);
          });
        }
      })
      .catch(err => console.error('❌ Backup failed:', err.message));
  } catch (err) {
    console.error('❌ Backup error:', err.message);
  }
}, 5 * 60 * 1000); // Every 5 minutes

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n📦 Shutting down...');
  console.log('💾 Flushing WAL to disk...');
  
  try {
    db.pragma('wal_checkpoint(TRUNCATE)'); // Flush WAL
    db.close();
    console.log('✅ Database closed safely');
  } catch (error) {
    console.error('❌ Error closing database:', error.message);
  }
  
  process.exit(0);
});

console.log('🚀 SQLite Local Sync Server initialized');
console.log('📊 Initial stats:', getDatabaseStats());

// ============================================================================
// Express App & HTTP Server
// ============================================================================

// Create Express app for HTTP endpoints
const app = express();
app.use(express.json());

// Create HTTP server
const httpServer = http.createServer(app);

// Create Socket.IO server
const io = socketIo(httpServer, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  },
  transports: ['websocket', 'polling'],
  pingTimeout: 60000, // 60 seconds before considering connection dead
  pingInterval: 25000, // Send ping every 25 seconds
  upgradeTimeout: 30000,
  maxHttpBufferSize: 1e8
});

// Store connected clients and rooms
const clients = new Map(); // socket.id -> { socket, outletId, type }
const outletRooms = new Map(); // outletId -> Set of socket.ids

// ============================================================================
// HTTP API Endpoints
// ============================================================================

// Health check endpoint (with database stats)
app.get('/health', (req, res) => {
  const roomStats = {};
  outletRooms.forEach((sockets, outletId) => {
    roomStats[`outlet_${outletId}`] = sockets.size;
  });

  const dbStats = getDatabaseStats();

  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    connections: clients.size,
    rooms: roomStats,
    uptime: process.uptime(),
    database: dbStats
  });
});

// HTTP endpoint to emit socket events (called by Django backend)
app.post('/emit', (req, res) => {
  const { event, data } = req.body;
  
  if (!event || !data) {
    return res.status(400).json({ error: 'Missing event or data' });
  }
  
  const outletId = data.outlet_id || data.tenant_id;
  
  console.log(`[${new Date().toISOString()}] 📡 HTTP emit: ${event} for outlet ${outletId}`);
  
  // Store order in SQLite (persistent storage)
  if (event === 'new_order' || event === 'order_updated') {
    storeOrder(data);
  }
  
  // Broadcast to outlet room via WebSocket
  io.to(`outlet_${outletId}`).emit(event, data);
  
  res.json({
    success: true,
    event,
    outletId,
    timestamp: new Date().toISOString()
  });
});

// Polling endpoint - Get orders from SQLite
app.get('/api/orders', (req, res) => {
  const { outlet_id, since_id } = req.query;
  
  if (!outlet_id) {
    return res.status(400).json({ error: 'Missing outlet_id parameter' });
  }

  const outletId = parseInt(outlet_id);
  const sinceId = since_id || null;

  console.log(`[${new Date().toISOString()}] 📊 Polling request: outlet ${outletId}${sinceId ? `, since_id ${sinceId}` : ''}`);

  // Get orders from SQLite
  const orders = getOrders(outletId, sinceId);

  console.log(`[${new Date().toISOString()}] 📦 Returning ${orders.length} orders`);

  res.json(orders);
});

// Mark order as synced to cloud
app.post('/api/orders/:orderId/synced', (req, res) => {
  const { orderId } = req.params;
  
  markOrderSynced(orderId);
  
  res.json({
    success: true,
    orderId,
    timestamp: new Date().toISOString()
  });
});

// Get unsynced orders (for backend sync)
app.get('/api/orders/unsynced', (req, res) => {
  const orders = getUnsyncedOrders();
  
  console.log(`[${new Date().toISOString()}] 🔄 Returning ${orders.length} unsynced orders`);
  
  res.json(orders);
});

// Get outlet statistics
app.get('/outlets', (req, res) => {
  const outlets = [];
  outletRooms.forEach((sockets, outletId) => {
    const socketInfos = [];
    sockets.forEach(socketId => {
      const client = clients.get(socketId);
      if (client) {
        socketInfos.push({
          socketId,
          type: client.type,
          connectedAt: client.connectedAt
        });
      }
    });
    outlets.push({
      outletId,
      connections: sockets.size,
      clients: socketInfos
    });
  });
  res.json({ outlets });
});

// Database stats endpoint
app.get('/api/stats', (req, res) => {
  const stats = getDatabaseStats();
  res.json(stats);
});

// ============================================================================
// Socket.IO Connection Handler
// ============================================================================
io.on('connection', (socket) => {
  const clientIp = socket.handshake.address;
  console.log(`[${new Date().toISOString()}] ✅ New connection: ${socket.id} from ${clientIp}`);
  
  // Store client info
  clients.set(socket.id, {
    socket,
    outletId: null,
    type: null,
    connectedAt: new Date().toISOString()
  });

  // Send welcome message
  socket.emit('connected', {
    message: 'Connected to Kitchen Sync Server',
    socketId: socket.id,
    timestamp: new Date().toISOString()
  });

  // Subscribe to outlet-specific room
  socket.on('subscribe_outlet', (outletId) => {
    const client = clients.get(socket.id);
    if (client) {
      client.outletId = outletId;
      socket.join(`outlet_${outletId}`);
      
      // Track outlet room
      if (!outletRooms.has(outletId)) {
        outletRooms.set(outletId, new Set());
      }
      outletRooms.get(outletId).add(socket.id);
      
      console.log(`[${new Date().toISOString()}] 📍 ${socket.id} subscribed to outlet_${outletId}`);
      
      socket.emit('subscribed', {
        outletId,
        timestamp: new Date().toISOString()
      });
    }
  });

  // Kitchen joins room (alternative to subscribe_outlet)
  socket.on('join-kitchen', (data) => {
    const { outletId, deviceId } = data;
    const client = clients.get(socket.id);
    
    if (client) {
      client.outletId = outletId;
      client.type = 'kitchen';
      client.deviceId = deviceId;
      
      socket.join(`outlet_${outletId}`);
      
      // Track outlet room
      if (!outletRooms.has(outletId)) {
        outletRooms.set(outletId, new Set());
      }
      outletRooms.get(outletId).add(socket.id);
      
      console.log(`[${new Date().toISOString()}] 🍳 Kitchen ${socket.id} joined outlet_${outletId} (device: ${deviceId})`);
      
      socket.emit('kitchen-joined', {
        outletId,
        deviceId,
        timestamp: new Date().toISOString()
      });
    }
  });

  // Identify client type (POS or Kitchen)
  socket.on('identify', (data) => {
    const client = clients.get(socket.id);
    if (client) {
      client.type = data.type; // 'pos' or 'kitchen'
      console.log(`[${new Date().toISOString()}] 🏷️  ${socket.id} identified as ${data.type}`);
    }
  });

  // Handle new order from POS
  socket.on('new_order', (message) => {
    const order = message.data || message; // Support both wrapped and direct formats
    const outletId = order.outlet_id || order.tenant_id;
    
    console.log(`[${new Date().toISOString()}] 📦 New order #${order.order_number} from outlet ${outletId}`);
    
    // Broadcast to all clients in the same outlet
    io.to(`outlet_${outletId}`).emit('order_created', order);
    
    // Send acknowledgment to sender
    socket.emit('order_sent', {
      orderId: order.id || order.order_number,
      timestamp: new Date().toISOString()
    });
  });

  // Handle offline order created (from kiosk in offline mode)
  socket.on('order:created:offline', (order) => {
    const outletId = order.checkout_data?.carts?.[0]?.outlet_id || order.store_id;
    
    console.log(`[${new Date().toISOString()}] 📴 Offline order received: ${order.order_number} for outlet ${outletId}`);
    
    // Broadcast to all kitchen displays in the same outlet
    io.to(`outlet_${outletId}`).emit('order:created:offline', order);
    
    console.log(`[${new Date().toISOString()}] ✅ Broadcasted offline order to outlet_${outletId} room`);
  });

  // Handle order status update from Kitchen
  socket.on('update_status', (message) => {
    const update = message.data || message; // Support both wrapped and direct formats
    const outletId = update.outlet_id || update.tenant_id;
    
    console.log(`[${new Date().toISOString()}] 🔄 Order #${update.order_number} status: ${update.status}`);
    
    // Broadcast to all clients in the same outlet
    io.to(`outlet_${outletId}`).emit('order_updated', update);
    
    // Send acknowledgment
    socket.emit('status_updated', {
      orderId: update.id,
      timestamp: new Date().toISOString()
    });
  });

  // Handle order completion
  socket.on('complete_order', (data) => {
    console.log(`[${new Date().toISOString()}] ✅ Order #${data.order_number} completed`);
    
    io.to(`outlet_${data.outlet_id}`).emit('order_completed', data);
  });

  // Handle order cancellation
  socket.on('cancel_order', (data) => {
    console.log(`[${new Date().toISOString()}] ❌ Order #${data.order_number} cancelled`);
    
    io.to(`outlet_${data.outlet_id}`).emit('order_cancelled', data);
  });

  // Handle generic broadcast
  socket.on('broadcast', (data) => {
    const client = clients.get(socket.id);
    if (client && client.outletId) {
      console.log(`[${new Date().toISOString()}] 📢 Broadcast to outlet ${client.outletId}`);
      socket.to(`outlet_${client.outletId}`).emit('message', data);
    }
  });

  // Handle client disconnect
  socket.on('disconnect', (reason) => {
    const client = clients.get(socket.id);
    if (client) {
      console.log(`[${new Date().toISOString()}] ❌ Client disconnected: ${socket.id} (${client.type || 'unknown'}) - Reason: ${reason}`);
      
      // Remove from outlet room
      if (client.outletId && outletRooms.has(client.outletId)) {
        outletRooms.get(client.outletId).delete(socket.id);
        if (outletRooms.get(client.outletId).size === 0) {
          outletRooms.delete(client.outletId);
        }
      }
      
      clients.delete(socket.id);
    } else {
      console.log(`[${new Date().toISOString()}] ❌ Unknown client disconnected: ${socket.id} - Reason: ${reason}`);
    }
  });

  // Handle errors
  socket.on('error', (error) => {
    console.error(`[${new Date().toISOString()}] ❌ Socket error for ${socket.id}:`, error);
  });
});

// Start HTTP server with Socket.IO
httpServer.listen(HTTP_PORT, () => {
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║     Kitchen Sync Server v2.0 - RUNNING (SQLite + ULID)    ║');
  console.log('║     Socket.IO + Express + SQLite                           ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
  console.log('');
  console.log(`✅ Socket.IO Server: http://localhost:${HTTP_PORT}`);
  console.log(`✅ WebSocket Path:   ws://localhost:${HTTP_PORT}/socket.io/`);
  console.log(`✅ Health Check:     http://localhost:${HTTP_PORT}/health`);
  console.log(`✅ Polling API:      http://localhost:${HTTP_PORT}/api/orders`);
  console.log(`✅ Database Stats:   http://localhost:${HTTP_PORT}/api/stats`);
  console.log('');
  console.log('📦 Database Configuration:');
  const stats = getDatabaseStats();
  console.log(`   - Total Orders:    ${stats.totalOrders}`);
  console.log(`   - Unsynced Orders: ${stats.unsyncedOrders}`);
  console.log(`   - Database Size:   ${stats.dbSizeKB} KB`);
  console.log(`   - WAL Mode:        ${stats.walEnabled ? 'Enabled ✅' : 'Disabled ❌'}`);
  console.log('');
  console.log('📡 Waiting for connections from POS and Kitchen displays...');
  console.log('');
  console.log('Events Supported:');
  console.log('  - subscribe_outlet  : Join outlet-specific room');
  console.log('  - new_order        : Broadcast new order to kitchen');
  console.log('  - update_status    : Update order status');
  console.log('  - complete_order   : Mark order as completed');
  console.log('  - cancel_order     : Cancel order');
  console.log('');
  console.log('Press Ctrl+C to stop the server');
  console.log('');
});

// Graceful shutdown (merged with database shutdown)
process.on('SIGINT', () => {
  console.log('\n\n🛑 Shutting down gracefully...');
  console.log('💾 Flushing WAL to disk...');
  
  // Flush WAL and close database
  try {
    db.pragma('wal_checkpoint(TRUNCATE)');
    db.close();
    console.log('✅ Database closed safely');
  } catch (error) {
    console.error('❌ Error closing database:', error.message);
  }
  
  // Disconnect all Socket.IO clients
  clients.forEach((client) => {
    client.socket.disconnect(true);
  });
  
  // Close Socket.IO server
  io.close(() => {
    console.log('✅ Socket.IO server closed');
    
    // Close HTTP server
    httpServer.close(() => {
      console.log('✅ HTTP server closed');
      console.log('👋 Goodbye!');
      process.exit(0);
    });
  });
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});
