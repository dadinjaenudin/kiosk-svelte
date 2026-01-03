/**
 * API Client for Reports
 */
import { authFetch } from './auth';

const BASE_URL = '/api/admin/reports';

/**
 * Get sales summary
 */
export async function getSalesSummary(period = '30days', startDate = null, endDate = null, tenantId = null) {
	const params = new URLSearchParams({ period });
	if (startDate && endDate) {
		params.append('start_date', startDate);
		params.append('end_date', endDate);
	}
	if (tenantId) {
		params.append('tenant', tenantId);
	}
	return authFetch(`${BASE_URL}/sales_summary/?${params}`);
}

/**
 * Get sales by period (day/week/month)
 */
export async function getSalesByPeriod(
	period = '30days',
	groupBy = 'day',
	startDate = null,
	endDate = null,
	tenantId = null
) {
	const params = new URLSearchParams({ period, group_by: groupBy });
	if (startDate && endDate) {
		params.append('start_date', startDate);
		params.append('end_date', endDate);
	}
	if (tenantId) {
		params.append('tenant', tenantId);
	}
	return authFetch(`${BASE_URL}/sales_by_period/?${params}`);
}

/**
 * Get top selling products
 */
export async function getTopProducts(period = '30days', limit = 10, tenantId = null) {
	const params = new URLSearchParams({ period, limit: limit.toString() });
	if (tenantId) {
		params.append('tenant', tenantId);
	}
	return authFetch(`${BASE_URL}/top_products/?${params}`);
}

/**
 * Get top selling categories
 */
export async function getTopCategories(period = '30days', tenantId = null) {
	const params = new URLSearchParams({ period });
	if (tenantId) {
		params.append('tenant', tenantId);
	}
	return authFetch(`${BASE_URL}/top_categories/?${params}`);
}

/**
 * Get sales by category (for pie chart)
 */
export async function getSalesByCategory(period = '30days') {
	const params = new URLSearchParams({ period });
	return authFetch(`${BASE_URL}/sales_by_category/?${params}`);
}

/**
 * Get customer statistics
 */
export async function getCustomerStats(period = '30days', tenantId = null) {
	const params = new URLSearchParams({ period });
	if (tenantId) {
		params.append('tenant', tenantId);
	}
	return authFetch(`${BASE_URL}/customer_stats/?${params}`);
}

/**
 * Get order statistics
 */
export async function getOrderStats(period = '30days', tenantId = null) {
	const params = new URLSearchParams({ period });
	if (tenantId) {
		params.append('tenant', tenantId);
	}
	return authFetch(`${BASE_URL}/order_stats/?${params}`);
}

/**
 * Get revenue trend (for line chart)
 */
export async function getRevenueTrend(period = '30days', groupBy = 'day') {
	return getSalesByPeriod(period, groupBy);
}

/**
 * Get payment method breakdown
 */
export async function getPaymentMethods(period = '30days', tenantId = null) {
	const params = new URLSearchParams({ period });
	if (tenantId) {
		params.append('tenant', tenantId);
	}
	return authFetch(`${BASE_URL}/payment_methods/?${params}`);
}

/**
 * Get hourly sales
 */
export async function getHourlySales(period = '7days', tenantId = null) {
	const params = new URLSearchParams({ period });
	if (tenantId) {
		params.append('tenant', tenantId);
	}
	return authFetch(`${BASE_URL}/hourly_sales/?${params}`);
}

/**
 * Format currency
 */
export function formatCurrency(amount) {
	return new Intl.NumberFormat('id-ID', {
		style: 'currency',
		currency: 'IDR',
		minimumFractionDigits: 0,
		maximumFractionDigits: 0
	}).format(amount);
}

/**
 * Format number with separator
 */
export function formatNumber(num) {
	return new Intl.NumberFormat('id-ID').format(num);
}

/**
 * Format percentage
 */
export function formatPercentage(value) {
	const sign = value >= 0 ? '+' : '';
	return `${sign}${value.toFixed(1)}%`;
}

/**
 * Get period label
 */
export function getPeriodLabel(period) {
	const labels = {
		today: 'Today',
		yesterday: 'Yesterday',
		'7days': 'Last 7 Days',
		'30days': 'Last 30 Days',
		'90days': 'Last 90 Days',
		this_month: 'This Month',
		last_month: 'Last Month',
		custom: 'Custom Range'
	};
	return labels[period] || period;
}

/**
 * Get period options for select
 */
export function getPeriodOptions() {
	return [
		{ value: 'today', label: 'Today' },
		{ value: 'yesterday', label: 'Yesterday' },
		{ value: '7days', label: 'Last 7 Days' },
		{ value: '30days', label: 'Last 30 Days' },
		{ value: '90days', label: 'Last 90 Days' },
		{ value: 'this_month', label: 'This Month' },
		{ value: 'last_month', label: 'Last Month' },
		{ value: 'custom', label: 'Custom Range' }
	];
}
