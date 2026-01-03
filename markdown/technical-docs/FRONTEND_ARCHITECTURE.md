# 🎨 Frontend Architecture - SvelteKit Application

## Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [SvelteKit Concepts](#sveltekit-concepts)
- [State Management](#state-management)
- [Offline-First Strategy](#offline-first-strategy)
- [Routing & Navigation](#routing--navigation)
- [Component Architecture](#component-architecture)
- [API Integration](#api-integration)
- [PWA Features](#pwa-features)

---

## Overview

Frontend menggunakan **SvelteKit** (Svelte 4) sebagai framework utama dengan pendekatan **offline-first** untuk mendukung operasi tanpa internet. UI menggunakan **TailwindCSS** dan **DaisyUI** untuk styling.

### Key Features

- **Reactive**: Auto-update UI ketika state berubah
- **Offline-First**: Semua data di-cache di IndexedDB
- **PWA**: Installable, work offline, push notifications
- **Fast**: Minimal bundle size, no virtual DOM
- **Type-Safe**: JavaScript dengan JSDoc annotations

### Tech Stack

```javascript
Framework:      SvelteKit 1.x (Svelte 4)
Language:       JavaScript (ES6+)
UI:             TailwindCSS + DaisyUI
State:          Svelte Stores (writable, derived)
Database:       IndexedDB (via Dexie.js)
HTTP:           Fetch API with retry logic
Build:          Vite
PWA:            Vite PWA Plugin
```

---

## Project Structure

```
frontend/
├── src/
│   ├── routes/                 # SvelteKit routes (file-based routing)
│   │   ├── +layout.svelte     # Root layout (wraps all pages)
│   │   ├── +page.svelte       # Home page (/)
│   │   │
│   │   ├── kiosk/             # Kiosk mode (/kiosk)
│   │   │   └── +page.svelte   # Main kiosk UI
│   │   │
│   │   └── kitchen/           # Kitchen display (/kitchen)
│   │       └── +page.svelte   # Kitchen order display
│   │
│   ├── lib/                   # Reusable code
│   │   ├── components/        # Svelte components
│   │   │   ├── PaymentModal.svelte
│   │   │   ├── ModifierModal.svelte
│   │   │   ├── ProductCard.svelte
│   │   │   └── CartItem.svelte
│   │   │
│   │   ├── stores/            # State management
│   │   │   ├── cart.js       # Cart state & operations
│   │   │   ├── auth.js       # Auth state & tokens
│   │   │   ├── settings.js   # App settings
│   │   │   └── sync.js       # Sync state
│   │   │
│   │   ├── db/                # IndexedDB wrapper
│   │   │   └── index.js      # Dexie database & operations
│   │   │
│   │   ├── api/               # API client
│   │   │   ├── client.js     # Base HTTP client
│   │   │   ├── products.js   # Product API
│   │   │   ├── orders.js     # Order API
│   │   │   └── auth.js       # Auth API
│   │   │
│   │   └── utils/             # Utility functions
│   │       ├── formatters.js # Format currency, date
│   │       ├── validators.js # Input validation
│   │       └── helpers.js    # Common helpers
│   │
│   ├── app.html               # HTML template
│   ├── app.css                # Global styles
│   └── service-worker.js      # PWA service worker
│
├── static/                    # Static assets
│   ├── favicon.png
│   ├── manifest.json         # PWA manifest
│   └── icons/                # PWA icons
│
├── package.json
├── svelte.config.js          # SvelteKit config
├── vite.config.js            # Vite config
├── tailwind.config.js        # TailwindCSS config
└── Dockerfile                # Container definition
```

---

## SvelteKit Concepts

### 1. File-Based Routing

SvelteKit menggunakan file system untuk routing:

```
routes/
├── +page.svelte              → /
├── kiosk/+page.svelte        → /kiosk
├── kitchen/+page.svelte      → /kitchen
└── admin/
    ├── +page.svelte          → /admin
    └── products/
        └── +page.svelte      → /admin/products
```

### 2. Layout System

**Root Layout** (`+layout.svelte`):
```svelte
<script>
  import '../app.css';
  import { onMount } from 'svelte';
  import { loadCart } from '$stores/cart.js';
  
  // Run on app startup
  onMount(() => {
    loadCart();
  });
</script>

<div class="app">
  <!-- This slot renders child pages -->
  <slot />
</div>
```

**Nested Layout**:
```svelte
<!-- routes/admin/+layout.svelte -->
<script>
  import Sidebar from '$lib/components/Sidebar.svelte';
</script>

<div class="admin-layout">
  <Sidebar />
  <main>
    <slot /> <!-- Child pages render here -->
  </main>
</div>
```

### 3. Page Components

**Simple Page** (`+page.svelte`):
```svelte
<script>
  import { onMount } from 'svelte';
  
  let products = [];
  
  onMount(async () => {
    // Fetch data on component mount
    products = await getProducts();
  });
</script>

<div class="page">
  <h1>Products</h1>
  
  {#each products as product}
    <ProductCard {product} />
  {/each}
</div>
```

### 4. Load Functions (SSR)

**Server-Side Data Loading** (`+page.js` or `+page.server.js`):
```javascript
// routes/products/+page.js
export async function load({ fetch, params }) {
  const response = await fetch('/api/products');
  const products = await response.json();
  
  return {
    products
  };
}
```

**In Component**:
```svelte
<script>
  export let data; // From load function
  
  $: products = data.products;
</script>
```

---

## State Management

### Svelte Stores

**Writable Store** (read/write):
```javascript
// lib/stores/cart.js
import { writable } from 'svelte/store';

export const cartItems = writable([]);

// Usage in component:
// import { cartItems } from '$stores/cart.js';
// $cartItems (read)
// cartItems.set([...]) (write)
```

**Derived Store** (computed):
```javascript
import { writable, derived } from 'svelte/store';

export const cartItems = writable([]);

export const cartTotals = derived(cartItems, ($cartItems) => {
  const subtotal = $cartItems.reduce((sum, item) => 
    sum + (item.product_price * item.quantity), 0
  );
  
  const tax = subtotal * 0.10;
  const total = subtotal + tax;
  
  return { subtotal, tax, total };
});
```

**Custom Store** (with methods):
```javascript
function createCartStore() {
  const { subscribe, set, update } = writable([]);
  
  return {
    subscribe,
    add: (item) => update(items => [...items, item]),
    remove: (id) => update(items => items.filter(i => i.id !== id)),
    clear: () => set([]),
  };
}

export const cart = createCartStore();
```

### Store Organization

```
stores/
├── cart.js           # Shopping cart state
│   ├── cartItems (writable)
│   ├── cartTotals (derived)
│   └── functions: addProductToCart, updateQuantity, etc.
│
├── auth.js           # Authentication state
│   ├── currentUser (writable)
│   ├── isAuthenticated (derived)
│   └── functions: login, logout, refreshToken
│
├── settings.js       # App settings
│   ├── theme (writable)
│   ├── outlet (writable)
│   └── functions: loadSettings, saveSettings
│
└── sync.js           # Offline sync state
    ├── isSyncing (writable)
    ├── lastSyncTime (writable)
    └── functions: syncData, checkOnline
```

### Using Stores in Components

```svelte
<script>
  import { cartItems, cartTotals } from '$stores/cart.js';
  
  // Auto-subscribed with $ prefix
  $: itemCount = $cartItems.length;
  $: totalAmount = $cartTotals.total;
  
  function addItem(product) {
    // Will trigger reactive update
    cartItems.update(items => [...items, product]);
  }
</script>

<div>
  <p>Items: {itemCount}</p>
  <p>Total: Rp {totalAmount}</p>
  
  {#each $cartItems as item}
    <CartItem {item} />
  {/each}
</div>
```

---

## Offline-First Strategy

### Architecture

```
┌──────────────────────────────────────────┐
│           UI Components                  │
│  (Svelte Components, Reactive Updates)   │
└──────────────┬───────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
   ┌────▼────┐   ┌────▼────┐
   │ Stores  │   │   API   │
   │(Memory) │   │ Client  │
   └────┬────┘   └────┬────┘
        │             │
   ┌────▼─────────────▼────┐
   │     IndexedDB          │
   │  (Persistent Storage)  │
   └────────────────────────┘
```

### IndexedDB Schema

```javascript
// lib/db/index.js
import Dexie from 'dexie';

export const db = new Dexie('POSDatabase');

db.version(1).stores({
  // Product catalog (synced from API)
  products: '++id, sku, name, category_id, outlet_id, price, sync_status',
  categories: '++id, name, outlet_id, sort_order',
  modifiers: '++id, product_id, name, type, price',
  
  // Cart (user's current order)
  cart: '++id, product_id, tenant_id, quantity, modifiers, notes, created_at',
  
  // Orders (pending sync)
  orders: '++id, order_number, status, total, created_at, sync_status',
  order_items: '++id, order_id, product_id, quantity, price',
  payments: '++id, order_id, method, amount, status, sync_status',
  
  // Sync queue
  sync_queue: '++id, entity_type, action, data, created_at, retry_count',
  
  // App state
  app_settings: 'key, value'
});
```

### Cart Operations (Offline-First)

```javascript
// lib/stores/cart.js
import { writable } from 'svelte/store';
import { 
  getCartItems, 
  addToCart as dbAddToCart, 
  updateCartItem, 
  removeFromCart 
} from '$db';

export const cartItems = writable([]);

/**
 * Load cart from IndexedDB (always local)
 */
export async function loadCart() {
  const items = await getCartItems();
  cartItems.set(items);
}

/**
 * Add product to cart (offline capable)
 */
export async function addProductToCart(product, quantity = 1, modifiers = []) {
  try {
    // Save to IndexedDB immediately
    const id = await dbAddToCart(product, quantity, modifiers);
    
    // Update reactive store
    await loadCart();
    
    return id;
  } catch (error) {
    console.error('Error adding to cart:', error);
    throw error;
  }
}

/**
 * Update quantity (offline capable)
 */
export async function updateQuantity(itemId, newQuantity) {
  if (newQuantity <= 0) {
    return await removeCartItem(itemId);
  }
  
  await updateCartItem(itemId, { quantity: newQuantity });
  await loadCart();
}
```

### Checkout with Sync

```javascript
// lib/api/orders.js
import { db, addToSyncQueue } from '$db';
import { apiClient } from './client.js';

export async function checkout(orderData) {
  try {
    // Try online first
    if (navigator.onLine) {
      const response = await apiClient.post('/api/orders/checkout/', orderData);
      return response.data;
    }
  } catch (error) {
    console.log('Offline mode - saving to sync queue');
  }
  
  // Offline fallback: Save to local DB
  const orderId = await db.orders.add({
    ...orderData,
    order_number: generateOfflineOrderNumber(),
    status: 'pending',
    sync_status: 'pending',
    created_at: new Date().toISOString()
  });
  
  // Add to sync queue
  await addToSyncQueue('order', orderId, 'create', orderData);
  
  return {
    id: orderId,
    order_number: orderData.order_number,
    status: 'pending',
    offline: true
  };
}
```

### Background Sync

```javascript
// lib/stores/sync.js
import { writable } from 'svelte/store';
import { getPendingSyncItems, removeSyncItem } from '$db';
import { apiClient } from '$api/client.js';

export const isSyncing = writable(false);
export const lastSyncTime = writable(null);

/**
 * Sync pending items to server
 */
export async function syncData() {
  if (!navigator.onLine) {
    console.log('Offline - skipping sync');
    return;
  }
  
  isSyncing.set(true);
  
  try {
    const pendingItems = await getPendingSyncItems();
    
    for (const item of pendingItems) {
      try {
        const data = JSON.parse(item.data);
        
        // Sync based on entity type
        if (item.entity_type === 'order') {
          await apiClient.post('/api/orders/checkout/', data);
        }
        // ... other entity types
        
        // Remove from queue after successful sync
        await removeSyncItem(item.id);
        
      } catch (error) {
        console.error(`Sync failed for item ${item.id}:`, error);
        // Increment retry count
        await incrementSyncRetry(item.id);
      }
    }
    
    lastSyncTime.set(new Date().toISOString());
    
  } catch (error) {
    console.error('Sync error:', error);
  } finally {
    isSyncing.set(false);
  }
}

/**
 * Auto-sync when online
 */
export function setupAutoSync() {
  // Sync when coming online
  window.addEventListener('online', () => {
    console.log('Online - triggering sync');
    syncData();
  });
  
  // Periodic sync every 5 minutes
  setInterval(() => {
    if (navigator.onLine) {
      syncData();
    }
  }, 5 * 60 * 1000);
}
```

---

## Routing & Navigation

### Routes Structure

```
/                       → Landing page / Tenant selection
/kiosk                  → Kiosk mode (self-service)
/kitchen                → Kitchen display system
/admin                  → Admin dashboard (requires auth)
/admin/products         → Product management
/admin/orders           → Order management
/admin/settings         → Settings
```

### Navigation Component

```svelte
<!-- lib/components/Navigation.svelte -->
<script>
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  
  $: currentPath = $page.url.pathname;
  
  function navigateTo(path) {
    goto(path);
  }
</script>

<nav>
  <a 
    href="/kiosk" 
    class:active={currentPath === '/kiosk'}
  >
    Kiosk
  </a>
  
  <a 
    href="/kitchen" 
    class:active={currentPath === '/kitchen'}
  >
    Kitchen
  </a>
  
  <a 
    href="/admin" 
    class:active={currentPath.startsWith('/admin')}
  >
    Admin
  </a>
</nav>
```

### Programmatic Navigation

```javascript
import { goto } from '$app/navigation';

// Navigate to route
goto('/kiosk');

// With state
goto('/checkout', { state: { orderId: 123 } });

// Replace history
goto('/success', { replaceState: true });

// External redirect
window.location.href = 'https://payment-gateway.com';
```

---

## Component Architecture

### Component Patterns

#### 1. **Presentational Component**

Hanya UI, tidak ada business logic.

```svelte
<!-- ProductCard.svelte -->
<script>
  export let product;
  export let onAddToCart = () => {};
  
  $: displayPrice = product.has_promo 
    ? product.promo_price 
    : product.price;
</script>

<div class="card">
  <img src={product.image} alt={product.name} />
  <h3>{product.name}</h3>
  <p class="price">Rp {displayPrice.toLocaleString()}</p>
  
  {#if product.has_promo}
    <span class="badge-promo">PROMO</span>
  {/if}
  
  <button on:click={() => onAddToCart(product)}>
    Add to Cart
  </button>
</div>

<style>
  .card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 16px;
  }
  
  .badge-promo {
    background: red;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
  }
</style>
```

#### 2. **Container Component**

Handle business logic dan state.

```svelte
<!-- ProductList.svelte -->
<script>
  import { onMount } from 'svelte';
  import ProductCard from './ProductCard.svelte';
  import { getProducts } from '$db';
  import { addProductToCart } from '$stores/cart.js';
  
  let products = [];
  let loading = true;
  
  onMount(async () => {
    products = await getProducts();
    loading = false;
  });
  
  async function handleAddToCart(product) {
    try {
      await addProductToCart(product, 1);
      alert('Added to cart!');
    } catch (error) {
      alert('Failed to add to cart');
    }
  }
</script>

{#if loading}
  <p>Loading...</p>
{:else}
  <div class="grid">
    {#each products as product}
      <ProductCard 
        {product} 
        onAddToCart={handleAddToCart} 
      />
    {/each}
  </div>
{/if}
```

#### 3. **Modal Component**

Reusable dialog/modal.

```svelte
<!-- Modal.svelte -->
<script>
  export let isOpen = false;
  export let title = '';
  export let onClose = () => {};
</script>

{#if isOpen}
  <div class="modal-overlay" on:click={onClose}>
    <div class="modal-content" on:click|stopPropagation>
      <div class="modal-header">
        <h2>{title}</h2>
        <button on:click={onClose}>&times;</button>
      </div>
      
      <div class="modal-body">
        <slot /> <!-- Content goes here -->
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  
  .modal-content {
    background: white;
    border-radius: 8px;
    padding: 24px;
    max-width: 600px;
    width: 90%;
  }
</style>
```

**Usage**:
```svelte
<script>
  import Modal from './Modal.svelte';
  
  let showModal = false;
</script>

<button on:click={() => showModal = true}>
  Open Modal
</button>

<Modal 
  isOpen={showModal} 
  title="Confirmation"
  onClose={() => showModal = false}
>
  <p>Are you sure?</p>
  <button>Yes</button>
  <button on:click={() => showModal = false}>No</button>
</Modal>
```

---

## API Integration

### API Client

```javascript
// lib/api/client.js
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }
  
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    // Add default headers
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };
    
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Add tenant headers if set
    const tenantId = localStorage.getItem('tenant_id');
    const outletId = localStorage.getItem('outlet_id');
    if (tenantId) headers['X-Tenant-ID'] = tenantId;
    if (outletId) headers['X-Outlet-ID'] = outletId;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
      
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }
  
  get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  }
  
  post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
  
  put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }
  
  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();
```

### API Modules

```javascript
// lib/api/products.js
import { apiClient } from './client.js';

export async function fetchProducts(tenantId = null, categoryId = null) {
  const params = new URLSearchParams();
  if (tenantId) params.append('tenant_id', tenantId);
  if (categoryId) params.append('category_id', categoryId);
  
  return await apiClient.get(`/api/products/?${params}`);
}

export async function fetchProductDetail(id) {
  return await apiClient.get(`/api/products/${id}/`);
}

// lib/api/orders.js
export async function checkoutOrder(orderData) {
  return await apiClient.post('/api/orders/checkout/', orderData);
}
```

---

## PWA Features

### Manifest

```json
// static/manifest.json
{
  "name": "POS F&B Kiosk",
  "short_name": "POS Kiosk",
  "description": "Food & Beverage POS System",
  "start_url": "/kiosk",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#FF6B35",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

### Service Worker (Vite PWA)

```javascript
// vite.config.js
import { sveltekit } from '@sveltejs/kit/vite';
import { VitePWA } from 'vite-plugin-pwa';

export default {
  plugins: [
    sveltekit(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'POS F&B Kiosk',
        short_name: 'POS',
        theme_color: '#FF6B35',
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,png,jpg,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.example\.com\/api\/.*/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60 // 1 hour
              }
            }
          }
        ]
      }
    })
  ]
};
```

---

## Next Steps

- **[FRONTEND_FLOW.md](FRONTEND_FLOW.md)** - Detailed user flow & interactions
- **[MULTI_TENANT_DEEP_DIVE.md](MULTI_TENANT_DEEP_DIVE.md)** - Multi-tenant frontend implementation
- **[DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md)** - Setup development environment

---

**Last Updated**: January 3, 2026
