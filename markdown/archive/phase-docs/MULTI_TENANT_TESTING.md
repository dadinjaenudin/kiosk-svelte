===============
🎯 MULTI-OUTLET TEST DATA SETUP COMPLETE
================================================================================


Test Accounts Available:
superadmin / admin123 - Super Admin
admin / admin123 - Admin
pizza_owner / owner123 - Tenant Owner (all Pizza outlets)
pizza_manager / manager123 - Manager (both outlets)
pizza_cashier / cashier123 - Cashier (Main Branch)
burger_cashier2 / cashier123 - Cashier (West Branch)
Dan 14 user lainnya...
Sekarang sistem multi-outlet sudah siap digunakan dengan script setup yang bersih! 🎊

🔑 Perbedaan Admin vs Super Admin
Super Admin (Level 100)
- Highest authority dalam platform
- Bisa manage TENANTS (create/delete tenant)
- Bisa manage semua USERS (termasuk admin)
- Bisa akses semua data di semua tenant
- Biasanya: Platform owner / System administrator

Admin (Level 90)
- High authority tapi bukan platform owner
- Bisa manage USERS (tapi mungkin tidak bisa delete super_admin)
- Bisa akses semua data di semua tenant
- TIDAK bisa create/delete TENANTS (hanya super_admin)
- Biasanya: Support team / Operations manager

📊 Permission Matrix
Feature	Super Admin	Admin	Tenant Owner	Manager
Create/Delete Tenants	✅	❌	❌	❌
Manage All Users	✅	✅	❌	❌
Access All Tenants	✅	✅	❌	❌
Access All Outlets	✅	✅	❌ (only own tenant)	❌ (only assigned)
View All Orders	✅	✅	✅ (own tenant)	✅ (own outlets)
Manage Products	✅	✅	✅	✅
System Configuration	✅	❌	❌	❌

🎯 Use Cases
Super Admin
Skenario: Platform owner yang jalankan food court system
Akses: Bisa create tenant baru saat ada restoran baru join
Contoh: "Saya mau tambah tenant baru: Sushi House"

Admin
Skenario: Customer support atau operations team
Akses: Bantu troubleshoot masalah di semua tenant, tapi tidak bisa hapus tenant
Contoh: "User pizza_cashier lupa password, saya reset"

Tenant Owner
Skenario: Pemilik franchise (misalnya pemilik semua outlet Pizza House)
Akses: Hanya manage outlet-outlet Pizza House, tidak bisa lihat Burger King

Manager
Skenario: Manager outlet spesifik
Akses: Manage 1-2 outlet saja dalam tenant


📊 TEST ACCOUNTS:
--------------------------------------------------------------------------------
Username                  Password        Role            Details

--------------------------------------------------------------------------------
superadmin                admin123        super_admin     ALL TENANTS
admin                     admin123        admin           ALL TENANTS
--------------------------------------------------------------------------------
pizza_owner              owner123        tenant_owner    All outlets
pizza_manager            manager123      manager         Both outlets
pizza_cashier            cashier123      cashier         Main branch
pizza_cashier2           cashier123      cashier         Branch 2

pizza_kitchen            kitchen123      kitchen         Main branch
pizza_kitchen2           kitchen123      kitchen         Branch 2

--------------------------------------------------------------------------------
burger_owner             owner123        tenant_owner    All outlets
burger_manager           manager123      manager         Both outlets
burger_cashier           cashier123      cashier         Main branch
burger_cashier2          cashier123      cashier         Branch 2

burger_kitchen           kitchen123      kitchen         Main branch
burger_kitchen2          kitchen123      kitchen         Branch 2

--------------------------------------------------------------------------------
noodle_owner             owner123        tenant_owner    All outlets
noodle_manager           manager123      manager         Both outlets
noodle_cashier           cashier123      cashier         Main branch
noodle_cashier2          cashier123      cashier         Branch 2

noodle_kitchen           kitchen123      kitchen         Main branch
noodle_kitchen2          kitchen123      kitchen         Branch 2

--------------------------------------------------------------------------------