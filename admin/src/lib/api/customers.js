/**
 * API Client for Customers Management
 */

import { authFetch } from './auth';

const API_BASE = '/api';

/**
 * Get customers list
 * @param {Object} filters - Filter parameters
 * @returns {Promise<Object>} Paginated customers list
 */
export async function getCustomers(filters = {}) {
	const params = new URLSearchParams();

	if (filters.search) params.append('search', filters.search);
	if (filters.membership_tier) params.append('membership_tier', filters.membership_tier);
	if (filters.is_active !== undefined) params.append('is_active', filters.is_active);
	if (filters.gender) params.append('gender', filters.gender);
	if (filters.is_subscribed !== undefined) params.append('is_subscribed', filters.is_subscribed);
	if (filters.ordering) params.append('ordering', filters.ordering);
	if (filters.page) params.append('page', filters.page);
	if (filters.page_size) params.append('page_size', filters.page_size);

	const url = `${API_BASE}/admin/customers/${params.toString() ? `?${params.toString()}` : ''}`;
	const response = await authFetch(url);
	return response;
}

/**
 * Get customer statistics
 * @returns {Promise<Object>} Customer statistics
 */
export async function getCustomerStats() {
	const response = await authFetch(`${API_BASE}/admin/customers/stats/`);
	return response;
}

/**
 * Get customer by ID
 * @param {number} id - Customer ID
 * @returns {Promise<Object>} Customer detail
 */
export async function getCustomer(id) {
	const response = await authFetch(`${API_BASE}/admin/customers/${id}/`);
	return response;
}

/**
 * Create new customer
 * @param {Object} customerData - Customer data
 * @returns {Promise<Object>} Created customer
 */
export async function createCustomer(customerData) {
	const response = await authFetch(`${API_BASE}/admin/customers/`, {
		method: 'POST',
		body: JSON.stringify(customerData)
	});
	return response;
}

/**
 * Update customer
 * @param {number} id - Customer ID
 * @param {Object} customerData - Customer data to update
 * @returns {Promise<Object>} Updated customer
 */
export async function updateCustomer(id, customerData) {
	const response = await authFetch(`${API_BASE}/admin/customers/${id}/`, {
		method: 'PATCH',
		body: JSON.stringify(customerData)
	});
	return response;
}

/**
 * Delete customer (soft delete)
 * @param {number} id - Customer ID
 * @returns {Promise<void>}
 */
export async function deleteCustomer(id) {
	await authFetch(`${API_BASE}/admin/customers/${id}/`, {
		method: 'DELETE'
	});
}

/**
 * Bulk update customers
 * @param {number[]} customerIds - Array of customer IDs
 * @param {Object} updates - Updates to apply
 * @returns {Promise<Object>} Bulk update result
 */
export async function bulkUpdateCustomers(customerIds, updates) {
	const response = await authFetch(`${API_BASE}/admin/customers/bulk_update/`, {
		method: 'POST',
		body: JSON.stringify({
			customer_ids: customerIds,
			updates: updates
		})
	});
	return response;
}

/**
 * Add points to customer
 * @param {number} id - Customer ID
 * @param {number} points - Points to add
 * @param {string} reason - Reason for adding points
 * @returns {Promise<Object>} Result with new total
 */
export async function addCustomerPoints(id, points, reason = '') {
	const response = await authFetch(`${API_BASE}/admin/customers/${id}/add_points/`, {
		method: 'POST',
		body: JSON.stringify({ points, reason })
	});
	return response;
}

/**
 * Redeem customer points
 * @param {number} id - Customer ID
 * @param {number} points - Points to redeem
 * @param {string} reason - Reason for redemption
 * @returns {Promise<Object>} Result with new total
 */
export async function redeemCustomerPoints(id, points, reason = '') {
	const response = await authFetch(`${API_BASE}/admin/customers/${id}/redeem_points/`, {
		method: 'POST',
		body: JSON.stringify({ points, reason })
	});
	return response;
}

