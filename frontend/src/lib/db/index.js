/**
 * IndexedDB Database for Offline-First POS
 * Using Dexie.js for simplified IndexedDB operations
 */
import Dexie from 'dexie';

export const db = new Dexie('POSDatabase');

// Define database schema
db.version(1).stores({
	products: '++id, sku, name, category_id, outlet_id, price, *tags, sync_status',
	categories: '++id, name, outlet_id, sort_order',
	modifiers: '++id, product_id, name, type, price',
	cart: '++id, product_id, quantity, modifiers, created_at',
	orders: '++id, order_number, status, total, payment_status, created_at, sync_status',
	order_items: '++id, order_id, product_id, quantity, price, modifiers',
	payments: '++id, order_id, method, amount, status, transaction_id, sync_status',
	sync_queue: '++id, entity_type, entity_id, action, data, created_at, retry_count',
	app_settings: 'key, value'
});

/**
 * Sync Queue Management
 */
export async function addToSyncQueue(entityType, entityId, action, data) {
	return await db.sync_queue.add({
		entity_type: entityType,
		entity_id: entityId,
		action: action,
		data: JSON.stringify(data),
		created_at: new Date().toISOString(),
		retry_count: 0
	});
}

/**
 * Get pending sync items
 */
export async function getPendingSyncItems() {
	return await db.sync_queue
		.where('retry_count')
		.below(5)
		.toArray();
}

/**
 * Remove synced item from queue
 */
export async function removeSyncItem(id) {
	return await db.sync_queue.delete(id);
}

/**
 * Increment retry count
 */
export async function incrementSyncRetry(id) {
	const item = await db.sync_queue.get(id);
	if (item) {
		return await db.sync_queue.update(id, {
			retry_count: item.retry_count + 1
		});
	}
}

/**
 * Product Operations
 */
export async function getProducts(categoryId = null, outletId = null) {
	let query = db.products;
	
	if (categoryId) {
		query = query.where('category_id').equals(categoryId);
	}
	
	if (outletId) {
		query = query.where('outlet_id').equals(outletId);
	}
	
	return await query.toArray();
}

export async function getProductById(id) {
	return await db.products.get(id);
}

export async function saveProduct(product) {
	return await db.products.put(product);
}

export async function saveProducts(products) {
	return await db.products.bulkPut(products);
}

/**
 * Category Operations
 */
export async function getCategories(outletId = null) {
	let query = db.categories;
	
	if (outletId) {
		query = query.where('outlet_id').equals(outletId);
	}
	
	return await query.sortBy('sort_order');
}

export async function saveCategories(categories) {
	return await db.categories.bulkPut(categories);
}

/**
 * Cart Operations
 */
export async function getCartItems() {
	return await db.cart.toArray();
}

export async function addToCart(product, quantity = 1, modifiers = []) {
	return await db.cart.add({
		product_id: product.id,
		product_name: product.name,
		product_price: product.price,
		quantity: quantity,
		modifiers: JSON.stringify(modifiers),
		created_at: new Date().toISOString()
	});
}

export async function updateCartItem(id, updates) {
	return await db.cart.update(id, updates);
}

export async function removeFromCart(id) {
	return await db.cart.delete(id);
}

export async function clearCart() {
	return await db.cart.clear();
}

/**
 * Order Operations
 */
export async function saveOrder(order) {
	return await db.orders.add({
		...order,
		sync_status: 'pending',
		created_at: new Date().toISOString()
	});
}

export async function getOrders(limit = 50) {
	return await db.orders
		.orderBy('created_at')
		.reverse()
		.limit(limit)
		.toArray();
}

export async function getOrderById(id) {
	return await db.orders.get(id);
}

/**
 * App Settings
 */
export async function getSetting(key) {
	const setting = await db.app_settings.get(key);
	return setting ? setting.value : null;
}

export async function saveSetting(key, value) {
	return await db.app_settings.put({ key, value });
}

/**
 * Clear all offline data (use carefully!)
 */
export async function clearAllData() {
	await db.products.clear();
	await db.categories.clear();
	await db.modifiers.clear();
	await db.cart.clear();
	await db.orders.clear();
	await db.order_items.clear();
	await db.payments.clear();
	await db.sync_queue.clear();
	console.log('All offline data cleared');
}

/**
 * Get database stats
 */
export async function getDatabaseStats() {
	return {
		products: await db.products.count(),
		categories: await db.categories.count(),
		cart_items: await db.cart.count(),
		orders: await db.orders.count(),
		pending_sync: await db.sync_queue.count()
	};
}

export default db;
