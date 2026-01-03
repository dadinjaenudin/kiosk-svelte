import { test, expect } from '@playwright/test';

test.describe('Outlets Management Tests', () => {
	test.beforeEach(async ({ page }) => {
		await page.goto('/login');
		await page.locator('input[type="text"]').fill('admin');
		await page.locator('input[type="password"]').fill('admin123');
		await page.locator('button[type="submit"]').click();
		await page.waitForURL('**/dashboard', { timeout: 5000 });
	});

	test('should display settings page with outlets tab', async ({ page }) => {
		await page.goto('/settings');
		
		// Click outlets tab
		await page.getByRole('tab', { name: /outlets/i }).click();
		
		// Verify outlets table is visible
		await expect(page.locator('table').first()).toBeVisible();
	});

	test('should open add outlet modal', async ({ page }) => {
		await page.goto('/settings');
		
		// Click outlets tab
		await page.getByRole('tab', { name: /outlets/i }).click();
		
		// Click add outlet button
		await page.getByRole('button', { name: /add outlet|create outlet/i }).click();
		
		// Wait for modal
		await page.waitForSelector('[role="dialog"]', { timeout: 2000 });
		
		// Verify modal is visible
		await expect(page.locator('[role="dialog"]')).toBeVisible();
	});

	test('should validate outlet form fields', async ({ page }) => {
		await page.goto('/settings');
		await page.getByRole('tab', { name: /outlets/i }).click();
		await page.getByRole('button', { name: /add outlet|create outlet/i }).click();
		
		// Wait for modal
		await page.waitForSelector('[role="dialog"]', { timeout: 2000 });
		
		// Try to submit empty form
		await page.getByRole('button', { name: /save|submit/i }).click();
		
		// Wait for validation errors to appear
		await page.waitForTimeout(500);
		
		// Verify form is still visible (not submitted)
		await expect(page.locator('[role="dialog"]')).toBeVisible();
	});

	test('should fill outlet form with valid data', async ({ page }) => {
		await page.goto('/settings');
		await page.getByRole('tab', { name: /outlets/i }).click();
		await page.getByRole('button', { name: /add outlet|create outlet/i }).click();
		
		await page.waitForSelector('[role="dialog"]', { timeout: 2000 });
		
		// Fill form fields
		await page.locator('input[name="name"], input[placeholder*="name" i]').first().fill('Test Outlet');
		await page.locator('input[name="address"], textarea[name="address"]').first().fill('123 Test Street');
		await page.locator('input[name="city"]').fill('Jakarta');
		await page.locator('input[name="phone"]').fill('081234567890');
		
		// Fill time fields
		await page.locator('input[type="time"][name="opening_time"], input[type="time"]').first().fill('08:00');
		await page.locator('input[type="time"][name="closing_time"], input[type="time"]').last().fill('22:00');
		
		// Note: Don't submit to avoid creating test data
		// await page.getByRole('button', { name: /save|submit/i }).click();
	});
});
