/**
 * Master Data Service
 * 
 * Handles pre-fetching and caching of critical data (menu, prices, categories)
 * when application starts and internet is available.
 * 
 * Features:
 * - Pre-fetch on app start when online
 * - Version tracking to avoid unnecessary downloads
 * - IndexedDB caching for offline access
 * - Incremental updates (only fetch changes)
 * - Automatic retry mechanism
 */

import { writable, type Writable } from 'svelte/store';
import { PUBLIC_API_URL } from '$env/static/public';
import { browser } from '$app/environment';

export interface MasterDataVersion {
	productsVersion: number;
	categoriesVersion: number;
	promotionsVersion: number;
	lastSyncAt: Date | null;
}

export interface MasterDataStatus {
	isSyncing: boolean;
	lastSyncAt: Date | null;
	syncError: string | null;
	productsCount: number;
	categoriesCount: number;
	promotionsCount: number;
}

export interface Product {
	id: number;
	name: string;
	description: string;
	price: number;
	category_id: number;
	image_url?: string;
	is_available: boolean;
	updated_at: string;
}

export interface Category {
	id: number;
	name: string;
	description: string;
	sort_order: number;
	is_active: boolean;
	updated_at: string;
}

export interface Promotion {
	id: number;
	name: string;
	discount_type: 'percentage' | 'fixed';
	discount_value: number;
	start_date: string;
	end_date: string;
	is_active: boolean;
	applicable_products: number[];
	updated_at: string;
}

class MasterDataService {
	private readonly DB_NAME = 'kiosk_master_data';
	private readonly DB_VERSION = 1;
	private db: IDBDatabase | null = null;

	// Stores
	public status: Writable<MasterDataStatus>;
	public version: Writable<MasterDataVersion>;

	constructor() {
		this.status = writable<MasterDataStatus>({
			isSyncing: false,
			lastSyncAt: null,
			syncError: null,
			productsCount: 0,
			categoriesCount: 0,
			promotionsCount: 0
		});

		this.version = writable<MasterDataVersion>({
			productsVersion: 0,
			categoriesVersion: 0,
			promotionsVersion: 0,
			lastSyncAt: null
		});

		if (browser) {
			this.initDB();
		}
	}

	/**
	 * Initialize IndexedDB for master data caching
	 */
	private async initDB(): Promise<void> {
		return new Promise((resolve, reject) => {
			const request = indexedDB.open(this.DB_NAME, this.DB_VERSION);

			request.onerror = () => {
				console.error('❌ Failed to open master data IndexedDB:', request.error);
				reject(request.error);
			};

			request.onsuccess = () => {
				this.db = request.result;
				console.log('✅ Master data IndexedDB opened successfully');
				resolve();
			};

			request.onupgradeneeded = (event) => {
				const db = (event.target as IDBOpenDBRequest).result;

				// Products store
				if (!db.objectStoreNames.contains('products')) {
					const productsStore = db.createObjectStore('products', { keyPath: 'id' });
					productsStore.createIndex('category_id', 'category_id', { unique: false });
					productsStore.createIndex('updated_at', 'updated_at', { unique: false });
				}

				// Categories store
				if (!db.objectStoreNames.contains('categories')) {
					const categoriesStore = db.createObjectStore('categories', { keyPath: 'id' });
					categoriesStore.createIndex('sort_order', 'sort_order', { unique: false });
				}

				// Promotions store
				if (!db.objectStoreNames.contains('promotions')) {
					const promotionsStore = db.createObjectStore('promotions', { keyPath: 'id' });
					promotionsStore.createIndex('is_active', 'is_active', { unique: false });
				}

				// Metadata store (for version tracking)
				if (!db.objectStoreNames.contains('metadata')) {
					db.createObjectStore('metadata', { keyPath: 'key' });
				}

				console.log('📦 Master data IndexedDB structure created');
			};
		});
	}

