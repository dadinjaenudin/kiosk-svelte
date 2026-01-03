/**
 * Order Management API client
 * 
 * Handles all order-related API calls for Admin Panel
 */
import { authFetch } from './auth';

const API_BASE = '/api';

/**
 * Get list of orders with filters
 * @param {Object} params - Filter parameters
 * @returns {Promise<Object>} Orders list with pagination
 */
export async function getOrders(params = {}) {
    const queryParams = new URLSearchParams();
    
    // Add filters
    if (params.status && params.status.length > 0) {
        params.status.forEach(status => queryParams.append('status', status));
    }
    if (params.payment_status) queryParams.append('payment_status', params.payment_status);
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);
    if (params.search) queryParams.append('search', params.search);
    if (params.tenant) queryParams.append('tenant', params.tenant);
    if (params.outlet) queryParams.append('outlet', params.outlet);
    if (params.ordering) queryParams.append('ordering', params.ordering);
    if (params.page) queryParams.append('page', params.page);
    if (params.page_size) queryParams.append('page_size', params.page_size);
    
    const url = `${API_BASE}/admin/orders/?${queryParams.toString()}`;
    return await authFetch(url);
}

/**
 * Get order details
 * @param {number} orderId - Order ID
 * @returns {Promise<Object>} Order details
 */
export async function getOrderDetail(orderId) {
    return await authFetch(`${API_BASE}/admin/orders/${orderId}/`);
}

/**
 * Update order status
 * @param {number} orderId - Order ID
 * @param {string} status - New status
 * @returns {Promise<Object>} Updated order
 */
export async function updateOrderStatus(orderId, status) {
    return await authFetch(`${API_BASE}/admin/orders/${orderId}/update_status/`, {
        method: 'POST',
        body: JSON.stringify({ status })
    });
}

/**
 * Get order timeline
 * @param {number} orderId - Order ID
 * @returns {Promise<Object>} Order timeline
 */
export async function getOrderTimeline(orderId) {
    return await authFetch(`${API_BASE}/admin/orders/${orderId}/timeline/`);
}

/**
 * Get receipt data
 * @param {number} orderId - Order ID
 * @returns {Promise<Object>} Receipt data
 */
export async function getOrderReceipt(orderId) {
    return await authFetch(`${API_BASE}/admin/orders/${orderId}/receipt/`);
}

/**
 * Get order statistics
 * @param {string} period - Period (today, week, month, year)
 * @returns {Promise<Object>} Order statistics
 */
export async function getOrderStatistics(period = 'today') {
    return await authFetch(`${API_BASE}/admin/orders/statistics/?period=${period}`);
}

/**
 * Format order status for display
 * @param {string} status - Order status
 * @returns {Object} Formatted status with color and label
 */
export function formatOrderStatus(status) {
    const statusMap = {
        'draft': { label: 'Draft', color: 'gray', bgColor: 'bg-gray-100', textColor: 'text-gray-800' },
        'pending': { label: 'Pending', color: 'yellow', bgColor: 'bg-yellow-100', textColor: 'text-yellow-800' },
        'confirmed': { label: 'Confirmed', color: 'blue', bgColor: 'bg-blue-100', textColor: 'text-blue-800' },
        'preparing': { label: 'Preparing', color: 'purple', bgColor: 'bg-purple-100', textColor: 'text-purple-800' },
        'ready': { label: 'Ready', color: 'green', bgColor: 'bg-green-100', textColor: 'text-green-800' },
        'served': { label: 'Served', color: 'teal', bgColor: 'bg-teal-100', textColor: 'text-teal-800' },
        'completed': { label: 'Completed', color: 'green', bgColor: 'bg-green-100', textColor: 'text-green-800' },
        'cancelled': { label: 'Cancelled', color: 'red', bgColor: 'bg-red-100', textColor: 'text-red-800' }
    };
    return statusMap[status] || { label: status, color: 'gray', bgColor: 'bg-gray-100', textColor: 'text-gray-800' };
}

/**
 * Format payment status for display
 * @param {string} status - Payment status
 * @returns {Object} Formatted status with color and label
 */
export function formatPaymentStatus(status) {
    const statusMap = {
        'unpaid': { label: 'Unpaid', color: 'red', bgColor: 'bg-red-100', textColor: 'text-red-800' },
        'pending': { label: 'Pending', color: 'yellow', bgColor: 'bg-yellow-100', textColor: 'text-yellow-800' },
        'paid': { label: 'Paid', color: 'green', bgColor: 'bg-green-100', textColor: 'text-green-800' },
        'refunded': { label: 'Refunded', color: 'gray', bgColor: 'bg-gray-100', textColor: 'text-gray-800' }
    };
    return statusMap[status] || { label: status, color: 'gray', bgColor: 'bg-gray-100', textColor: 'text-gray-800' };
}

/**
 * Format currency (IDR)
 * @param {number} amount - Amount
 * @returns {string} Formatted currency
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
 * Format date time
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date time
 */
export function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('id-ID', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

/**
 * Get time ago string
 * @param {string} dateString - ISO date string
 * @returns {string} Time ago string
 */
export function getTimeAgo(dateString) {
    if (!dateString) return '-';
    
    const now = new Date();
    const date = new Date(dateString);
    const seconds = Math.floor((now - date) / 1000);
    
    const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60
    };
    
    for (const [unit, secondsInUnit] of Object.entries(intervals)) {
        const interval = Math.floor(seconds / secondsInUnit);
        if (interval >= 1) {
            return `${interval} ${unit}${interval > 1 ? 's' : ''} ago`;
        }
    }
    
    return 'Just now';
}
