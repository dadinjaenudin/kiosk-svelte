/**
 * Kitchen Sync Server - Local Network Socket.IO Server
 * Handles real-time order synchronization between POS and Kitchen displays
 * when internet is unavailable (offline-first architecture)
 * 
 * Features:
 * - Socket.IO for reliable WebSocket connections
 * - Room-based broadcasting (per outlet)
 * - Automatic reconnection support
 * - Health check endpoint
 */

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');

const HTTP_PORT = 3002;

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
  transports: ['websocket', 'polling']
});

// Store connected clients and rooms
const clients = new Map(); // socket.id -> { socket, outletId, type }
const outletRooms = new Map(); // outletId -> Set of socket.ids

// Health check endpoint
app.get('/health', (req, res) => {
  const roomStats = {};
  outletRooms.forEach((sockets, outletId) => {
    roomStats[`outlet_${outletId}`] = sockets.size;
  });

  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    connections: clients.size,
    rooms: roomStats,
    uptime: process.uptime()
  });
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

// Socket.IO connection handler
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

  // Identify client type (POS or Kitchen)
  socket.on('identify', (data) => {
    const client = clients.get(socket.id);
    if (client) {
      client.type = data.type; // 'pos' or 'kitchen'
      console.log(`[${new Date().toISOString()}] 🏷️  ${socket.id} identified as ${data.type}`);
    }
  });

  // Handle new order from POS
  socket.on('new_order', (order) => {
    console.log(`[${new Date().toISOString()}] 📦 New order #${order.order_number} from outlet ${order.outlet_id}`);
    
    // Broadcast to all clients in the same outlet
    io.to(`outlet_${order.outlet_id}`).emit('order_created', order);
    
    // Send acknowledgment to sender
    socket.emit('order_sent', {
      orderId: order.id,
      timestamp: new Date().toISOString()
    });
  });

  // Handle order status update from Kitchen
  socket.on('update_status', (update) => {
    console.log(`[${new Date().toISOString()}] 🔄 Order #${update.order_number} status: ${update.status}`);
    
    // Broadcast to all clients in the same outlet
    io.to(`outlet_${update.outlet_id}`).emit('order_updated', update);
    
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
  socket.on('disconnect', () => {
    const client = clients.get(socket.id);
    if (client) {
      console.log(`[${new Date().toISOString()}] ❌ Client disconnected: ${socket.id} (${client.type || 'unknown'})`);
      
      // Remove from outlet room
      if (client.outletId && outletRooms.has(client.outletId)) {
        outletRooms.get(client.outletId).delete(socket.id);
        if (outletRooms.get(client.outletId).size === 0) {
          outletRooms.delete(client.outletId);
        }
      }
      
      clients.delete(socket.id);
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
  console.log('║     Kitchen Sync Server - RUNNING                          ║');
  console.log('║     Socket.IO + Express                                    ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
  console.log('');
  console.log(`✅ Socket.IO Server: http://localhost:${HTTP_PORT}`);
  console.log(`✅ WebSocket Path:   ws://localhost:${HTTP_PORT}/socket.io/`);
  console.log(`✅ Health Check:     http://localhost:${HTTP_PORT}/health`);
  console.log(`✅ Outlet Stats:     http://localhost:${HTTP_PORT}/outlets`);
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

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n🛑 Shutting down gracefully...');
  
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
