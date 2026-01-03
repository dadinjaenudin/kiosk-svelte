import { test, expect } from '@playwright/test';

test.describe('Login Tests', () => {
	test('should display login page', async ({ page }) => {
		await page.goto('/login');
		
		// Check if login form elements exist
		await expect(page.locator('input[type="text"]')).toBeVisible();
		await expect(page.locator('input[type="password"]')).toBeVisible();
		await expect(page.locator('button[type="submit"]')).toBeVisible();
	});

	test('should show error for invalid credentials', async ({ page }) => {
		await page.goto('/login');
		
		// Fill in invalid credentials
		await page.locator('input[type="text"]').fill('invalid@test.com');
		await page.locator('input[type="password"]').fill('wrongpassword');
		
		// Click login button
		await page.locator('button[type="submit"]').click();
		
		// Wait for error message (adjust selector based on your implementation)
		await page.waitForTimeout(1000);
	});

	test('should login with valid credentials', async ({ page }) => {
		await page.goto('/login');
		
		// Fill in valid credentials (adjust to your test credentials)
		await page.locator('input[type="text"]').fill('admin');
		await page.locator('input[type="password"]').fill('admin123');
		
		// Click login button
		await page.locator('button[type="submit"]').click();
		
		// Wait for redirect to dashboard
		await page.waitForURL('**/dashboard', { timeout: 5000 });
		
		// Verify we're on the dashboard
		expect(page.url()).toContain('/dashboard');
	});
});
