// Kiosk Store - Manages kiosk configuration and multi-outlet cart
import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';
import { ulid } from 'ulid';

// ===== KIOSK CONFIGURATION =====

export interface KioskConfig {
	storeCode: string | null;
	storeName: string | null;
	storeId: number | null;
	tenantName: string | null;
	tenantId: number | null;
	deviceId: string;
	isConfigured: boolean;
	enableMultiOutlet: boolean;
}

function createKioskConfig() {
	// Load from localStorage (only in browser)
	let stored: string | null = null;
	if (browser && typeof window !== 'undefined' && window.localStorage) {
		try {
			stored = localStorage.getItem('kiosk_config');
		} catch (e) {
			console.warn('Failed to load kiosk config from localStorage:', e);
		}
	}
	
	const defaultConfig: KioskConfig = {
		storeCode: null,
		storeName: null,
		storeId: null,
		tenantName: null,
		tenantId: null,
		deviceId: browser ? generateDeviceId() : 'KIOSK-TEMP',
		isConfigured: false,
		enableMultiOutlet: true
	};

	// If stored config exists, use it directly (don't merge with defaults)
	const initialConfig = stored ? JSON.parse(stored) : defaultConfig;
	
	// Ensure deviceId exists
	if (!initialConfig.deviceId && browser) {
		initialConfig.deviceId = generateDeviceId();
	}

	const { subscribe, set, update } = writable<KioskConfig>(initialConfig);

	return {
		subscribe,
		setStore: (storeCode: string, storeName: string, storeId: number, tenantName: string, tenantId: number, enableMultiOutlet: boolean = true) => {
			update(config => {
				const newConfig = {
					...config,
					storeCode,
					storeName,
					storeId,
					tenantName,
					tenantId,
					enableMultiOutlet,
					isConfigured: true
				};
				if (browser) {
					localStorage.setItem('kiosk_config', JSON.stringify(newConfig));
				}
				return newConfig;
			});
		},
		reset: () => {
			const newConfig = {
				...defaultConfig,
				deviceId: browser ? generateDeviceId() : 'KIOSK-TEMP'
			};
			if (browser) {
				localStorage.removeItem('kiosk_config');
			}
			set(newConfig);
		},
		update
	};
}

export const kioskConfig = createKioskConfig();

// ===== MULTI-OUTLET CART =====

/**
 * Cart Item Interface
 * 
 * ⚠️ IMPORTANT: All prices are SNAPSHOTS (frozen values)
 * - price: Product price at time of adding to cart
 * - modifiersPrice: Total modifier price at time of selection
 * - NEVER recalculate from product reference after adding to cart
 * - This ensures price consistency (F&B legal requirement)
 */
export interface CartItem {
	id: string; // Unique ID for cart item (ULID-based)
	productId: number;
	productName: string; // SNAPSHOT: Name frozen
	productSku: string;  // SNAPSHOT: SKU frozen
	price: number;       // SNAPSHOT: Product price frozen (not reference!)
	quantity: number;
	modifiers: any[];    // SNAPSHOT: Modifier details frozen
	modifiersPrice: number; // SNAPSHOT: Total modifier price frozen
	notes: string;
	image?: string;
}

export interface OutletCart {
	outletId: number;
	outletName: string;
	tenantName: string;
	tenantColor: string;
	items: CartItem[];
	subtotal: number;
	tax: number;
	serviceCharge: number;
	total: number;
	taxRate: number;
	serviceChargeRate: number;
}

export interface MultiCart {
	carts: { [outletId: number]: OutletCart };
	totalAmount: number;
	itemsCount: number;
	outletsCount: number;
}

