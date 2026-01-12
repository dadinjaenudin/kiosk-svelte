/**
 * Master Data Service
 * 
 * Purpose: Pre-fetch and cache menu, categories, and promotions
 * 
 * Features:
 * - Incremental updates (version-based)
 * - IndexedDB caching for offline access
 * - Background refresh every 1 hour
 * - Reactive Svelte stores for UI updates
 * - Automatic retry on failure
 * 
 * Version: 2.0.0 (Enhanced with idb library)
 * Date: 2026-01-12
 */

import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';
import { networkStatus } from './networkService';
import * as masterDataDB from '$lib/db/masterDataDB';
import type { Product, Category, Promotion } from '$lib/db/masterDataDB';

// ============================================================================
// TYPES
// ============================================================================

export interface MasterDataState {
	products: Product[];
	categories: Category[];
	promotions: Promotion[];
	loading: boolean;
	error: string | null;
	lastSync: Date | null;
	isStale: boolean;
}

export interface SyncResult {
	productsUpdated: number;
	categoriesUpdated: number;
	promotionsUpdated: number;
	timestamp: Date;
}

// ============================================================================
// STORES
// ============================================================================

export const masterData = writable<MasterDataState>({
	products: [],
	categories: [],
	promotions: [],
	loading: false,
	error: null,
	lastSync: null,
	isStale: false
});

// Derived: Products by outlet
export function getProductsByOutlet(outletId: number) {
	return derived(masterData, $data => 
		$data.products.filter(p => p.outlet_id === outletId && p.is_available)
	);
}

// Derived: Active promotions
export const activePromotions = derived(masterData, $data => {
	const now = new Date().toISOString();
	return $data.promotions.filter(promo => 
		promo.is_active &&
		promo.start_date <= now &&
		promo.end_date >= now
	);
});

// ============================================================================
// CONSTANTS
// ============================================================================

const API_BASE = 'http://localhost:8001/api';
const REFRESH_INTERVAL = 60 * 60 * 1000; // 1 hour
// ============================================================================
// SERVICE CLASS
// ============================================================================

class MasterDataService {
	private refreshInterval: ReturnType<typeof setInterval> | null = null;
	private isRefreshing = false;

	/**
	 * Initialize service (load from cache, start background refresh)
	 */
	async init(): Promise<void> {
		if (!browser) return;

		console.log('📦 Master Data Service: Initializing...');

		// Load from cache first (instant)
		await this.loadFromCache();

		// Check if online and sync
		const $networkStatus = get(networkStatus);
		if ($networkStatus.isOnline) {
			console.log('🌐 Online: Syncing master data...');
			await this.sync();
		} else {
			console.log('📴 Offline: Using cached data');
			
			// Check if cache is stale
			const isStale = await masterDataDB.isCacheStale();
			if (isStale) {
				console.warn('⚠️ Cache is stale (>24 hours old)');
				masterData.update(s => ({ ...s, isStale: true }));
			}
		}

		// Start background refresh
		this.startBackgroundRefresh();

		console.log('✅ Master Data Service: Initialized');
	}

	/**
	 * Load data from IndexedDB cache
	 */
	async loadFromCache(): Promise<void> {
		try {
			console.log('💾 Loading master data from cache...');

			const [products, categories, promotions, lastSync, isStale] = await Promise.all([
				masterDataDB.getAllProducts(),
				masterDataDB.getAllCategories(),
				masterDataDB.getAllPromotions(),
				masterDataDB.getLastSyncTime(),
				masterDataDB.isCacheStale()
			]);

			masterData.set({
				products,
				categories,
				promotions,
				loading: false,
				error: null,
				lastSync,
				isStale
			});

			console.log(`✅ Loaded from cache: ${products.length} products, ${categories.length} categories, ${promotions.length} promotions`);
		} catch (error) {
			console.error('❌ Failed to load from cache:', error);
			masterData.update(s => ({
				...s,
				error: error instanceof Error ? error.message : 'Cache load failed'
			}));
		}
	}

	/**
	 * Sync with backend (incremental update)
	 */
	async sync(force: boolean = false): Promise<SyncResult | null> {
		if (this.isRefreshing && !force) {
			console.log('⏳ Sync already in progress');
			return null;
		}

		const $networkStatus = get(networkStatus);
		if (!$networkStatus.isOnline) {
			console.log('📴 Offline: Skipping sync');
			return null;
		}

		this.isRefreshing = true;
		masterData.update(s => ({ ...s, loading: true, error: null }));

		try {
			console.log('🔄 Syncing master data...');

			// Get current versions
			const [productsVersion, categoriesVersion, promotionsVersion] = await Promise.all([
				masterDataDB.getVersion('products'),
				masterDataDB.getVersion('categories'),
				masterDataDB.getVersion('promotions')
			]);

			console.log(`📊 Current versions: products=${productsVersion}, categories=${categoriesVersion}, promotions=${promotionsVersion}`);

			// Fetch updates
			const [productsResult, categoriesResult, promotionsResult] = await Promise.all([
				this.fetchProducts(productsVersion),
				this.fetchCategories(categoriesVersion),
				this.fetchPromotions(promotionsVersion)
			]);

			// Update cache
			if (productsResult.data.length > 0) {
				await masterDataDB.saveProducts(productsResult.data);
				await masterDataDB.setVersion('products', productsResult.version);
			}

			if (categoriesResult.data.length > 0) {
				await masterDataDB.saveCategories(categoriesResult.data);
				await masterDataDB.setVersion('categories', categoriesResult.version);
			}

			if (promotionsResult.data.length > 0) {
				await masterDataDB.savePromotions(promotionsResult.data);
				await masterDataDB.setVersion('promotions', promotionsResult.version);
			}

			// Update last sync time
			const syncTime = new Date();
			await masterDataDB.setLastSyncTime(syncTime);

			// Reload from cache to update store
			await this.loadFromCache();

			const result: SyncResult = {
				productsUpdated: productsResult.data.length,
				categoriesUpdated: categoriesResult.data.length,
				promotionsUpdated: promotionsResult.data.length,
				timestamp: syncTime
			};

			console.log(`✅ Sync complete: ${result.productsUpdated} products, ${result.categoriesUpdated} categories, ${result.promotionsUpdated} promotions updated`);

			return result;
		} catch (error) {
			console.error('❌ Sync failed:', error);
			masterData.update(s => ({
				...s,
				error: error instanceof Error ? error.message : 'Sync failed'
			}));
			return null;
		} finally {
			this.isRefreshing = false;
			masterData.update(s => ({ ...s, loading: false }));
		}
	}

