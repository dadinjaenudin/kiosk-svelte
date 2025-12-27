# 🪟 Windows Scripts untuk Kitchen Display Debugging

## 📝 File yang Tersedia

### 1. **check_kitchen_orders.bat** (Batch File)
- Double-click untuk run
- Kompatibel dengan semua Windows
- Paling simple untuk digunakan

### 2. **check_kitchen_orders.ps1** (PowerShell)
- Run dari PowerShell
- Output dengan warna
- Lebih modern

### 3. **check_orders.py** (Python Script)
- Script utama yang dijalankan di Docker
- Tidak perlu dijalankan langsung

---

## 🚀 Cara Menggunakan

### **Opsi 1: Batch File (RECOMMENDED)** ✅

**Paling mudah - Double click!**

1. Buka folder project: `D:\YOGYA-Kiosk\kiosk-svelte`
2. **Double-click** `check_kitchen_orders.bat`
3. Window CMD akan terbuka dan menjalankan check
4. Lihat hasilnya
5. Tekan tombol apa saja untuk close

**Screenshot**:
```
================================
Kitchen Display - Database Check
================================

Step 1: Checking all orders in database...

=== ALL ORDERS ===
Total orders: 3

Order: ORD-20251227-0001
  Tenant ID: 1
  Tenant Name: Warung Nasi Padang
  Status: confirmed
  Payment Status: paid
  Items: 2
  Created: 2024-12-27 10:30:00

...

================================
Check complete!
================================
Press any key to continue . . .
```

---

### **Opsi 2: PowerShell** ⚡

**Untuk user yang suka PowerShell**

1. Buka **PowerShell** (bukan CMD)
2. Navigate ke folder:
   ```powershell
   cd D:\YOGYA-Kiosk\kiosk-svelte
   ```

3. Allow script execution (first time only):
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

4. Run script:
   ```powershell
   .\check_kitchen_orders.ps1
   ```

5. Lihat hasilnya dengan warna!

---

### **Opsi 3: Manual Command** 🔧

**Untuk advanced users**

1. Buka **Command Prompt** atau **PowerShell**
2. Navigate ke folder:
   ```cmd
   cd D:\YOGYA-Kiosk\kiosk-svelte
   ```

3. Run command:
   ```cmd
   type check_orders.py | docker-compose exec -T backend python manage.py shell
   ```

---

## 📊 Output Explanation

### **Section 1: ALL ORDERS**
```
=== ALL ORDERS ===
Total orders: 3
```
Total semua orders di database.

**Per Order Details**:
```
Order: ORD-20251227-0001
  Tenant ID: 1                    ← Tenant yang punya order ini
  Tenant Name: Warung Nasi Padang
  Status: confirmed               ← Kitchen Display butuh: confirmed/preparing/ready
  Payment Status: paid
  Items: 2                        ← Jumlah items di order
  Created: 2024-12-27 10:30:00
```

---

### **Section 2: ORDERS BY STATUS**
```
=== ORDERS BY STATUS ===
Draft: 0
Pending: 1
Confirmed: 2      ← Kitchen Display show ini
Preparing: 0      ← Kitchen Display show ini
Ready: 0          ← Kitchen Display show ini
Served: 0
Completed: 0
Cancelled: 0
```

Kitchen Display **HANYA** menampilkan orders dengan status:
- ✅ `Confirmed`
- ✅ `Preparing`
- ✅ `Ready`

Jika ada order dengan status `Pending` atau lainnya → **TIDAK** muncul di Kitchen Display!

---

### **Section 3: ORDERS BY TENANT**
```
=== ORDERS BY TENANT ===
Tenant 1 (Warung Nasi Padang): 2 orders
Tenant 2 (Mie Ayam & Bakso): 1 orders
Tenant 3 (Soto Betawi H. Mamat): 0 orders
Tenant 4 (Ayam Geprek Mantap): 0 orders    ← NO ORDERS!
Tenant 5 (Nasi Goreng Abang): 0 orders
```

