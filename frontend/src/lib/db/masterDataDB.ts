/**
 * Master Data IndexedDB Schema
 * 
 * Purpose: Store pre-fetched menu, categories, and promotions
 * for offline access and fast loading
 * 
 * Features:
 * - Versioning for incremental updates
 * - Automatic cache invalidation
 * - Query optimization with indexes
 * 
 * Version: 1.0.0
 * Date: 2026-01-12
 */

import { openDB, DBSchema, IDBPDatabase } from 'idb';

// ============================================================================
// TYPES
// ============================================================================

export interface Product {
	id: number;
	name: string;
	description: string | null;
	price: number;
	category: string;
	category_id: number | null;
	image: string | null;
	is_available: boolean;
	has_modifiers: boolean;
	modifiers?: Modifier[];
	outlet_id: number;
	tenant_id: number;
	version: number;
	updated_at: string;
}

export interface Category {
	id: number;
	name: string;
	description: string | null;
	display_order: number;
	version: number;
	updated_at: string;
}

export interface Promotion {
	id: number;
	name: string;
	description: string | null;
	discount_type: 'percentage' | 'fixed';
	discount_value: number;
	start_date: string;
	end_date: string;
	is_active: boolean;
	applicable_products: number[];
	version: number;
	updated_at: string;
}

export interface Modifier {
	id: number;
	name: string;
	options: ModifierOption[];
}

export interface ModifierOption {
	id: number;
	name: string;
	price: number;
}

export interface Metadata {
	key: string;
	value: any;
	updated_at: string;
}

// ============================================================================
// DATABASE SCHEMA
// ============================================================================

interface MasterDataDBSchema extends DBSchema {
	products: {
		key: number;
		value: Product;
		indexes: {
			'by-outlet': number;
			'by-category': string;
			'by-version': number;
			'by-updated': string;
		};
	};
	categories: {
		key: number;
		value: Category;
		indexes: {
			'by-version': number;
			'by-order': number;
		};
	};
	promotions: {
		key: number;
		value: Promotion;
		indexes: {
			'by-active': number; // 1 for active, 0 for inactive
			'by-version': number;
			'by-dates': string; // Combined start-end for range queries
		};
	};
	metadata: {
		key: string;
		value: Metadata;
	};
}

// ============================================================================
// DATABASE CONSTANTS
// ============================================================================

const DB_NAME = 'kiosk_master_data';
const DB_VERSION = 1;

// ============================================================================
// DATABASE INSTANCE
// ============================================================================

let dbInstance: IDBPDatabase<MasterDataDBSchema> | null = null;

/**
 * Open or get existing database connection
 */
export async function getMasterDataDB(): Promise<IDBPDatabase<MasterDataDBSchema>> {
	if (dbInstance) {
		return dbInstance;
	}

	dbInstance = await openDB<MasterDataDBSchema>(DB_NAME, DB_VERSION, {
		upgrade(db, oldVersion, newVersion, transaction) {
			console.log(`📦 Upgrading Master Data DB from v${oldVersion} to v${newVersion}`);

			// Products store
			if (!db.objectStoreNames.contains('products')) {
				const productsStore = db.createObjectStore('products', { keyPath: 'id' });
				productsStore.createIndex('by-outlet', 'outlet_id', { unique: false });
				productsStore.createIndex('by-category', 'category', { unique: false });
				productsStore.createIndex('by-version', 'version', { unique: false });
				productsStore.createIndex('by-updated', 'updated_at', { unique: false });
				console.log('✅ Created products store with indexes');
			}

			// Categories store
			if (!db.objectStoreNames.contains('categories')) {
				const categoriesStore = db.createObjectStore('categories', { keyPath: 'id' });
				categoriesStore.createIndex('by-version', 'version', { unique: false });
				categoriesStore.createIndex('by-order', 'display_order', { unique: false });
				console.log('✅ Created categories store with indexes');
			}

			// Promotions store
			if (!db.objectStoreNames.contains('promotions')) {
				const promotionsStore = db.createObjectStore('promotions', { keyPath: 'id' });
				promotionsStore.createIndex('by-active', 'is_active', { unique: false });
				promotionsStore.createIndex('by-version', 'version', { unique: false });
				promotionsStore.createIndex('by-dates', ['start_date', 'end_date'], { unique: false });
				console.log('✅ Created promotions store with indexes');
			}

			// Metadata store
			if (!db.objectStoreNames.contains('metadata')) {
				db.createObjectStore('metadata', { keyPath: 'key' });
				console.log('✅ Created metadata store');
			}
		},
		blocked() {
			console.warn('⚠️ Master Data DB upgrade blocked - close other tabs');
		},
		blocking() {
			console.warn('⚠️ Master Data DB blocking - closing connection');
			dbInstance?.close();
			dbInstance = null;
		}
	});

	console.log('✅ Master Data DB opened');
	return dbInstance;
}

