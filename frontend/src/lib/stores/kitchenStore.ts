import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';
import { socketService, type SocketMode } from '$lib/services/socketService';
import { networkStatus, type ConnectionMode } from '$lib/services/networkService';

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
	useWebSocket: boolean; // Enable WebSocket mode
	useLocalSocket: boolean; // Connect to Local Sync Server
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
	useWebSocket: false, // Disabled by default, use HTTP Polling
	useLocalSocket: true, // Enable Local Socket by default for offline support
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
		
		// Add single order to column (for Socket.IO real-time updates)
		addOrder: (order: KitchenOrder, column: 'pending' | 'preparing' | 'ready') => {
			update(state => {
				// Check if order already exists
				const exists = state[column].some(o => o.id === order.id || o.order_number === order.order_number);
				if (exists) {
					console.log('Order already exists in', column, ':', order.order_number);
					return state;
				}
				
				return {
					...state,
					[column]: [...state[column], order],
				};
			});
		},
		
		// Update order in place (status change)
		updateOrder: (orderId: number, updates: Partial<KitchenOrder>) => {
			update(state => {
				const columns: Array<'pending' | 'preparing' | 'ready'> = ['pending', 'preparing', 'ready'];
				const newState = { ...state };
				
				for (const column of columns) {
					const index = newState[column].findIndex(o => o.id === orderId);
					if (index !== -1) {
						newState[column][index] = { ...newState[column][index], ...updates };
						break;
					}
				}
				
				return newState;
			});
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

/**
 * Kitchen Socket Manager
 * Handles dual-mode Socket.IO connections (Central + Local)
 */
class KitchenSocketManager {
	private isInitialized = false;
	
	/**
	 * Initialize Socket.IO connections based on config
	 */
	init(config: KitchenConfig) {
		if (this.isInitialized) {
			console.log('🔄 Socket already initialized, skipping...');
			return;
		}
		
		if (!config.isConfigured || !config.outletId) {
			console.warn('⚠️ Kitchen not configured, cannot initialize sockets');
			return;
		}
		
		console.log('🚀 Initializing Kitchen Socket Manager...');
		
		// Connect to Local Socket (always if enabled)
		if (config.useLocalSocket) {
			socketService.connectLocal();
		}
		
		// Connect to Central Socket (if WebSocket mode enabled and online)
		if (config.useWebSocket) {
			this.checkAndConnectCentral();
		}
		
		// Subscribe to outlet room
		socketService.subscribeOutlet(config.outletId);
		
		// Identify as kitchen display
		socketService.identify('kitchen');
		
		// Setup event listeners
		this.setupEventListeners();
		
		// Monitor network status for auto-switching
		this.monitorNetworkStatus(config);
		
		this.isInitialized = true;
		console.log('✅ Kitchen Socket Manager initialized');
	}
	
	/**
	 * Check network and connect to Central if online
	 */
	private async checkAndConnectCentral() {
		const status = get(networkStatus);
		if (status.isOnline) {
			console.log('🌐 Network online, connecting to Central Socket...');
			socketService.connectCentral();
		} else {
			console.log('🔴 Network offline, skipping Central Socket');
		}
	}
	
	/**
	 * Setup Socket.IO event listeners for kitchen orders
	 */
	private setupEventListeners() {
		// New order created
		socketService.on('order_created', (order: any) => {
			console.log('📦 Socket: New order received', order.order_number);
			
			// Convert to KitchenOrder format
			const kitchenOrder = this.convertToKitchenOrder(order);
			
			// Add to pending column
			kitchenOrders.addOrder(kitchenOrder, 'pending');
			
			// Play sound notification
			this.playNotificationSound();
		});
		
		// Order status updated
		socketService.on('order_updated', (update: any) => {
			console.log('🔄 Socket: Order updated', update.order_number, update.status);
			
			// Find and move order to appropriate column
			const currentState = get(kitchenOrders);
			const orderId = update.id;
			
			if (update.status === 'preparing') {
				kitchenOrders.moveOrder(orderId, 'pending', 'preparing');
			} else if (update.status === 'ready') {
				kitchenOrders.moveOrder(orderId, 'preparing', 'ready');
			} else if (update.status === 'served') {
				// Remove from ready column
				kitchenOrders.removeOrder(orderId, 'ready');
			}
		});
		
		// Order completed
		socketService.on('order_completed', (order: any) => {
			console.log('✅ Socket: Order completed', order.order_number);
			kitchenOrders.removeOrder(order.id, 'ready');
		});
		
		// Order cancelled
		socketService.on('order_cancelled', (order: any) => {
			console.log('❌ Socket: Order cancelled', order.order_number);
			
			// Remove from all columns
			kitchenOrders.removeOrder(order.id, 'pending');
			kitchenOrders.removeOrder(order.id, 'preparing');
			kitchenOrders.removeOrder(order.id, 'ready');
		});
	}
	
	/**
	 * Monitor network status for automatic failover
	 */
	private monitorNetworkStatus(config: KitchenConfig) {
		networkStatus.subscribe(status => {
			if (status.mode === 'online' && config.useWebSocket) {
				// Network restored, connect to Central if not already
				const socketState = get(socketService.getStatus());
				if (!socketState.centralConnected) {
					console.log('🟢 Network restored, reconnecting to Central Socket...');
					socketService.connectCentral();
					socketService.subscribeOutlet(config.outletId!);
				}
			} else if (status.mode === 'offline') {
				console.log('🟡 Network offline, relying on Local Socket only');
			}
		});
	}
	
	/**
	 * Convert API order format to KitchenOrder format
	 */
	private convertToKitchenOrder(order: any): KitchenOrder {
		return {
			id: order.id,
			order_number: order.order_number,
			status: order.status || 'pending',
			customer_name: order.customer?.name || order.customer_name || 'Guest',
			customer_phone: order.customer?.phone || order.customer_phone || '',
			table_number: order.table_number || '',
			notes: order.notes || '',
			items: order.items || [],
			total_amount: order.total_amount || '0',
			wait_time: order.wait_time || 0,
			is_urgent: order.is_urgent || false,
			source: order.source || 'kiosk',
			device_id: order.device_id || '',
			created_at: order.created_at || new Date().toISOString(),
			updated_at: order.updated_at || new Date().toISOString(),
		};
	}
	
	/**
	 * Play notification sound for new orders
	 */
	private playNotificationSound() {
		const config = get(kitchenConfig);
		if (!config.soundEnabled) return;
		
		try {
			// Play beep sound (Web Audio API)
			const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
			const oscillator = audioContext.createOscillator();
			const gainNode = audioContext.createGain();
			
			oscillator.connect(gainNode);
			gainNode.connect(audioContext.destination);
			
			oscillator.frequency.value = 800; // 800 Hz
			oscillator.type = 'sine';
			
			gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
			gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
			
			oscillator.start(audioContext.currentTime);
			oscillator.stop(audioContext.currentTime + 0.5);
		} catch (error) {
			console.warn('Failed to play notification sound:', error);
		}
	}
	
	/**
	 * Disconnect all sockets
	 */
	disconnect() {
		socketService.disconnect();
		this.isInitialized = false;
		console.log('🛑 Kitchen Socket Manager disconnected');
	}
}

// Singleton instance
export const kitchenSocketManager = new KitchenSocketManager();

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