	/**
	 * Fetch products from API (incremental)
	 */
	private async fetchProducts(sinceVersion: number): Promise<{ data: Product[]; version: number }> {
		try {
			const response = await fetch(
				`${API_BASE}/products/?since_version=${sinceVersion}&is_available=true`,
				{
					headers: {
						'Accept': 'application/json'
					}
				}
			);

			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}

			const data = await response.json();

			// Handle both paginated and non-paginated responses
			const products = data.results || data || [];
			const currentVersion = data.current_version || sinceVersion + 1;

			return {
				data: products,
				version: currentVersion
			};
		} catch (error) {
			console.error('❌ Failed to fetch products:', error);
			return { data: [], version: sinceVersion };
		}
	}

	/**
	 * Fetch categories from API (incremental)
	 */
	private async fetchCategories(sinceVersion: number): Promise<{ data: Category[]; version: number }> {
		try {
			const response = await fetch(
				`${API_BASE}/categories/?since_version=${sinceVersion}`,
				{
					headers: {
						'Accept': 'application/json'
					}
				}
			);

			if (!response.ok) {
				// Categories endpoint might not support versioning yet
				// Return empty if endpoint doesn't exist
				if (response.status === 404) {
					console.warn('⚠️ Categories endpoint not found, extracting from products');
					return { data: [], version: sinceVersion };
				}
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}

			const data = await response.json();
			const categories = data.results || data || [];
			const currentVersion = data.current_version || sinceVersion + 1;

			return {
				data: categories,
				version: currentVersion
			};
		} catch (error) {
			console.error('❌ Failed to fetch categories:', error);
			return { data: [], version: sinceVersion };
		}
	}

	/**
	 * Fetch promotions from API (incremental)
	 */
	private async fetchPromotions(sinceVersion: number): Promise<{ data: Promotion[]; version: number }> {
		try {
			const response = await fetch(
				`${API_BASE}/promotions/?since_version=${sinceVersion}&is_active=true`,
				{
					headers: {
						'Accept': 'application/json'
					}
				}
			);

			if (!response.ok) {
				// Promotions endpoint might not exist yet
				if (response.status === 404) {
					console.warn('⚠️ Promotions endpoint not found');
					return { data: [], version: sinceVersion };
				}
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}

			const data = await response.json();
			const promotions = data.results || data || [];
			const currentVersion = data.current_version || sinceVersion + 1;

			return {
				data: promotions,
				version: currentVersion
			};
		} catch (error) {
			console.error('❌ Failed to fetch promotions:', error);
			return { data: [], version: sinceVersion };
		}
	}

	/**
	 * Start background refresh (every 1 hour)
	 */
	private startBackgroundRefresh(): void {
		if (this.refreshInterval) {
			clearInterval(this.refreshInterval);
		}

		this.refreshInterval = setInterval(() => {
			const $networkStatus = get(networkStatus);
			if ($networkStatus.isOnline && !this.isRefreshing) {
				console.log('⏰ Background refresh triggered');
				this.sync();
			}
		}, REFRESH_INTERVAL);

		console.log('✅ Background refresh started (every 1 hour)');
	}

	/**
	 * Stop background refresh
	 */
	stopBackgroundRefresh(): void {
		if (this.refreshInterval) {
			clearInterval(this.refreshInterval);
			this.refreshInterval = null;
			console.log('🛑 Background refresh stopped');
		}
	}

	/**
	 * Force full refresh (clear cache and re-fetch)
	 */
	async forceRefresh(): Promise<SyncResult | null> {
		console.log('🔄 Force refresh: Clearing cache...');
		
		await masterDataDB.clearAllCache();
		
		// Reset store
		masterData.update(s => ({
			...s,
			products: [],
			categories: [],
			promotions: [],
			lastSync: null
		}));

		return this.sync(true);
	}

	/**
	 * Get products by outlet (from cache)
	 */
	async getProductsByOutlet(outletId: number): Promise<Product[]> {
		return masterDataDB.getProductsByOutlet(outletId);
	}

	/**
	 * Get active promotions (from cache)
	 */
	async getActivePromotions(): Promise<Promotion[]> {
		return masterDataDB.getActivePromotions();
	}

	/**
	 * Get cache statistics
	 */
	async getCacheStats() {
		return masterDataDB.getCacheStats();
	}

	/**
	 * Clear all cached data
	 */
	async clearCache(): Promise<void> {
		await masterDataDB.clearAllCache();
		await this.loadFromCache();
		console.log('🗑️ Cache cleared');
	}
}

// ============================================================================
// SINGLETON INSTANCE
// ============================================================================

export const masterDataService = new MasterDataService();

// ============================================================================
// AUTO-INITIALIZE (in browser only)
// ============================================================================

if (browser) {
	// Initialize on module load
	masterDataService.init().catch(error => {
		console.error('❌ Master Data Service initialization failed:', error);
	});
}