// ============================================================================
// PRODUCTS OPERATIONS
// ============================================================================

/**
 * Save or update products
 */
export async function saveProducts(products: Product[]): Promise<void> {
	const db = await getMasterDataDB();
	const tx = db.transaction('products', 'readwrite');
	
	await Promise.all(
		products.map(product => tx.store.put(product))
	);
	
	await tx.done;
	console.log(`✅ Saved ${products.length} products to IndexedDB`);
}

/**
 * Get all products
 */
export async function getAllProducts(): Promise<Product[]> {
	const db = await getMasterDataDB();
	return db.getAll('products');
}

/**
 * Get products by outlet
 */
export async function getProductsByOutlet(outletId: number): Promise<Product[]> {
	const db = await getMasterDataDB();
	return db.getAllFromIndex('products', 'by-outlet', outletId);
}

/**
 * Get products by category
 */
export async function getProductsByCategory(category: string): Promise<Product[]> {
	const db = await getMasterDataDB();
	return db.getAllFromIndex('products', 'by-category', category);
}

/**
 * Get products updated after version
 */
export async function getProductsSinceVersion(version: number): Promise<Product[]> {
	const db = await getMasterDataDB();
	const allProducts = await db.getAll('products');
	return allProducts.filter(p => p.version > version);
}

/**
 * Clear all products
 */
export async function clearProducts(): Promise<void> {
	const db = await getMasterDataDB();
	await db.clear('products');
	console.log('🗑️ Cleared all products');
}

// ============================================================================
// CATEGORIES OPERATIONS
// ============================================================================

/**
 * Save or update categories
 */
export async function saveCategories(categories: Category[]): Promise<void> {
	const db = await getMasterDataDB();
	const tx = db.transaction('categories', 'readwrite');
	
	await Promise.all(
		categories.map(category => tx.store.put(category))
	);
	
	await tx.done;
	console.log(`✅ Saved ${categories.length} categories to IndexedDB`);
}

/**
 * Get all categories
 */
export async function getAllCategories(): Promise<Category[]> {
	const db = await getMasterDataDB();
	const categories = await db.getAll('categories');
	// Sort by display order
	return categories.sort((a, b) => a.display_order - b.display_order);
}

/**
 * Clear all categories
 */
export async function clearCategories(): Promise<void> {
	const db = await getMasterDataDB();
	await db.clear('categories');
	console.log('🗑️ Cleared all categories');
}

// ============================================================================
// PROMOTIONS OPERATIONS
// ============================================================================

/**
 * Save or update promotions
 */
export async function savePromotions(promotions: Promotion[]): Promise<void> {
	const db = await getMasterDataDB();
	const tx = db.transaction('promotions', 'readwrite');
	
	await Promise.all(
		promotions.map(promotion => tx.store.put(promotion))
	);
	
	await tx.done;
	console.log(`✅ Saved ${promotions.length} promotions to IndexedDB`);
}

/**
 * Get all active promotions
 */
