/**
 * Cart Store - Reactive cart state management
 */
import { writable, derived } from 'svelte/store';
import { getCartItems, addToCart as dbAddToCart, updateCartItem, removeFromCart, clearCart as dbClearCart } from '$db';

// Cart items store
export const cartItems = writable([]);

// Cart totals (derived)
export const cartTotals = derived(cartItems, ($cartItems) => {
	const subtotal = $cartItems.reduce((sum, item) => {
		const itemTotal = item.product_price * item.quantity;
		const modifiersTotal = calculateModifiersTotal(item.modifiers);
		return sum + itemTotal + (modifiersTotal * item.quantity);
	}, 0);
	
	const tax = subtotal * 0.10; // 10% tax
	const serviceCharge = subtotal * 0.05; // 5% service charge
	const total = subtotal + tax + serviceCharge;
	
	return {
		subtotal: subtotal.toFixed(2),
		tax: tax.toFixed(2),
		serviceCharge: serviceCharge.toFixed(2),
		total: total.toFixed(2),
		itemCount: $cartItems.reduce((sum, item) => sum + item.quantity, 0)
	};
});

function calculateModifiersTotal(modifiersJson) {
	try {
		const modifiers = typeof modifiersJson === 'string' ? JSON.parse(modifiersJson) : modifiersJson;
		return modifiers.reduce((sum, mod) => sum + (parseFloat(mod.price_adjustment) || 0), 0);
	} catch (e) {
		return 0;
	}
}

/**
 * Load cart from IndexedDB
 */
export async function loadCart() {
	const items = await getCartItems();
	cartItems.set(items);
}

/**
 * Add product to cart
 */
export async function addProductToCart(product, quantity = 1, modifiers = [], notes = '') {
	try {
		const id = await dbAddToCart(product, quantity, modifiers, notes);
		await loadCart();
		return id;
	} catch (error) {
		console.error('Error adding to cart:', error);
		throw error;
	}
}

/**
 * Update cart item quantity
 */
export async function updateQuantity(itemId, newQuantity) {
	if (newQuantity <= 0) {
		return await removeCartItem(itemId);
	}
	
	await updateCartItem(itemId, { quantity: newQuantity });
	await loadCart();
}

/**
 * Remove item from cart
 */
export async function removeCartItem(itemId) {
	await removeFromCart(itemId);
	await loadCart();
}

/**
 * Clear entire cart
 */
export async function clearAllCart() {
	await dbClearCart();
	cartItems.set([]);
}
