import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';

export interface KitchenConfig {
	isConfigured: boolean;
	tenantId: number | null;
	tenantName: string;
	storeId: number | null;
	storeName: string;
	outletId: number | null;
	outletName: string;
	deviceId: string;
	soundEnabled: boolean;
}

export interface KitchenOrder {
	id: number;
	order_number: string;
	status: string;
	customer_name: string;
	customer_phone: string;
	table_number: string;
	notes: string;
	items: KitchenOrderItem[];
	total_amount: string;
	wait_time: number;
	is_urgent: boolean;
	source: string; // 'kiosk' | 'web'
	device_id: string;
	created_at: string;
	updated_at: string;
}

export interface KitchenOrderItem {
	id: number;
	product_name: string;
	quantity: number;
	notes: string;
	modifiers_display: Array<{ name: string; quantity: number }>;
}

export interface KitchenStats {
	pending_count: number;
	preparing_count: number;
	ready_count: number;
	completed_today: number;
	avg_prep_time: number;
	total_orders_today: number;
}

const STORAGE_KEY = 'kitchen-config';

// Default config
const defaultConfig: KitchenConfig = {
	isConfigured: false,
	tenantId: null,
	tenantName: '',
	storeId: null,
	storeName: '',
	outletId: null,
	outletName: '',
	deviceId: '',
	soundEnabled: true,
};

// Load from localStorage
function loadConfig(): KitchenConfig {
	if (!browser) return defaultConfig;
	
	try {
		const stored = localStorage.getItem(STORAGE_KEY);
		if (stored) {
			const config = JSON.parse(stored);
			return { ...defaultConfig, ...config };
		}
	} catch (error) {
		console.error('Failed to load kitchen config:', error);
	}
	
	return defaultConfig;
}

// Save to localStorage
function saveConfig(config: KitchenConfig) {
	if (!browser) return;
	
	try {
		localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
	} catch (error) {
		console.error('Failed to save kitchen config:', error);
	}
}

// Kitchen config store
function createKitchenConfigStore() {
	const { subscribe, set, update } = writable<KitchenConfig>(loadConfig());

	return {
		subscribe,
		
		// Set kitchen configuration
		setConfig: (config: Partial<KitchenConfig>) => {
			update(current => {
				const newConfig = {
					...current,
					...config,
					isConfigured: true,
				};
				saveConfig(newConfig);
				return newConfig;
			});
		},
		
		// Toggle sound
		toggleSound: () => {
			update(current => {
				const newConfig = { ...current, soundEnabled: !current.soundEnabled };
				saveConfig(newConfig);
				return newConfig;
			});
		},
		
		// Clear configuration
		clear: () => {
			if (browser) {
				localStorage.removeItem(STORAGE_KEY);
			}
			set(defaultConfig);
		},
		
		// Reset
		reset: () => {
			if (browser) {
				localStorage.removeItem(STORAGE_KEY);
			}
			set(defaultConfig);
		}
	};
}

// Kitchen orders store (pending, preparing, ready)
function createKitchenOrdersStore() {
	const { subscribe, set, update } = writable<{
		pending: KitchenOrder[];
		preparing: KitchenOrder[];
		ready: KitchenOrder[];
		loading: boolean;
		error: string | null;
	}>({
		pending: [],
		preparing: [],
		ready: [],
		loading: false,
		error: null,
	});

	return {
		subscribe,
		
		setPending: (orders: KitchenOrder[]) => {
			update(state => ({ ...state, pending: orders }));
		},
		
		setPreparing: (orders: KitchenOrder[]) => {
			update(state => ({ ...state, preparing: orders }));
		},
		
		setReady: (orders: KitchenOrder[]) => {
			update(state => ({ ...state, ready: orders }));
		},
		
		setAll: (pending: KitchenOrder[], preparing: KitchenOrder[], ready: KitchenOrder[]) => {
			update(state => ({ ...state, pending, preparing, ready }));
		},
		
		setLoading: (loading: boolean) => {
			update(state => ({ ...state, loading }));
		},
		
		setError: (error: string | null) => {
			update(state => ({ ...state, error }));
		},
		
		// Move order from one column to another
		moveOrder: (orderId: number, from: 'pending' | 'preparing' | 'ready', to: 'pending' | 'preparing' | 'ready') => {
			update(state => {
				const order = state[from].find(o => o.id === orderId);
				if (!order) return state;
				
				return {
					...state,
					[from]: state[from].filter(o => o.id !== orderId),
					[to]: [...state[to], { ...order, status: to }],
				};
			});
		},
		
		// Remove order from column
		removeOrder: (orderId: number, column: 'pending' | 'preparing' | 'ready') => {
			update(state => ({
				...state,
				[column]: state[column].filter(o => o.id !== orderId),
			}));
		},
		
		clear: () => {
			set({
				pending: [],
				preparing: [],
				ready: [],
				loading: false,
				error: null,
			});
		}
	};
}

// Kitchen stats store
function createKitchenStatsStore() {
	const { subscribe, set } = writable<KitchenStats>({
		pending_count: 0,
		preparing_count: 0,
		ready_count: 0,
		completed_today: 0,
		avg_prep_time: 0,
		total_orders_today: 0,
	});

	return {
		subscribe,
		setStats: (stats: KitchenStats) => set(stats),
	};
}

export const kitchenConfig = createKitchenConfigStore();
export const kitchenOrders = createKitchenOrdersStore();
export const kitchenStats = createKitchenStatsStore();

// Derived stores
export const isKitchenConfigured = derived(
	kitchenConfig,
	$config => $config.isConfigured && $config.outletId !== null
);
