import { test, expect } from '@playwright/test';

test.describe('Products CRUD Tests', () => {
	// Login before each test
	test.beforeEach(async ({ page }) => {
		await page.goto('/login');
		await page.locator('input[type="text"]').fill('admin');
		await page.locator('input[type="password"]').fill('admin123');
		await page.locator('button[type="submit"]').click();
		await page.waitForURL('**/dashboard', { timeout: 5000 });
	});

	test('should display products page', async ({ page }) => {
		await page.goto('/products');
		
		// Check if products table/list exists
		await expect(page.locator('table')).toBeVisible();
		
		// Check for pagination
		await expect(page.locator('button').filter({ hasText: /previous|next/i })).toHaveCount(2);
	});

	test('should open add product modal', async ({ page }) => {
		await page.goto('/products');
		
		// Click add product button
		await page.getByRole('button', { name: /add product|create product/i }).click();
		
		// Wait for modal to appear
		await page.waitForSelector('[role="dialog"]', { timeout: 2000 });
		
		// Verify modal is visible
		await expect(page.locator('[role="dialog"]')).toBeVisible();
	});

	test('should search products', async ({ page }) => {
		await page.goto('/products');
		
		// Find search input and type
		const searchInput = page.locator('input[placeholder*="search" i], input[type="search"]').first();
		await searchInput.fill('test');
		
		// Wait for results to update
		await page.waitForTimeout(1000);
	});

	test('should paginate products', async ({ page }) => {
		await page.goto('/products');
		
		// Click next page button
		const nextButton = page.getByRole('button', { name: /next|›|»/i }).first();
		
		if (await nextButton.isEnabled()) {
			await nextButton.click();
			await page.waitForTimeout(500);
			
			// Verify URL or content changed
			const url = page.url();
			expect(url).toContain('page=2');
		}
	});
});
