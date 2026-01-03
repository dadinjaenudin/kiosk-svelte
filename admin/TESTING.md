# Playwright Testing Guide

## Overview
Playwright tests untuk admin panel Kiosk POS system. Tests mencakup login, CRUD operations, dan UI interactions.

## Installation
Playwright sudah terinstall. Jika perlu install ulang:
```bash
npm install -D @playwright/test
npx playwright install chromium
```

## Running Tests

### Run all tests (headless)
```bash
npm test
```

### Run tests with UI mode (recommended)
```bash
npm run test:ui
```
UI mode memberikan interface interaktif untuk:
- Melihat test execution secara visual
- Debug test yang gagal
- Time travel debugging
- Pick locator tool

### Run tests in headed mode (show browser)
```bash
npm run test:headed
```

### Debug specific test
```bash
npm run test:debug
```
Atau debug specific file:
```bash
npx playwright test tests/login.spec.js --debug
```

### View test report
```bash
npm run test:report
```

## Test Structure

### Test Files
```
tests/
├── login.spec.js          # Login authentication tests
├── products.spec.js       # Products CRUD operations
└── outlets.spec.js        # Outlets management tests
```

### Configuration
`playwright.config.js` - Main configuration file
- Base URL: http://localhost:5175
- Auto-start dev server
- Screenshots on failure
- Trace on first retry

## Writing Tests

### Basic Test Structure
```javascript
import { test, expect } from '@playwright/test';

test.describe('Feature Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Setup - login, navigate, etc
  });

  test('should do something', async ({ page }) => {
    // Test steps
    await page.goto('/page');
    await expect(page.locator('selector')).toBeVisible();
  });
});
```

### Common Patterns

#### Login Helper
```javascript
test.beforeEach(async ({ page }) => {
  await page.goto('/login');
  await page.locator('input[type="text"]').fill('admin');
  await page.locator('input[type="password"]').fill('admin123');
  await page.locator('button[type="submit"]').click();
  await page.waitForURL('**/dashboard', { timeout: 5000 });
});
```

#### Wait for Elements
```javascript
// Wait for element to be visible
await page.waitForSelector('table', { timeout: 2000 });

// Wait for URL change
await page.waitForURL('**/products', { timeout: 5000 });

// Wait for network request
await page.waitForResponse(resp => 
  resp.url().includes('/api/products') && resp.status() === 200
);
```

#### Assertions
```javascript
// Visibility
await expect(page.locator('table')).toBeVisible();

// Count
await expect(page.locator('tr')).toHaveCount(10);

// Text content
await expect(page.locator('h1')).toHaveText('Products');

// URL
expect(page.url()).toContain('/products');
```

## Best Practices

1. **Use data-testid for stable selectors**
   ```html
   <button data-testid="add-product-btn">Add Product</button>
   ```
   ```javascript
   await page.locator('[data-testid="add-product-btn"]').click();
   ```

2. **Wait for network requests**
   ```javascript
   await page.waitForResponse(resp => resp.url().includes('/api/products'));
   ```

3. **Use beforeEach for common setup**
   - Login
   - Navigate to page
   - Setup test data

4. **Clean up after tests**
   ```javascript
   test.afterEach(async ({ page }) => {
     // Delete test data if created
   });
   ```

5. **Use descriptive test names**
   ```javascript
   test('should display validation error when submitting empty outlet form', ...)
   ```

## Test Credentials
- Username: `admin`
- Password: `admin123`

## CI/CD Integration
Tests dapat dijalankan di CI/CD pipeline:
```yaml
- name: Run Playwright tests
  run: |
    npm ci
    npx playwright install chromium
    npm test
```

## Debugging Tips

1. **Use playwright inspector**
   ```bash
   npx playwright test --debug
   ```

2. **Add console logs**
   ```javascript
   console.log(await page.locator('table').count());
   ```

3. **Take screenshots**
   ```javascript
   await page.screenshot({ path: 'screenshot.png' });
   ```

4. **Pause test**
   ```javascript
   await page.pause();
   ```

5. **Use codegen to generate selectors**
   ```bash
   npx playwright codegen http://localhost:5175
   ```

## Known Issues
- Tests require dev server running on port 5175
- Some tests may need adjustment based on actual data
- Time format validation tests depend on backend response

## Resources
- [Playwright Documentation](https://playwright.dev)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Selectors Guide](https://playwright.dev/docs/selectors)
