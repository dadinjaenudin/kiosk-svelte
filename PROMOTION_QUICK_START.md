# 🚀 Quick Start: Promotion Management

## 📋 Prerequisites

✅ Backend running (port 8001)  
✅ Admin Panel running (port 5175)  
✅ Admin user created (`admin/admin123`)  
✅ Sample products seeded

---

## 🏃 Quick Setup (5 Minutes)

### Step 1: Pull Latest Code
```powershell
cd D:\YOGYA-Kiosk\kiosk-svelte
git pull origin main
```

### Step 2: Run Migrations
```powershell
docker-compose exec backend python manage.py makemigrations promotions
docker-compose exec backend python manage.py migrate
```

### Step 3: Verify Services
```powershell
# Check backend health
curl http://localhost:8001/api/health/

# Expected: {"status":"ok","service":"POS Backend"}
```

### Step 4: Access Admin Panel
1. Open browser: **http://localhost:5175/**
2. Login: `admin` / `admin123`
3. Navigate: **Promotions** (in sidebar)

---

## 🎯 Your First Promotion (2 Minutes)

### Create "Weekend Special" Promotion

1. **Click**: "Create Promotion" button (top right)

2. **Basic Info**:
   - Name: `Weekend Flash Sale`
   - Description: `Get 50% off on selected items this weekend!`
   - Status: **Active**
   - ✅ Check "Active now"

3. **Discount Type**:
   - Click: **Percentage Discount** (% icon)
   - Discount Value: `50` %
   - Max Discount: `50000` IDR
   - Min Purchase: `100000` IDR

4. **Select Products**:
   - Search: type product name (e.g., "ayam")
   - Click products to select (2-3 products)
   - Verify: Selected count shows below

5. **Schedule**:
   - Start: Tomorrow 00:00
   - End: Next Sunday 23:59
   - Days: Click "Weekends" button
   - ✅ Check "Enable daily time restriction"
   - Time: 10:00 → 22:00

6. **Usage Limits** (Optional):
   - Total Usage Limit: `100`
   - Per Customer: `1`

7. **Click**: "Create Promotion"

8. **Verify**:
   - Redirected to Promotions list
   - New promotion appears
   - Status badge: **Active** (green)
   - Usage: `0 / 100`

---

## 🧪 Test All Features (5 Minutes)

### Test 1: Search
1. Type in search box: `"weekend"`
2. Hit Enter or click "Apply Filters"
3. ✅ Only matching promotions show

### Test 2: Filter
1. Status dropdown: Select "Active"
2. Type dropdown: Select "Percentage Discount"
3. Click "Apply Filters"
4. ✅ Filtered results show

### Test 3: View Details
1. Click **Eye icon** (View) on any promotion
2. (Coming soon: Detail page will open)

### Test 4: Edit
1. Click **Pencil icon** (Edit)
2. Update: Name or discount value
3. Save changes
4. ✅ Changes reflected in list

### Test 5: Activate/Deactivate
1. Find a Draft promotion
2. Click **Play icon** (Activate)
3. ✅ Status → Active
4. Click **Pause icon** (Deactivate)
5. ✅ Status → Paused

### Test 6: Delete
1. Click **Trash icon** (Delete)
2. Confirm in modal
3. ✅ Promotion removed

---

## 📊 Create Different Promo Types

### Type 1: Fixed Amount Discount
```
Name: "Happy Hour - Rp 10,000 Off"
Type: Fixed Amount
Discount: 10000 IDR
Min Purchase: 50000 IDR
Schedule: Weekdays 15:00-18:00
```

### Type 2: Buy 2 Get 1
```
Name: "Buy 2 Get 1 Free - Coffee"
Type: Buy X Get Y
Buy Quantity: 2
Get Quantity: 1
Products: Coffee items only
Schedule: All days
```

### Type 3: Bundle Deal
```
Name: "Lunch Combo Special"
Type: Bundle Deal
Discount: 15% (or fixed)
Products: Rice + Drink + Dessert
Schedule: Monday-Friday 11:00-14:00
```