Menunjukkan berapa banyak orders **total** per tenant (semua status).

**Jika tenant menunjukkan 0 orders** → Belum ada order untuk tenant ini!

---

### **Section 4: KITCHEN DISPLAY FILTER**
```
=== KITCHEN DISPLAY FILTER ===
Filters: status__in=['confirmed', 'preparing', 'ready']
Tenant 1 (Warung Nasi Padang): 2 orders
Tenant 2 (Mie Ayam & Bakso): 0 orders
Tenant 3 (Soto Betawi H. Mamat): 0 orders
Tenant 4 (Ayam Geprek Mantap): 0 orders    ← ZERO FILTERED!
Tenant 5 (Nasi Goreng Abang): 0 orders
```

Ini adalah **exact count** yang Kitchen Display akan tampilkan.

**Jika 0** → Kitchen Display akan show "Tidak Ada Pesanan"

---

## 🔍 Troubleshooting

### Issue 1: "docker-compose is not recognized"

**Cause**: Docker Desktop tidak terinstall atau tidak running

**Fix**:
1. Pastikan Docker Desktop running
2. Check dengan command:
   ```cmd
   docker-compose --version
   ```

---

### Issue 2: Script tidak jalan (PowerShell)

**Error**:
```
cannot be loaded because running scripts is disabled
```

**Fix**:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then run script again.

---

### Issue 3: "No such file or directory: check_orders.py"

**Cause**: File belum di-pull dari Git

**Fix**:
```cmd
git pull origin main
```

---

### Issue 4: Database connection error

**Cause**: Backend container tidak running

**Fix**:
```cmd
docker-compose up -d backend
```

Wait 10 seconds, then run script again.

---

## 📝 Example Output (Full)

```
================================
Kitchen Display - Database Check
================================

Step 1: Checking all orders in database...

=== ALL ORDERS ===
Total orders: 3

Order: ORD-20251227-0001
  Tenant ID: 1
  Tenant Name: Warung Nasi Padang
  Status: confirmed
  Payment Status: paid
  Items: 2
  Created: 2024-12-27 10:30:00.123456+00:00

Order: ORD-20251227-0002
  Tenant ID: 1
  Tenant Name: Warung Nasi Padang
  Status: confirmed
  Payment Status: paid
  Items: 3
  Created: 2024-12-27 11:15:00.123456+00:00

Order: ORD-20251227-0003
  Tenant ID: 2
  Tenant Name: Mie Ayam & Bakso
  Status: pending
  Payment Status: unpaid
  Items: 1
  Created: 2024-12-27 11:45:00.123456+00:00

=== ORDERS BY STATUS ===
Draft: 0
Pending: 1
Confirmed: 2
Preparing: 0
Ready: 0
Served: 0
Completed: 0
Cancelled: 0

=== ORDERS BY TENANT ===
Tenant 1 (Warung Nasi Padang): 2 orders
Tenant 2 (Mie Ayam & Bakso): 1 orders
Tenant 3 (Soto Betawi H. Mamat): 0 orders
Tenant 4 (Ayam Geprek Mantap): 0 orders
Tenant 5 (Nasi Goreng Abang): 0 orders

=== KITCHEN DISPLAY FILTER ===
Filters: status__in=['confirmed', 'preparing', 'ready']
Tenant 1 (Warung Nasi Padang): 2 orders
Tenant 2 (Mie Ayam & Bakso): 0 orders
Tenant 3 (Soto Betawi H. Mamat): 0 orders
Tenant 4 (Ayam Geprek Mantap): 0 orders
Tenant 5 (Nasi Goreng Abang): 0 orders

================================
Check complete!
================================
Press any key to continue . . .
```

---

## 🎯 Interpretation Guide

### ✅ **Good Output** (Orders Will Show):