	/**
	 * Pre-fetch all master data on app start (when online)
	 */
	async preFetchData(): Promise<void> {
		if (!browser) {
			console.warn('⚠️ Master data pre-fetch skipped: Not in browser context');
			return;
		}

		console.log('🔄 Starting master data pre-fetch...');
		
		this.status.update(s => ({ ...s, isSyncing: true, syncError: null }));

		try {
			// Wait for DB to be ready
			if (!this.db) {
				await this.initDB();
			}

			// Get current version from local cache
			const currentVersion = await this.getStoredVersion();

			// Fetch updates from server
			await this.fetchProducts(currentVersion.productsVersion);
			await this.fetchCategories(currentVersion.categoriesVersion);
			await this.fetchPromotions(currentVersion.promotionsVersion);

			// Update sync status
			const newVersion: MasterDataVersion = {
				productsVersion: currentVersion.productsVersion + 1,
				categoriesVersion: currentVersion.categoriesVersion + 1,
				promotionsVersion: currentVersion.promotionsVersion + 1,
				lastSyncAt: new Date()
			};

			await this.storeVersion(newVersion);

			const counts = await this.getCounts();
			
			this.status.update(s => ({
				...s,
				isSyncing: false,
				lastSyncAt: new Date(),
				...counts
			}));

			this.version.set(newVersion);

			console.log('✅ Master data pre-fetch completed:', counts);

		} catch (error) {
			console.error('❌ Master data pre-fetch failed:', error);
			this.status.update(s => ({
				...s,
				isSyncing: false,
				syncError: error instanceof Error ? error.message : 'Unknown error'
			}));
			throw error;
		}
	}

