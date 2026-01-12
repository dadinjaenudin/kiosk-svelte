/**
 * Order Snapshot Validation Tests
 * 
 * Tests the snapshot integrity validation for F&B POS orders
 */

import { describe, it, expect } from 'vitest';
import { validateOrderSnapshot } from '../offlineOrderService';

describe('Order Snapshot Validation', () => {
	it('should pass validation for valid order with all snapshots', () => {
		const validOrder = {
			order_number: 'OFFLINE-01KEQVJSWC3183WAJGVD8T8V8A',
			total_amount: 50000,
			subtotal: 45000,
			payment_method: 'cash',
			created_at: '2026-01-12T10:30:00Z',
			items: [
				{
					product_id: 1,
					product_name: 'Nasi Goreng', // SNAPSHOT
					price: 25000, // SNAPSHOT
					quantity: 2,
					modifiers: [
						{
							id: 10,
							name: 'Extra Egg', // SNAPSHOT
							price: 5000 // SNAPSHOT
						}
					],
					modifiers_price: 5000,
					subtotal: 60000 // (25000 + 5000) * 2
				}
			]
		};

		const result = validateOrderSnapshot(validOrder);
		expect(result.valid).toBe(true);
		expect(result.errors).toHaveLength(0);
	});

	it('should fail when price is not a number', () => {
		const invalidOrder = {
			order_number: 'TEST-001',
			total_amount: 50000,
			subtotal: 45000,
			payment_method: 'cash',
			created_at: '2026-01-12T10:30:00Z',
			items: [
				{
					product_id: 1,
					product_name: 'Nasi Goreng',
					price: '25000', // ❌ STRING instead of number
					quantity: 1,
					modifiers: []
				}
			]
		};

		const result = validateOrderSnapshot(invalidOrder);
		expect(result.valid).toBe(false);
		expect(result.errors).toContain('Item 0: price must be a frozen number (snapshot)');
	});

	it('should fail when product_name is missing', () => {
		const invalidOrder = {
			order_number: 'TEST-002',
			total_amount: 25000,
			subtotal: 25000,
			payment_method: 'cash',
			created_at: '2026-01-12T10:30:00Z',
			items: [
				{
					product_id: 1,
					// product_name: missing! ❌
					price: 25000,
					quantity: 1,
					modifiers: []
				}
			]
		};

		const result = validateOrderSnapshot(invalidOrder);
		expect(result.valid).toBe(false);
		expect(result.errors).toContain('Item 0: product_name is required (snapshot)');
	});

	it('should fail when modifier price is not a number', () => {
		const invalidOrder = {
			order_number: 'TEST-003',
			total_amount: 30000,
			subtotal: 30000,
			payment_method: 'cash',
			created_at: '2026-01-12T10:30:00Z',
			items: [
				{
					product_id: 1,
					product_name: 'Nasi Goreng',
					price: 25000,
					quantity: 1,
					modifiers: [
						{
							id: 10,
							name: 'Extra Egg',
							price: '5000' // ❌ STRING instead of number
						}
					]
				}
			]
		};

		const result = validateOrderSnapshot(invalidOrder);
		expect(result.valid).toBe(false);
		expect(result.errors).toContain('Item 0, Modifier 0: price must be a frozen number');
	});

	it('should fail when subtotal calculation is wrong', () => {
		const invalidOrder = {
			order_number: 'TEST-004',
			total_amount: 50000,
			subtotal: 50000,
			payment_method: 'cash',
			created_at: '2026-01-12T10:30:00Z',
			items: [
				{
					product_id: 1,
					product_name: 'Nasi Goreng',
					price: 25000,
					quantity: 2,
					modifiers: [],
					modifiers_price: 0,
					subtotal: 45000 // ❌ Wrong! Should be 50000 (25000 * 2)
				}
			]
		};

		const result = validateOrderSnapshot(invalidOrder);
		expect(result.valid).toBe(false);
		expect(result.errors.some(e => e.includes('subtotal mismatch'))).toBe(true);
	});

	it('should fail when items array is empty', () => {
		const invalidOrder = {
			order_number: 'TEST-005',
			total_amount: 0,
			subtotal: 0,
			payment_method: 'cash',
			created_at: '2026-01-12T10:30:00Z',
			items: [] // ❌ Empty items
		};

		const result = validateOrderSnapshot(invalidOrder);
		expect(result.valid).toBe(false);
		expect(result.errors).toContain('items array is required and must not be empty');
	});

	it('should fail when payment_method is missing', () => {
		const invalidOrder = {
			order_number: 'TEST-006',
			total_amount: 25000,
			subtotal: 25000,
			// payment_method: missing! ❌
			created_at: '2026-01-12T10:30:00Z',
			items: [
				{
					product_id: 1,
					product_name: 'Nasi Goreng',
					price: 25000,
					quantity: 1,
					modifiers: []
				}
			]
		};

		const result = validateOrderSnapshot(invalidOrder);
		expect(result.valid).toBe(false);
		expect(result.errors).toContain('payment_method is required');
	});

	it('should pass with multiple items and modifiers', () => {
		const validOrder = {
			order_number: 'OFFLINE-01KEQVJSWC3183WAJGVD8T8V8A',
			total_amount: 100000,
			subtotal: 90000,
			payment_method: 'qris',
			created_at: '2026-01-12T10:30:00Z',
			items: [
				{
					product_id: 1,
					product_name: 'Nasi Goreng',
					price: 25000,
					quantity: 2,
					modifiers: [
						{
							id: 10,
							name: 'Extra Egg',
							price: 5000
						},
						{
							id: 11,
							name: 'Extra Spicy',
							price: 2000
						}
					],
					modifiers_price: 7000,
					subtotal: 64000 // (25000 + 7000) * 2
				},
				{
					product_id: 2,
					product_name: 'Es Teh',
					price: 5000,
					quantity: 2,
					modifiers: [],
					modifiers_price: 0,
					subtotal: 10000 // 5000 * 2
				}
			]
		};

		const result = validateOrderSnapshot(validOrder);
		expect(result.valid).toBe(true);
		expect(result.errors).toHaveLength(0);
	});
});