---

## 🔍 Troubleshooting

### Issue 1: Migration Error
```bash
# If you see migration conflicts:
docker-compose exec backend python manage.py migrate --fake promotions zero
docker-compose exec backend python manage.py migrate promotions
```

### Issue 2: Products Not Loading
```bash
# Check if products exist:
docker-compose exec backend python manage.py shell
>>> from apps.products.models import Product
>>> Product.objects.count()
>>> exit()

# If count is 0, seed data:
docker-compose exec backend python manage.py seed_foodcourt
```

### Issue 3: Can't Create Promotion (API Error)
1. Check browser console (F12)
2. Look for error message
3. Common causes:
   - Token expired: Re-login
   - Invalid data: Check form validation
   - Products not selected: Select at least 1 product
   - Date range invalid: End must be after start

### Issue 4: Admin Panel Not Loading
```bash
# Restart admin container:
docker-compose restart admin

# Check logs:
docker-compose logs admin --tail=50

# Expected: "VITE ready" message
```

---

## 🎨 Tips & Best Practices

### Naming Conventions
- ✅ Clear: "Weekend Sale 50% Off"
- ✅ Specific: "Happy Hour Coffee - Buy 2 Get 1"
- ❌ Vague: "Promo 1", "Test"

### Discount Strategy
- **Percentage**: Best for high-value items
- **Fixed Amount**: Better for psychology ($10 off sounds more than 10%)
- **Buy X Get Y**: Increases order quantity
- **Bundle**: Cross-sells complementary items

### Scheduling
- **Weekends**: Higher traffic, use percentage
- **Weekdays**: Slower, use fixed amount or buy X get Y
- **Happy Hour**: Time restrictions (e.g., 15:00-18:00)
- **Late Night**: Clearance deals (21:00-23:00)

### Usage Limits
- **High-Value Promos**: Limit to 1 per customer
- **Low-Value Promos**: Allow multiple uses
- **Flash Sales**: Set total limit (e.g., first 50 customers)

---

## 📱 Mobile Testing

1. Open browser DevTools (F12)
2. Click "Toggle Device Toolbar" (Ctrl+Shift+M)
3. Select: iPhone 12 Pro or similar
4. Test:
   - ✅ Filters collapse properly
   - ✅ Table scrolls horizontally
   - ✅ Forms are usable
   - ✅ Buttons are touch-friendly

---

## 🔐 Security Notes

### Permissions
- **Admin**: Can create promos for all tenants
- **Tenant Owner**: Can only create for their tenant
- **Manager**: Can create/edit tenant promos
- **Staff**: View-only (coming soon)

### Validation
- ✅ Start date < End date
- ✅ Percentage ≤ 100%
- ✅ Discount > 0
- ✅ At least 1 product selected
- ✅ At least 1 day selected

---

## 🚢 Next Steps

### Immediate
1. ✅ Create 2-3 sample promotions
2. ✅ Test search and filters
3. ✅ Verify activation works

### Short-Term (This Week)
- [ ] Promotion detail page
- [ ] Edit promotion form
- [ ] Preview component (price before/after)
- [ ] Apply promotions in kiosk frontend

### Long-Term (Next Week)
- [ ] Analytics dashboard
- [ ] Usage history page
- [ ] Promo templates
- [ ] Notification system

---

## 📞 Support

### Having Issues?
1. Check this guide first
2. Review `PHASE5_PROMOTION_MANAGEMENT.md`
3. Check browser console for errors
4. Review Docker logs: `docker-compose logs backend`

### Documentation
- **Full Docs**: `/PHASE5_PROMOTION_MANAGEMENT.md`
- **API Docs**: http://localhost:8001/api/docs/
- **Repository**: https://github.com/dadinjaenudin/kiosk-svelte

---

**Ready to Go?** 🚀  
Open http://localhost:5175/promotions and create your first promotion!