export async function getActivePromotions(): Promise<Promotion[]> {
	const db = await getMasterDataDB();
	const now = new Date().toISOString();
	
	const allPromotions = await db.getAll('promotions');
	
	// Filter active promotions within date range
	return allPromotions.filter(promo => 
		promo.is_active &&
		promo.start_date <= now &&
		promo.end_date >= now
	);
}

/**
 * Get all promotions
 */
export async function getAllPromotions(): Promise<Promotion[]> {
	const db = await getMasterDataDB();
	return db.getAll('promotions');
}

/**
 * Clear all promotions
 */
export async function clearPromotions(): Promise<void> {
	const db = await getMasterDataDB();
	await db.clear('promotions');
	console.log('🗑️ Cleared all promotions');
}

// ============================================================================
// METADATA OPERATIONS
// ============================================================================

/**
 * Set metadata value
 */
export async function setMetadata(key: string, value: any): Promise<void> {
	const db = await getMasterDataDB();
	await db.put('metadata', {
		key,
		value,
		updated_at: new Date().toISOString()
	});
}

/**
 * Get metadata value
 */
export async function getMetadata(key: string): Promise<any> {
	const db = await getMasterDataDB();
	const metadata = await db.get('metadata', key);
	return metadata?.value;
}

/**
 * Get all metadata
 */
export async function getAllMetadata(): Promise<Record<string, any>> {
	const db = await getMasterDataDB();
	const allMetadata = await db.getAll('metadata');
	
	const result: Record<string, any> = {};
	allMetadata.forEach(meta => {
		result[meta.key] = meta.value;
	});
	
	return result;
}

// ============================================================================
// VERSION MANAGEMENT
// ============================================================================

/**
 * Get current version for a data type
 */
export async function getVersion(dataType: 'products' | 'categories' | 'promotions'): Promise<number> {
	const version = await getMetadata(`${dataType}_version`);
	return version || 0;
}

/**
 * Set version for a data type
 */
export async function setVersion(dataType: 'products' | 'categories' | 'promotions', version: number): Promise<void> {
	await setMetadata(`${dataType}_version`, version);
	console.log(`✅ Set ${dataType} version to ${version}`);
}

/**
 * Get last sync timestamp
 */
export async function getLastSyncTime(): Promise<Date | null> {
	const timestamp = await getMetadata('last_sync_time');
	return timestamp ? new Date(timestamp) : null;
}

/**
 * Set last sync timestamp
 */
export async function setLastSyncTime(timestamp: Date = new Date()): Promise<void> {
	await setMetadata('last_sync_time', timestamp.toISOString());
}

// ============================================================================
// CACHE MANAGEMENT
// ============================================================================

/**
 * Clear all cached data
 */
export async function clearAllCache(): Promise<void> {
	await clearProducts();
	await clearCategories();
	await clearPromotions();
	
	// Reset versions
	await setVersion('products', 0);
	await setVersion('categories', 0);
	await setVersion('promotions', 0);
	await setLastSyncTime(new Date(0));
	
	console.log('🗑️ Cleared all master data cache');
}

/**
 * Check if cache is stale (older than 24 hours)
 */
export async function isCacheStale(maxAgeHours: number = 24): Promise<boolean> {
	const lastSync = await getLastSyncTime();
	
	if (!lastSync) {
		return true; // No cache
	}
	
	const ageMs = Date.now() - lastSync.getTime();
	const ageHours = ageMs / (1000 * 60 * 60);
	
	return ageHours > maxAgeHours;
}

/**
 * Get cache statistics
 */
export async function getCacheStats(): Promise<{
	productsCount: number;
	categoriesCount: number;
	promotionsCount: number;
	lastSync: Date | null;
	isStale: boolean;
}> {
	const db = await getMasterDataDB();
	
	const [productsCount, categoriesCount, promotionsCount, lastSync, isStale] = await Promise.all([
		db.count('products'),
		db.count('categories'),
		db.count('promotions'),
		getLastSyncTime(),
		isCacheStale()
	]);
	
	return {
		productsCount,
		categoriesCount,
		promotionsCount,
		lastSync,
		isStale
	};
}
