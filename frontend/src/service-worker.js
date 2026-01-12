/**
 * Service Worker with Workbox
 * 
 * Features:
 * - Background Sync for failed order submissions
 * - Offline caching strategies
 * - Static asset caching
 * - API request caching with NetworkFirst
 */

import { precacheAndRoute } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import { NetworkFirst, CacheFirst, StaleWhileRevalidate } from 'workbox-strategies';
import { BackgroundSyncPlugin } from 'workbox-background-sync';
import { CacheableResponsePlugin } from 'workbox-cacheable-response';
import { ExpirationPlugin } from 'workbox-expiration';

// Precache all assets from build
precacheAndRoute(self.__WB_MANIFEST);

console.log('[Service Worker] Loaded');

// Background Sync Plugin for failed order submissions
const bgSyncPlugin = new BackgroundSyncPlugin('order-sync-queue', {
  maxRetentionTime: 24 * 60, // Retry for max of 24 Hours (in minutes)
  onSync: async ({ queue }) => {
    console.log('[Background Sync] Replaying queued requests...');
    let entry;
    while ((entry = await queue.shiftRequest())) {
      try {
        await fetch(entry.request.clone());
        console.log('[Background Sync] Request succeeded:', entry.request.url);
      } catch (error) {
        console.error('[Background Sync] Request failed:', entry.request.url, error);
        // Re-queue if still failing
        await queue.unshiftRequest(entry);
        throw error;
      }
    }
    console.log('[Background Sync] Queue replayed successfully');
  }
});

// API Routes - NetworkFirst strategy (try network, fallback to cache)
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/'),
  new NetworkFirst({
    cacheName: 'api-cache',
    plugins: [
      new CacheableResponsePlugin({
        statuses: [0, 200],
      }),
      new ExpirationPlugin({
        maxEntries: 100,
        maxAgeSeconds: 5 * 60, // 5 minutes
      }),
    ],
  })
);

// Order submission with Background Sync
registerRoute(
  ({ url, request }) => 
    url.pathname.includes('/api/orders/order-groups/') && 
    request.method === 'POST',
  new NetworkFirst({
    cacheName: 'order-submissions',
    plugins: [
      bgSyncPlugin,
      new CacheableResponsePlugin({
        statuses: [0, 200, 201],
      }),
    ],
  })
);

// Master Data (products, categories) - StaleWhileRevalidate
registerRoute(
  ({ url }) => 
    url.pathname.includes('/api/products/') || 
    url.pathname.includes('/api/categories/') ||
    url.pathname.includes('/api/promotions/'),
  new StaleWhileRevalidate({
    cacheName: 'master-data-cache',
    plugins: [
      new CacheableResponsePlugin({
        statuses: [0, 200],
      }),
      new ExpirationPlugin({
        maxEntries: 200,
        maxAgeSeconds: 60 * 60, // 1 hour
      }),
    ],
  })
);

// Static Assets - CacheFirst (images, fonts, CSS, JS)
registerRoute(
  ({ request }) => 
    request.destination === 'image' ||
    request.destination === 'font' ||
    request.destination === 'style' ||
    request.destination === 'script',
  new CacheFirst({
    cacheName: 'static-assets',
    plugins: [
      new CacheableResponsePlugin({
        statuses: [0, 200],
      }),
      new ExpirationPlugin({
        maxEntries: 500,
        maxAgeSeconds: 30 * 24 * 60 * 60, // 30 days
      }),
    ],
  })
);

// Listen for Background Sync registration
self.addEventListener('sync', (event) => {
  console.log('[Service Worker] Sync event:', event.tag);
  
  if (event.tag === 'sync-orders') {
    event.waitUntil(syncOrders());
  }
});

// Manual sync function
async function syncOrders() {
  console.log('[Service Worker] Syncing orders...');
  
  try {
    // Get pending orders from IndexedDB
    const db = await openDB();
    const orders = await getPendingOrders(db);
    
    console.log(`[Service Worker] Found ${orders.length} pending orders`);
    
    for (const order of orders) {
      try {
        const response = await fetch('/api/orders/order-groups/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(order.data),
        });
        
        if (response.ok) {
          console.log('[Service Worker] Order synced:', order.id);
          await markOrderAsSynced(db, order.id);
        } else {
          console.error('[Service Worker] Failed to sync order:', order.id, response.status);
        }
      } catch (error) {
        console.error('[Service Worker] Error syncing order:', order.id, error);
      }
    }
    
    console.log('[Service Worker] Sync completed');
  } catch (error) {
    console.error('[Service Worker] Sync failed:', error);
  }
}

// IndexedDB helpers
async function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('kiosk_offline_orders', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('orders')) {
        const store = db.createObjectStore('orders', { keyPath: 'id', autoIncrement: true });
        store.createIndex('synced', 'synced', { unique: false });
        store.createIndex('createdAt', 'createdAt', { unique: false });
      }
    };
  });
}

async function getPendingOrders(db) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(['orders'], 'readonly');
    const store = transaction.objectStore('orders');
    const index = store.index('synced');
    const request = index.getAll(0); // 0 = not synced
    
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function markOrderAsSynced(db, orderId) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(['orders'], 'readwrite');
    const store = transaction.objectStore('orders');
    const request = store.get(orderId);
    
    request.onsuccess = () => {
      const order = request.result;
      order.synced = 1;
      order.syncedAt = new Date().toISOString();
      
      const updateRequest = store.put(order);
      updateRequest.onsuccess = () => resolve();
      updateRequest.onerror = () => reject(updateRequest.error);
    };
    
    request.onerror = () => reject(request.error);
  });
}

// Listen for messages from client
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'SYNC_NOW') {
    console.log('[Service Worker] Manual sync requested');
    syncOrders().then(() => {
      event.ports[0].postMessage({ success: true });
    }).catch((error) => {
      event.ports[0].postMessage({ success: false, error: error.message });
    });
  }
});

// Activate immediately
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(self.clients.claim());
});