```
Tenant 1 (Warung Nasi Padang): 2 orders    ← Section 3
Tenant 1 (Warung Nasi Padang): 2 orders    ← Section 4 (SAME!)
```

**Meaning**: 
- 2 total orders untuk tenant
- 2 orders dengan status `confirmed/preparing/ready`
- **Kitchen Display AKAN show 2 orders**

---

### ⚠️ **Warning** (Orders Won't Show):

```
Tenant 2 (Mie Ayam & Bakso): 1 orders      ← Section 3
Tenant 2 (Mie Ayam & Bakso): 0 orders      ← Section 4 (DIFFERENT!)
```

**Meaning**:
- 1 total order untuk tenant
- 0 orders dengan status `confirmed/preparing/ready`
- Order punya status `pending` atau lainnya
- **Kitchen Display TIDAK AKAN show order**

**Fix**: Update order status ke `confirmed`:
```python
# Via Django shell
from apps.orders.models import Order
order = Order.objects.get(order_number='ORD-20251227-0003')
order.status = 'confirmed'
order.save()
```

---

### ❌ **Problem** (No Orders):

```
Tenant 4 (Ayam Geprek Mantap): 0 orders    ← Section 3
Tenant 4 (Ayam Geprek Mantap): 0 orders    ← Section 4
```

**Meaning**:
- Tidak ada orders sama sekali untuk tenant ini
- **Kitchen Display akan show "Tidak Ada Pesanan"**

**Fix**: Create order via Kiosk:
1. Open http://localhost:5174/kiosk
2. Filter by "Ayam Geprek Mantap"
3. Add items
4. Checkout
5. Run script again → should show 1 order

---

## 🔄 Complete Workflow

### **Step-by-Step Debugging**:

1. **Run Script**:
   ```cmd
   check_kitchen_orders.bat
   ```

2. **Check Output**:
   - Look at "KITCHEN DISPLAY FILTER" section
   - Find your tenant
   - Check order count

3. **If Count is 0**:
   - Check "ORDERS BY TENANT" section
   - If also 0 → **Create test order**
   - If > 0 → **Check status** in "ALL ORDERS" section

4. **Create Test Order**:
   - Open Kiosk
   - Select tenant
   - Add items
   - Checkout
   - Run script again

5. **Verify**:
   - Script should show order count > 0
   - Kitchen Display should show order

---

## 📋 Quick Reference

| What to Check | Where to Look | What it Means |
|--------------|---------------|---------------|
| Total orders in DB | "Total orders: X" | All orders across all tenants |
| Orders per tenant (all status) | "ORDERS BY TENANT" | How many orders tenant has |
| Orders per status | "ORDERS BY STATUS" | Distribution of order statuses |
| Kitchen Display count | "KITCHEN DISPLAY FILTER" | What Kitchen Display will show |

---

## ✅ Status

- **Status**: 🪟 **WINDOWS SCRIPTS READY**
- **Files Created**:
  - ✅ `check_kitchen_orders.bat` - Batch file (double-click)
  - ✅ `check_kitchen_orders.ps1` - PowerShell script (with colors)
  - ✅ `check_orders.py` - Python script (runs in Docker)
- **Commit**: Pending (will commit after this doc)
- **Documentation**: `WINDOWS_SCRIPTS_GUIDE.md` (this file)
- **GitHub**: https://github.com/dadinjaenudin/kiosk-svelte

---

## 🎯 RECOMMENDED USAGE

**For most users**:
1. Double-click `check_kitchen_orders.bat`
2. Read the output
3. Focus on "KITCHEN DISPLAY FILTER" section
4. Share screenshot if needed

**Simple!** 🚀

---

## 🆘 Need Help?

Share:
1. **Screenshot** of script output (full window)
2. **Which tenant** you're checking
3. **Console logs** from Kiosk (if you did checkout)
4. **Console logs** from Kitchen Display

**Dengan informasi ini, kita bisa diagnose exact issue!** 🔍
