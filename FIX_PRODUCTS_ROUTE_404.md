# Product Route 404 Fix

## Issue
Route `/products` showing "404 Not Found" despite file existing at `admin/src/routes/products/+page.svelte`

## Root Cause
Admin container (Vite dev server) hasn't detected the new route files.

## Solution

### Option 1: Quick Restart (Recommended)
```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
docker-compose restart admin
```

Wait ~30 seconds, then hard refresh browser:
- Windows: `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`

### Option 2: Full Rebuild (If restart doesn't work)
```bash
cd D:\YOGYA-Kiosk\kiosk-svelte
docker-compose down
docker-compose up -d
```

### Option 3: Check Container Status
```bash
# Check if admin container is running
docker-compose ps admin

# Check admin logs for errors
docker-compose logs -f admin
```

Look for:
```
VITE v4.x.x  ready in XXX ms
➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

## Verification

After restart, verify:

1. **Admin container is running**:
   ```bash
   docker-compose ps
   # admin should show "Up"
   ```

2. **Vite is ready**:
   ```bash
   docker-compose logs admin | tail -20
   # Should see "VITE ready"
   ```

3. **Route is accessible**:
   - Open: http://localhost:5175/products
   - Should see Product List page (not 404)

## Common Issues

### Issue: Container won't start
```bash
# Check for port conflicts
docker-compose down
docker-compose up -d admin
docker-compose logs -f admin
```

### Issue: Still 404 after restart
```bash
# Clear browser cache completely
# Or try incognito mode
```

### Issue: Vite errors in logs
```bash
# Check for syntax errors
docker-compose logs admin | grep -i error

# Full rebuild if needed
docker-compose build --no-cache admin
docker-compose up -d admin
```

## File Structure (Verified ✅)
```
admin/src/routes/
├── products/
│   ├── +page.svelte          ✅ Exists (List page)
│   ├── create/
│   │   └── +page.svelte      ✅ Exists (Create page)
│   └── [id]/
│       └── edit/
│           └── +page.svelte  ✅ Exists (Edit page)
```

## Navigation Link (Verified ✅)
```javascript
// admin/src/routes/+layout.svelte
{ name: 'Products', href: '/products', icon: '🍽️', feature: 'products' }
```

## Status
- Files: ✅ Correct
- Structure: ✅ Correct
- Navigation: ✅ Correct
- **Container**: ⏳ Needs restart

## Next Steps
1. Restart admin container
2. Wait 30 seconds
3. Hard refresh browser
4. Navigate to /products
5. Should work! ✅
