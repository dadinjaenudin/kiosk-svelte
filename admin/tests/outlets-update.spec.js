import { test, expect } from '@playwright/test';

test.describe('Outlet Update Bug Test', () => {
	test.beforeEach(async ({ page }) => {
		// Login
		await page.goto('/login');
		await page.locator('input[type="text"]').fill('admin');
		await page.locator('input[type="password"]').fill('admin123');
		await page.locator('button[type="submit"]').click();
		await page.waitForURL('**/dashboard', { timeout: 5000 });
	});

	test('should capture outlet update error', async ({ page }) => {
		// Listen to console logs
		const consoleLogs = [];
		page.on('console', msg => {
			consoleLogs.push(`${msg.type()}: ${msg.text()}`);
		});

		// Listen to network requests
		const requests = [];
		page.on('request', request => {
			if (request.url().includes('/api/')) {
				requests.push({
					url: request.url(),
					method: request.method(),
					postData: request.postData()
				});
			}
		});

		// Listen to network responses
		const responses = [];
		page.on('response', async response => {
			if (response.url().includes('/api/')) {
				try {
					const body = await response.text();
					responses.push({
						url: response.url(),
						status: response.status(),
						body: body.substring(0, 500) // Limit size
					});
				} catch (e) {
					// Ignore errors reading response
				}
			}
		});

		// Navigate to settings
		await page.goto('/settings');
		await page.waitForTimeout(1000);

		// Click outlets tab
		await page.getByText('Outlets', { exact: false }).click();
		await page.waitForTimeout(1000);

		// Find and click edit button on first outlet
		const editButton = page.locator('button').filter({ hasText: /edit/i }).first();
		
		if (await editButton.count() > 0) {
			await editButton.click();
			await page.waitForTimeout(1000);

			// Wait for modal
			await page.waitForSelector('[role="dialog"]', { timeout: 3000 });

			// Check current time values
			const openingTimeValue = await page.locator('input[type="time"]').first().inputValue();
			const closingTimeValue = await page.locator('input[type="time"]').last().inputValue();

			console.log('Opening time value:', openingTimeValue);
			console.log('Closing time value:', closingTimeValue);

			// Try to submit the form
			await page.getByRole('button', { name: /save|update/i }).click();
			
			// Wait for response
			await page.waitForTimeout(2000);

			// Print captured data
			console.log('\n=== CONSOLE LOGS ===');
			consoleLogs.forEach(log => console.log(log));

			console.log('\n=== REQUESTS ===');
			requests.forEach(req => {
				console.log(`${req.method} ${req.url}`);
				if (req.postData) {
					console.log('POST DATA:', req.postData);
				}
			});

			console.log('\n=== RESPONSES ===');
			responses.forEach(resp => {
				console.log(`${resp.status} ${resp.url}`);
				console.log('BODY:', resp.body);
			});
		} else {
			console.log('No edit button found - no outlets exist?');
		}
	});
});
