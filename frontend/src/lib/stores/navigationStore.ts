import { writable, derived } from 'svelte/store';
import { goto } from '$app/navigation';

export interface NavigationState {
	currentPath: string;
	breadcrumbs: Array<{ label: string; path: string }>;
	canGoBack: boolean;
	showCartBadge: boolean;
	cartItemCount: number;
}

// Session timeout configuration
const SESSION_TIMEOUT_MS = 15 * 60 * 1000; // 15 minutes
const IDLE_TIMEOUT_MS = 2 * 60 * 1000; // 2 minutes for idle screen

let sessionTimeoutId: number | null = null;
let idleTimeoutId: number | null = null;
let lastActivityTime = Date.now();

// Navigation state store
function createNavigationStore() {
	const { subscribe, set, update } = writable<NavigationState>({
		currentPath: '/kiosk',
		breadcrumbs: [],
		canGoBack: false,
		showCartBadge: true,
		cartItemCount: 0
	});

	return {
		subscribe,
		
		// Update current path and breadcrumbs
		setCurrentPath: (path: string) => {
			update(state => {
				const breadcrumbs = generateBreadcrumbs(path);
				return {
					...state,
					currentPath: path,
					breadcrumbs,
					canGoBack: breadcrumbs.length > 1
				};
			});
		},
		
		// Update cart item count
		setCartItemCount: (count: number) => {
			update(state => ({ ...state, cartItemCount: count }));
		},
		
		// Go back with confirmation if cart has items
		goBack: async (cartItemCount: number = 0) => {
			if (cartItemCount > 0) {
				const confirmed = confirm('You have items in your cart. Are you sure you want to go back?');
				if (!confirmed) return false;
			}
			
			window.history.back();
			return true;
		},
		
		// Clear navigation state
		reset: () => {
			set({
				currentPath: '/kiosk',
				breadcrumbs: [],
				canGoBack: false,
				showCartBadge: true,
				cartItemCount: 0
			});
		}
	};
}

// Generate breadcrumbs from path
function generateBreadcrumbs(path: string): Array<{ label: string; path: string }> {
	const segments = path.split('/').filter(Boolean);
	const breadcrumbs: Array<{ label: string; path: string }> = [];
	
	if (segments.length === 0) return breadcrumbs;
	
	// Always start with home/kiosk
	breadcrumbs.push({ label: 'Home', path: '/kiosk' });
	
	let currentPath = '';
	segments.forEach((segment, index) => {
		currentPath += '/' + segment;
		
		// Skip the first 'kiosk' segment since we already added home
		if (segment === 'kiosk' && index === 0) return;
		
		// Map segment to readable label
		let label = segment.charAt(0).toUpperCase() + segment.slice(1);
		
		// Special cases
		if (segment === 'products') label = 'Browse Products';
		if (segment === 'cart') label = 'Shopping Cart';
		if (segment === 'checkout') label = 'Checkout';
		if (segment === 'success') label = 'Order Complete';
		if (segment === 'idle') label = 'Welcome';
		
		// Don't add dynamic segments (UUIDs, group numbers, etc)
		if (segment.length > 15 && segment.includes('-')) return;
		
		breadcrumbs.push({ label, path: currentPath });
	});
	
	return breadcrumbs;
}

// Session management
export const sessionManager = {
	// Record user activity
	recordActivity: () => {
		lastActivityTime = Date.now();
		sessionManager.resetSessionTimeout();
		sessionManager.resetIdleTimeout();
	},
	
	// Start session timeout (15 minutes)
	startSessionTimeout: () => {
		sessionManager.clearSessionTimeout();
		sessionTimeoutId = window.setTimeout(() => {
			alert('Your session has expired due to inactivity. Returning to home screen.');
			sessionManager.clearSession();
			goto('/kiosk/idle');
		}, SESSION_TIMEOUT_MS);
	},
	
	// Reset session timeout
	resetSessionTimeout: () => {
		if (sessionTimeoutId) {
			clearTimeout(sessionTimeoutId);
		}
		sessionManager.startSessionTimeout();
	},
	
	// Clear session timeout
	clearSessionTimeout: () => {
		if (sessionTimeoutId) {
			clearTimeout(sessionTimeoutId);
			sessionTimeoutId = null;
		}
	},
	
	// Start idle timeout (2 minutes)
	startIdleTimeout: () => {
		sessionManager.clearIdleTimeout();
		idleTimeoutId = window.setTimeout(() => {
			// Only go to idle if not already on a critical page (checkout, success)
			const currentPath = window.location.pathname;
			if (!currentPath.includes('checkout') && !currentPath.includes('success')) {
				goto('/kiosk/idle');
			}
		}, IDLE_TIMEOUT_MS);
	},
	
	// Reset idle timeout
	resetIdleTimeout: () => {
		if (idleTimeoutId) {
			clearTimeout(idleTimeoutId);
		}
		sessionManager.startIdleTimeout();
	},
	
	// Clear idle timeout
	clearIdleTimeout: () => {
		if (idleTimeoutId) {
			clearTimeout(idleTimeoutId);
			idleTimeoutId = null;
		}
	},
	
	// Clear entire session (called on order completion or session expiry)
	clearSession: () => {
		sessionManager.clearSessionTimeout();
		sessionManager.clearIdleTimeout();
		
		// Clear cart and kiosk state
		if (typeof window !== 'undefined') {
			// Will be implemented by components that use this
			window.dispatchEvent(new CustomEvent('clear-session'));
		}
	},
	
	// Initialize session tracking
	initialize: () => {
		if (typeof window === 'undefined') return;
		
		// Track mouse movements, clicks, touches, keyboard
		const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
		
		activityEvents.forEach(event => {
			window.addEventListener(event, () => {
				sessionManager.recordActivity();
			}, { passive: true });
		});
		
		// Start timers
		sessionManager.startSessionTimeout();
		sessionManager.startIdleTimeout();
	},
	
	// Get time since last activity (for debugging)
	getTimeSinceLastActivity: () => {
		return Date.now() - lastActivityTime;
	}
};

export const navigationStore = createNavigationStore();

// Derived store for showing back button
export const showBackButton = derived(
	navigationStore,
	$nav => $nav.canGoBack && $nav.currentPath !== '/kiosk/idle'
);