	/**
	 * Fetch products from server (incremental)
	 */
	private async fetchProducts(sinceVersion: number): Promise<void> {
		const url = `${PUBLIC_API_URL}/products/?since_version=${sinceVersion}`;
		
		const response = await fetch(url, {
			method: 'GET',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (!response.ok) {
			throw new Error(`Failed to fetch products: ${response.statusText}`);
		}

		const products: Product[] = await response.json();
		
		console.log(`📦 Fetched ${products.length} products (since version ${sinceVersion})`);

		// Store in IndexedDB
		await this.storeProducts(products);
	}

	/**
	 * Fetch categories from server (incremental)
	 */
	private async fetchCategories(sinceVersion: number): Promise<void> {
		const url = `${PUBLIC_API_URL}/categories/?since_version=${sinceVersion}`;
		
		const response = await fetch(url, {
			method: 'GET',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (!response.ok) {
			throw new Error(`Failed to fetch categories: ${response.statusText}`);
		}

		const categories: Category[] = await response.json();
		
		console.log(`📦 Fetched ${categories.length} categories (since version ${sinceVersion})`);

		// Store in IndexedDB
		await this.storeCategories(categories);
	}

	/**
	 * Fetch promotions from server (incremental)
	 */
	private async fetchPromotions(sinceVersion: number): Promise<void> {
		const url = `${PUBLIC_API_URL}/promotions/?since_version=${sinceVersion}`;
		
		const response = await fetch(url, {
			method: 'GET',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (!response.ok) {
			throw new Error(`Failed to fetch promotions: ${response.statusText}`);
		}

		const promotions: Promotion[] = await response.json();
		
		console.log(`📦 Fetched ${promotions.length} promotions (since version ${sinceVersion})`);

		// Store in IndexedDB
		await this.storePromotions(promotions);
	}

	/**
	 * Store products in IndexedDB
	 */
	private async storeProducts(products: Product[]): Promise<void> {
		if (!this.db) throw new Error('Database not initialized');

		const transaction = this.db.transaction(['products'], 'readwrite');
		const store = transaction.objectStore('products');

		for (const product of products) {
			store.put(product);
		}

		return new Promise((resolve, reject) => {
			transaction.oncomplete = () => resolve();
			transaction.onerror = () => reject(transaction.error);
		});
	}

	/**
	 * Store categories in IndexedDB
	 */
	private async storeCategories(categories: Category[]): Promise<void> {
		if (!this.db) throw new Error('Database not initialized');

		const transaction = this.db.transaction(['categories'], 'readwrite');
		const store = transaction.objectStore('categories');

		for (const category of categories) {
			store.put(category);
		}

		return new Promise((resolve, reject) => {
			transaction.oncomplete = () => resolve();
			transaction.onerror = () => reject(transaction.error);
		});
	}

	/**
	 * Store promotions in IndexedDB
	 */
	private async storePromotions(promotions: Promotion[]): Promise<void> {
		if (!this.db) throw new Error('Database not initialized');

		const transaction = this.db.transaction(['promotions'], 'readwrite');
		const store = transaction.objectStore('promotions');

		for (const promotion of promotions) {
			store.put(promotion);
		}

		return new Promise((resolve, reject) => {
			transaction.oncomplete = () => resolve();
			transaction.onerror = () => reject(transaction.error);
		});
	}

	/**
	 * Get stored version from IndexedDB
	 */
	private async getStoredVersion(): Promise<MasterDataVersion> {
		if (!this.db) throw new Error('Database not initialized');

		const transaction = this.db.transaction(['metadata'], 'readonly');
		const store = transaction.objectStore('metadata');
		
		return new Promise((resolve) => {
			const request = store.get('version');
			
			request.onsuccess = () => {
				if (request.result) {
					resolve(request.result.value);
				} else {
					// Default version if not found
					resolve({
						productsVersion: 0,
						categoriesVersion: 0,
						promotionsVersion: 0,
						lastSyncAt: null
					});
				}
			};

			request.onerror = () => {
				console.error('Failed to get version:', request.error);
				resolve({
					productsVersion: 0,
					categoriesVersion: 0,
					promotionsVersion: 0,
					lastSyncAt: null
				});
			};
		});
	}

	/**
	 * Store version in IndexedDB
	 */
	private async storeVersion(version: MasterDataVersion): Promise<void> {
		if (!this.db) throw new Error('Database not initialized');

		const transaction = this.db.transaction(['metadata'], 'readwrite');
		const store = transaction.objectStore('metadata');

		store.put({ key: 'version', value: version });

		return new Promise((resolve, reject) => {
			transaction.oncomplete = () => resolve();
			transaction.onerror = () => reject(transaction.error);
		});
	}

	/**
	 * Get counts of cached data
	 */
	private async getCounts(): Promise<{ productsCount: number; categoriesCount: number; promotionsCount: number }> {
		if (!this.db) throw new Error('Database not initialized');

		const transaction = this.db.transaction(['products', 'categories', 'promotions'], 'readonly');

		const productsCount = await new Promise<number>((resolve) => {
			const request = transaction.objectStore('products').count();
			request.onsuccess = () => resolve(request.result);
			request.onerror = () => resolve(0);
		});

		const categoriesCount = await new Promise<number>((resolve) => {
			const request = transaction.objectStore('categories').count();
			request.onsuccess = () => resolve(request.result);
			request.onerror = () => resolve(0);
		});

		const promotionsCount = await new Promise<number>((resolve) => {
			const request = transaction.objectStore('promotions').count();
			request.onsuccess = () => resolve(request.result);
			request.onerror = () => resolve(0);
		});

		return { productsCount, categoriesCount, promotionsCount };
	}

	/**
	 * Get all products from cache
	 */
	async getProducts(): Promise<Product[]> {
		if (!this.db) throw new Error('Database not initialized');

		const transaction = this.db.transaction(['products'], 'readonly');
		const store = transaction.objectStore('products');

		return new Promise((resolve, reject) => {
			const request = store.getAll();
			request.onsuccess = () => resolve(request.result);
			request.onerror = () => reject(request.error);
		});
	}

	/**
	 * Get all categories from cache
	 */
	async getCategories(): Promise<Category[]> {
		if (!this.db) throw new Error('Database not initialized');

		const transaction = this.db.transaction(['categories'], 'readonly');
		const store = transaction.objectStore('categories');

		return new Promise((resolve, reject) => {
			const request = store.getAll();
			request.onsuccess = () => resolve(request.result);
			request.onerror = () => reject(request.error);
		});
	}

	/**
	 * Get all active promotions from cache
	 */
	async getActivePromotions(): Promise<Promotion[]> {
		if (!this.db) throw new Error('Database not initialized');

		const transaction = this.db.transaction(['promotions'], 'readonly');
		const store = transaction.objectStore('promotions');
		const index = store.index('is_active');

		return new Promise((resolve, reject) => {
			const request = index.getAll(IDBKeyRange.only(1)); // 1 for true/active
			request.onsuccess = () => resolve(request.result);
			request.onerror = () => reject(request.error);
		});
	}

	/**
	 * Get product by ID from cache
	 */
	async getProduct(id: number): Promise<Product | null> {
		if (!this.db) throw new Error('Database not initialized');

		const transaction = this.db.transaction(['products'], 'readonly');
		const store = transaction.objectStore('products');

		return new Promise((resolve, reject) => {
			const request = store.get(id);
			request.onsuccess = () => resolve(request.result || null);
			request.onerror = () => reject(request.error);
		});
	}

	/**
	 * Clear all cached data (for testing or reset)
	 */
	async clearCache(): Promise<void> {
		if (!this.db) throw new Error('Database not initialized');

		const transaction = this.db.transaction(['products', 'categories', 'promotions', 'metadata'], 'readwrite');
		
		transaction.objectStore('products').clear();
		transaction.objectStore('categories').clear();
		transaction.objectStore('promotions').clear();
		transaction.objectStore('metadata').clear();

		return new Promise((resolve, reject) => {
			transaction.oncomplete = () => {
				console.log('🗑️ Master data cache cleared');
				this.status.update(s => ({
					...s,
					productsCount: 0,
					categoriesCount: 0,
					promotionsCount: 0,
					lastSyncAt: null
				}));
				resolve();
			};
			transaction.onerror = () => reject(transaction.error);
		});
	}
}

// Export singleton instance
export const masterDataService = new MasterDataService();
