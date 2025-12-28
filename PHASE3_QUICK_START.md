# Quick Start: Testing Phase 3 Order Management

**Status**: Ready to Test  
**Date**: 2025-12-28

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Start Services (2 min)

```bash
# From D:\YOGYA-Kiosk\kiosk-svelte
cd D:\YOGYA-Kiosk\kiosk-svelte

# Pull latest code
git pull origin main

# Start all services
docker-compose up --build

# Wait for services to be ready (~2 minutes)
# Look for: "VITE ready" for both frontend and admin
```

### Step 2: Create Test Orders (1 min)

Open Kiosk and create some test orders:

```
http://localhost:5174/kiosk
```

1. Add some items to cart (from different tenants)
2. Click "Checkout"
3. Fill in customer info (optional)
4. Select payment method
5. Complete checkout
6. Repeat 2-3 times to create multiple orders

### Step 3: Access Order Management (2 min)

```
http://localhost:5175/orders
```

**Login**:
- Username: `admin`
- Password: `admin123`

**What to Test**:

1. **View Orders List**:
   - ✅ See all orders you created
   - ✅ Check order numbers, amounts, status

2. **Try Filters**:
   - Click "▼ Filters"
   - Select "Pending" status
   - Orders should filter

3. **Search**:
   - Type order number in search box
   - Order should appear

4. **View Order Detail**:
   - Click any order
   - Review order info, items, timeline

5. **Update Status**:
   - Click "Update Status"
   - Select "Confirmed"
   - Click "Update Status"
   - Timeline should update

6. **Print Receipt**:
   - Click "🖨️ Print Receipt"
   - Review receipt data
   - Use Ctrl+P to print

---

## 🎯 Quick Test Commands

### Test Backend API

```bash
# Get your token first
# Login to admin panel, then open browser DevTools > Application > Local Storage
# Copy the token value

# Set token as variable (PowerShell)
$TOKEN = "your_token_here"

# Test order list
curl.exe -H "Authorization: Token $TOKEN" http://localhost:8001/api/admin/orders/

# Test order detail (replace 1 with actual order ID)
curl.exe -H "Authorization: Token $TOKEN" http://localhost:8001/api/admin/orders/1/

# Test statistics
curl.exe -H "Authorization: Token $TOKEN" http://localhost:8001/api/admin/orders/statistics/?period=today
```

---

## ✅ Success Checklist

After following the Quick Start, verify:

- [ ] Services running: `docker-compose ps` shows all "Up"
- [ ] Can access Kiosk: http://localhost:5174/kiosk
- [ ] Can create orders from Kiosk
- [ ] Can access Admin Panel: http://localhost:5175/
- [ ] Can login to Admin Panel
- [ ] Orders page loads: http://localhost:5175/orders
- [ ] Can see test orders in list
- [ ] Can filter orders
- [ ] Can search orders
- [ ] Can click order to view detail
- [ ] Can see order timeline
- [ ] Can update order status
- [ ] Can print receipt
- [ ] No errors in browser console (F12)

---

## 🐛 Troubleshooting

### Issue: Services not starting

```bash
# Check Docker
docker-compose ps

# Check logs
docker-compose logs backend --tail=50
docker-compose logs admin --tail=50

# Restart
docker-compose restart
```

### Issue: Admin Panel 500 error after login

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create admin user
docker-compose exec backend python manage.py shell
# Then:
# from apps.users.models import User
# User.objects.create_superuser('admin', 'admin@example.com', 'admin123', role='admin')
# exit()
```

### Issue: No orders showing

1. Create orders from Kiosk first: http://localhost:5174/kiosk
2. Check if you're logged in as correct user
3. Check browser console for errors (F12)

---

## 📸 Expected Screenshots

### Orders List Page
- Header: "Order Management"
- Search bar and filters
- Table with orders (or "No orders found")
- Status and payment badges (colored)

### Order Detail Page
- Order number at top
- Status cards showing current status
- Order items with modifiers
- Timeline showing progression
- "Update Status" and "Print Receipt" buttons

### Timeline Example
```
✓ Order Placed       - 10:30 AM
✓ Confirmed          - 10:32 AM
✓ Preparing          - 10:35 AM
○ Ready to Serve     - Pending
○ Served             - Pending
○ Completed          - Pending
```

---

## 🎉 Demo Scenario

**Complete Order Workflow Test**:

1. **Create Order** (Kiosk):
   - Go to http://localhost:5174/kiosk
   - Add: Ayam Geprek Keju + Level Pedas (Sedang)
   - Add: Nasi Goreng Spesial
   - Checkout with customer name "John Doe"
   - Payment: Cash

2. **View Order** (Admin):
   - Go to http://localhost:5175/orders
   - See new order at top (status: Pending)
   - Click to view details

3. **Process Order** (Admin):
   - Update status: Pending → Confirmed
   - Update status: Confirmed → Preparing
   - Update status: Preparing → Ready
   - Update status: Ready → Served
   - Update status: Served → Completed

4. **Verify Timeline** (Admin):
   - Timeline should show all steps completed
   - Each step should have timestamp

5. **Print Receipt** (Admin):
   - Click "Print Receipt"
   - Receipt shows all items, modifiers, totals
   - Print or save as PDF

---

## 📊 Expected Results

After completing the demo:

- **Order Status**: Completed ✅
- **Timeline**: All 7 steps completed
- **Receipt**: Shows 2 items with modifiers
- **Total**: Calculated correctly with tax and service charge

---

## 🔗 Quick Links

- **Kiosk**: http://localhost:5174/kiosk
- **Admin Panel**: http://localhost:5175/
- **Orders Page**: http://localhost:5175/orders
- **Backend API**: http://localhost:8001/api/
- **API Docs**: http://localhost:8001/api/docs/

---

## 📝 Next Steps

After testing Phase 3:

1. ✅ Verify all features work
2. 📸 Take screenshots of key pages
3. 🐛 Report any issues found
4. 💡 Suggest improvements

**Phase 4 Preview**:
- Customer Management (view, search, history)
- Advanced Promo Management
- Reports and Analytics Dashboard
- Export Orders (CSV, Excel, PDF)

---

**Happy Testing!** 🎉

If you encounter any issues, check:
1. Browser console (F12)
2. Backend logs: `docker-compose logs backend --tail=50`
3. Network tab (F12 → Network)

---

**Last Updated**: 2025-12-28