/**
 * Get top customers
 * @param {number} limit - Number of top customers to return
 * @returns {Promise<Array>} Top customers list
 */
export async function getTopCustomers(limit = 10) {
	const response = await authFetch(`${API_BASE}/admin/customers/top_customers/?limit=${limit}`);
	return response;
}

/**
 * Utility Functions
 */

/**
 * Get membership tier options
 * @returns {Array} Membership tier options
 */
export function getMembershipTierOptions() {
	return [
		{ value: 'regular', label: 'Regular' },
		{ value: 'silver', label: 'Silver' },
		{ value: 'gold', label: 'Gold' },
		{ value: 'platinum', label: 'Platinum' }
	];
}

/**
 * Get gender options
 * @returns {Array} Gender options
 */
export function getGenderOptions() {
	return [
		{ value: 'M', label: 'Male' },
		{ value: 'F', label: 'Female' },
		{ value: 'O', label: 'Other' }
	];
}

/**
 * Format membership tier with color
 * @param {string} tier - Membership tier
 * @returns {Object} Tier label and color class
 */
export function formatMembershipTier(tier) {
	const tiers = {
		regular: { label: 'Regular', colorClass: 'bg-gray-100 text-gray-800' },
		silver: { label: 'Silver', colorClass: 'bg-gray-300 text-gray-900' },
		gold: { label: 'Gold', colorClass: 'bg-yellow-100 text-yellow-800' },
		platinum: { label: 'Platinum', colorClass: 'bg-purple-100 text-purple-800' }
	};
	return tiers[tier] || tiers.regular;
}

/**
 * Format gender display
 * @param {string} gender - Gender code
 * @returns {string} Gender label
 */
export function formatGender(gender) {
	const genders = {
		M: 'Male',
		F: 'Female',
		O: 'Other'
	};
	return genders[gender] || '-';
}

/**
 * Format phone number
 * @param {string} phone - Phone number
 * @returns {string} Formatted phone
 */
export function formatPhone(phone) {
	if (!phone) return '-';
	// Format: +62 812-3456-7890
	if (phone.startsWith('+62')) {
		return phone.replace(/(\+62)(\d{3})(\d{4})(\d{4})/, '$1 $2-$3-$4');
	}
	return phone;
}

/**
 * Format currency
 * @param {number} amount - Amount
 * @returns {string} Formatted currency
 */
export function formatCurrency(amount) {
	if (amount === null || amount === undefined) return 'Rp 0';
	return new Intl.NumberFormat('id-ID', {
		style: 'currency',
		currency: 'IDR',
		minimumFractionDigits: 0,
		maximumFractionDigits: 0
	}).format(amount);
}

/**
 * Format date
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
export function formatDate(dateString) {
	if (!dateString) return '-';
	return new Date(dateString).toLocaleDateString('id-ID', {
		year: 'numeric',
		month: 'short',
		day: 'numeric'
	});
}

/**
 * Format date with time
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date with time
 */
export function formatDateTime(dateString) {
	if (!dateString) return '-';
	return new Date(dateString).toLocaleString('id-ID', {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit'
	});
}

/**
 * Get status badge class
 * @param {boolean} isActive - Active status
 * @returns {Object} Badge label and color class
 */
export function getStatusBadge(isActive) {
	return isActive
		? { label: 'Active', colorClass: 'bg-green-100 text-green-800' }
		: { label: 'Inactive', colorClass: 'bg-red-100 text-red-800' };
}

/**
 * Validate email format
 * @param {string} email - Email address
 * @returns {boolean} True if valid
 */
export function isValidEmail(email) {
	if (!email) return true; // Email is optional
	return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email);
}

/**
 * Validate phone format
 * @param {string} phone - Phone number
 * @returns {boolean} True if valid
 */
export function isValidPhone(phone) {
	if (!phone) return false; // Phone is required
	// Remove spaces and dashes
	const cleaned = phone.replace(/[\s-]/g, '');
	// Check if starts with + and rest is digits, or all digits
	return /^\+?\d+$/.test(cleaned);
}
