/**
 * Kitchen Sync Server - Local Network WebSocket Server
 * Handles real-time order synchronization between POS and Kitchen displays
 * when internet is unavailable (offline-first architecture)
 */

const WebSocket = require('ws');
const express = require('express');
const http = require('http');

const WS_PORT = 3001;
const HTTP_PORT = 3002;

// Create Express app for HTTP endpoints (health check, etc.)
const app = express();
app.use(express.json());

// Create HTTP server
const httpServer = http.createServer(app);

// Create WebSocket server
const wss = new WebSocket.Server({ port: WS_PORT });

// Store connected clients
const clients = new Set();

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    connections: clients.size,
    uptime: process.uptime()
  });
});

// WebSocket connection handler
wss.on('connection', (ws, req) => {
  const clientIp = req.socket.remoteAddress;
  console.log(`[${new Date().toISOString()}] New connection from ${clientIp}`);
  
  clients.add(ws);

  // Send welcome message
  ws.send(JSON.stringify({
    type: 'connected',
    message: 'Connected to Kitchen Sync Server',
    timestamp: new Date().toISOString()
  }));

  // Handle incoming messages
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      console.log(`[${new Date().toISOString()}] Received:`, data.type);

      // Broadcast to all connected clients except sender
      clients.forEach((client) => {
        if (client !== ws && client.readyState === WebSocket.OPEN) {
          client.send(message);
        }
      });

      // Send acknowledgment to sender
      ws.send(JSON.stringify({
        type: 'ack',
        messageType: data.type,
        timestamp: new Date().toISOString()
      }));

    } catch (error) {
      console.error('Error parsing message:', error);
      ws.send(JSON.stringify({
        type: 'error',
        message: 'Invalid message format',
        timestamp: new Date().toISOString()
      }));
    }
  });

  // Handle client disconnect
  ws.on('close', () => {
    console.log(`[${new Date().toISOString()}] Client disconnected from ${clientIp}`);
    clients.delete(ws);
  });

  // Handle errors
  ws.on('error', (error) => {
    console.error(`[${new Date().toISOString()}] WebSocket error:`, error);
    clients.delete(ws);
  });
});

// Start HTTP server
httpServer.listen(HTTP_PORT, () => {
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║     Kitchen Sync Server - RUNNING                          ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
  console.log('');
  console.log(`✅ WebSocket Server: ws://localhost:${WS_PORT}`);
  console.log(`✅ HTTP Server:      http://localhost:${HTTP_PORT}`);
  console.log(`✅ Health Check:     http://localhost:${HTTP_PORT}/health`);
  console.log('');
  console.log('📡 Waiting for connections from POS and Kitchen displays...');
  console.log('');
  console.log('Press Ctrl+C to stop the server');
  console.log('');
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\n🛑 Shutting down gracefully...');
  
  // Close all WebSocket connections
  clients.forEach((client) => {
    client.close();
  });
  
  // Close WebSocket server
  wss.close(() => {
    console.log('✅ WebSocket server closed');
  });
  
  // Close HTTP server
  httpServer.close(() => {
    console.log('✅ HTTP server closed');
    console.log('👋 Goodbye!');
    process.exit(0);
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