function createMultiCart() {
	const { subscribe, set, update } = writable<MultiCart>({
		carts: {},
		totalAmount: 0,
		itemsCount: 0,
		outletsCount: 0
	});

	function calculateCart() {
		update(state => {
			let totalAmount = 0;
			let itemsCount = 0;

			Object.values(state.carts).forEach(cart => {
				// Calculate cart subtotal
				cart.subtotal = cart.items.reduce((sum, item) => {
					return sum + (item.price + item.modifiersPrice) * item.quantity;
				}, 0);

				// Calculate tax and service charge
				cart.tax = cart.subtotal * (cart.taxRate / 100);
				cart.serviceCharge = cart.subtotal * (cart.serviceChargeRate / 100);
				cart.total = cart.subtotal + cart.tax + cart.serviceCharge;

				totalAmount += cart.total;
				itemsCount += cart.items.reduce((sum, item) => sum + item.quantity, 0);
			});

			return {
				...state,
				totalAmount,
				itemsCount,
				outletsCount: Object.keys(state.carts).length
			};
		});
	}

	return {
		subscribe,
		
		addItem: (
			outletId: number,
			outletName: string,
			tenantName: string,
			tenantColor: string,
			taxRate: number,
			serviceChargeRate: number,
			product: any,
			quantity: number = 1,
			modifiers: any[] = [],
			notes: string = ''
		) => {
			update(state => {
				// Get or create outlet cart
				if (!state.carts[outletId]) {
					state.carts[outletId] = {
						outletId,
						outletName,
						tenantName,
						tenantColor,
						items: [],
						subtotal: 0,
						tax: 0,
						serviceCharge: 0,
						total: 0,
						taxRate,
						serviceChargeRate
					};
				}

				const cart = state.carts[outletId];

				// Calculate modifiers price
				const modifiersPrice = modifiers.reduce((sum, mod) => sum + (mod.price || 0), 0);

				// Check if exact item exists (same product, modifiers, notes)
				const existingItem = cart.items.find(
					item =>
						item.productId === product.id &&
						item.notes === notes &&
						JSON.stringify(item.modifiers) === JSON.stringify(modifiers)
				);

				if (existingItem) {
					// Update quantity
					existingItem.quantity += quantity;
				} else {
					// Add new item with ULID-based cart item ID
					const cartItem: CartItem = {
						id: `${outletId}-${product.id}-${ulid()}`,
						productId: product.id,
						productName: product.name,
						productSku: product.sku,
						price: product.price,
						quantity,
						modifiers,
						modifiersPrice,
						notes,
						image: product.image
					};
					cart.items.push(cartItem);
				}

				return state;
			});

			calculateCart();
		},

		updateQuantity: (outletId: number, cartItemId: string, quantity: number) => {
			update(state => {
				const cart = state.carts[outletId];
				if (!cart) return state;

				const item = cart.items.find(i => i.id === cartItemId);
				if (item) {
					if (quantity <= 0) {
						// Remove item
						cart.items = cart.items.filter(i => i.id !== cartItemId);
						
						// Remove cart if empty
						if (cart.items.length === 0) {
							delete state.carts[outletId];
						}
					} else {
						item.quantity = quantity;
					}
				}

				return state;
			});

			calculateCart();
		},

		removeItem: (outletId: number, cartItemId: string) => {
			update(state => {
				const cart = state.carts[outletId];
				if (!cart) return state;

				cart.items = cart.items.filter(i => i.id !== cartItemId);

				// Remove cart if empty
				if (cart.items.length === 0) {
					delete state.carts[outletId];
				}

				return state;
			});

			calculateCart();
		},

		clearOutlet: (outletId: number) => {
			update(state => {
				delete state.carts[outletId];
				return state;
			});

			calculateCart();
		},

		clearAll: () => {
			set({
				carts: {},
				totalAmount: 0,
				itemsCount: 0,
				outletsCount: 0
			});
		},

		getCheckoutData: () => {
			const state = get({ subscribe });
			const config = get(kioskConfig);

			// ✅ SNAPSHOT STRATEGY: Freeze prices at order creation
			return {
				store_id: config.storeId,
				customer_name: '',
				customer_phone: '',
				source: 'kiosk',
				device_id: config.deviceId,
				session_id: generateSessionId(),
				carts: Object.values(state.carts).map(cart => ({
					outlet_id: cart.outletId,
					items: cart.items.map(item => ({
						product_id: item.productId,
						product_name: item.productName, // SNAPSHOT: Name at order time
						product_sku: item.productSku,   // SNAPSHOT: SKU at order time
						price: item.price,              // SNAPSHOT: Price frozen (not reference!)
						quantity: item.quantity,
						modifiers: item.modifiers.map(mod => ({
							// SNAPSHOT: Modifier details frozen
							id: mod.id,
							name: mod.name,
							price: mod.price || 0,      // SNAPSHOT: Modifier price frozen
							price_adjustment: mod.price_adjustment || 0
						})),
						modifiers_price: item.modifiersPrice, // SNAPSHOT: Total modifiers price
						notes: item.notes,
						subtotal: (item.price + item.modifiersPrice) * item.quantity // SNAPSHOT: Calculated subtotal
					}))
				}))
			};
		}
	};
}

export const multiCart = createMultiCart();

// ===== SELECTED OUTLET (for browsing menu) =====

export interface SelectedOutlet {
	id: number | null;
	name: string | null;
	tenantId: number | null;
	tenantName: string | null;
	tenantColor: string | null;
	taxRate: number;
	serviceChargeRate: number;
}

export const selectedOutlet = writable<SelectedOutlet>({
	id: null,
	name: null,
	tenantId: null,
	tenantName: null,
	tenantColor: null,
	taxRate: 10,
	serviceChargeRate: 5
});

// ===== HELPER FUNCTIONS =====

function generateDeviceId(): string {
	if (!browser || typeof window === 'undefined' || !window.localStorage) {
		return 'KIOSK-TEMP';
	}
	
	try {
		const stored = localStorage.getItem('kiosk_device_id');
		if (stored) return stored;

		// Use ULID for unique, sortable device ID
		const newId = `KIOSK-${ulid()}`;
		localStorage.setItem('kiosk_device_id', newId);
		return newId;
	} catch (e) {
		console.warn('Failed to access localStorage for device ID:', e);
		return 'KIOSK-TEMP';
	}
}

function generateSessionId(): string {
	// Use ULID for session ID (sortable, unique)
	return `SESS-${ulid()}`;
}

// ===== DERIVED STORES =====

export const isKioskConfigured = derived(
	kioskConfig,
	$config => $config.isConfigured
);

export const hasItemsInCart = derived(
	multiCart,
	$cart => $cart.itemsCount > 0
);

export const cartSummary = derived(
	multiCart,
	$cart => ({
		outlets: Object.keys($cart.carts).length,
		items: $cart.itemsCount,
		total: $cart.totalAmount
	})
);
