# 🧪 USER TESTING GUIDE
## Food Court Multi-Tenant POS System

**Document Version:** 1.0  
**Last Updated:** January 3, 2026  
**Test Environment:** Docker Local Development  

---

## 📋 Table of Contents
1. [Pre-Testing Setup](#pre-testing-setup)
2. [Test Accounts](#test-accounts)
3. [Test Scenarios](#test-scenarios)
4. [Detailed Test Cases](#detailed-test-cases)
5. [Bug Report Template](#bug-report-template)
6. [Test Checklist](#test-checklist)

---

## 🚀 Pre-Testing Setup

### System Requirements
- Docker Desktop running
- All containers up: `docker-compose up`
- Sample data loaded: `.\setup_multi_outlet_test_docker.bat`

### URLs to Test
- **Admin Panel:** http://localhost:5175
- **Kiosk (Customer):** http://localhost:5174/kiosk
- **Kitchen Display:** http://localhost:5174/kitchen

### Test Data Summary
- **Tenants:** 3 (Pizza Paradise, Burger Station, Noodle House)
- **Outlets:** 6 (2 per tenant)
- **Products:** 12 (4 per tenant)
- **Users:** 20 (various roles)
- **Modifiers:** 10 (5 toppings + 5 spicy levels)

---

## 👥 Test Accounts

### Super Admin & Admin Accounts
| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| `superadmin` | `admin123` | super_admin | ALL TENANTS + Tenant Management |
| `admin` | `admin123` | admin | ALL TENANTS (no tenant create/delete) |

### Pizza Paradise Accounts
| Username | Password | Role | Access |
|----------|----------|------|--------|
| `pizza_owner` | `owner123` | tenant_owner | All Pizza outlets |
| `pizza_manager` | `manager123` | manager | Both Pizza outlets |
| `pizza_cashier` | `cashier123` | cashier | Main Branch only |
| `pizza_cashier2` | `cashier123` | cashier | North Branch only |
| `pizza_kitchen` | `kitchen123` | kitchen | Main Branch only |
| `pizza_kitchen2` | `kitchen123` | kitchen | North Branch only |

### Burger Station Accounts
| Username | Password | Role | Access |
|----------|----------|------|--------|
| `burger_owner` | `owner123` | tenant_owner | All Burger outlets |
| `burger_manager` | `manager123` | manager | Both Burger outlets |
| `burger_cashier` | `cashier123` | cashier | Central only |
| `burger_cashier2` | `cashier123` | cashier | West only |
| `burger_kitchen` | `kitchen123` | kitchen | Central only |
| `burger_kitchen2` | `kitchen123` | kitchen | West only |

### Noodle House Accounts
| Username | Password | Role | Access |
|----------|----------|------|--------|
| `noodle_owner` | `owner123` | tenant_owner | All Noodle outlets |
| `noodle_manager` | `manager123` | manager | Both Noodle outlets |
| `noodle_cashier` | `cashier123` | cashier | Downtown only |
| `noodle_cashier2` | `cashier123` | cashier | East only |
| `noodle_kitchen` | `kitchen123` | kitchen | Downtown only |
| `noodle_kitchen2` | `kitchen123` | kitchen | East only |

---

## 🎯 Test Scenarios

### Scenario 1: Super Admin - Full System Management
**User:** `superadmin` / `admin123`  
**Objective:** Test highest privilege level access

### Scenario 2: Admin - Cross-Tenant Support
**User:** `admin` / `admin123`  
**Objective:** Test admin operations across all tenants

### Scenario 3: Tenant Owner - Multi-Outlet Management
**User:** `pizza_owner` / `owner123`  
**Objective:** Test tenant-level management

### Scenario 4: Manager - Dual-Outlet Operations
**User:** `burger_manager` / `manager123`  
**Objective:** Test manager access to multiple outlets

### Scenario 5: Cashier - Single Outlet POS
**User:** `noodle_cashier` / `cashier123`  
**Objective:** Test outlet-specific access

### Scenario 6: Kitchen Staff - Order Display
**User:** `pizza_kitchen` / `kitchen123`  
**Objective:** Test kitchen display functionality

### Scenario 7: Customer - Self-Service Kiosk
**User:** (No login required)  
**Objective:** Test customer-facing kiosk

---

## 📝 Detailed Test Cases

## TEST CASE #1: Login & Authentication

### TC-1.1: Super Admin Login
**Priority:** High  
**Precondition:** None

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to http://localhost:5175 | Login page displayed | ☐ Pass ☐ Fail |
| 2 | Enter username: `superadmin` | Username field populated | ☐ Pass ☐ Fail |
| 3 | Enter password: `admin123` | Password masked with bullets | ☐ Pass ☐ Fail |
| 4 | Click "Login" button | Redirect to dashboard | ☐ Pass ☐ Fail |
| 5 | Check role badge | Shows "super_admin" badge | ☐ Pass ☐ Fail |
| 6 | Check navigation menu | All menu items visible | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

### TC-1.2: Tenant Owner Login
**Priority:** High  
**Precondition:** None

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to http://localhost:5175 | Login page displayed | ☐ Pass ☐ Fail |
| 2 | Enter username: `pizza_owner` | Username field populated | ☐ Pass ☐ Fail |
| 3 | Enter password: `owner123` | Password masked | ☐ Pass ☐ Fail |
| 4 | Click "Login" | Redirect to dashboard | ☐ Pass ☐ Fail |
| 5 | Check tenant badge | Shows "Pizza Paradise" | ☐ Pass ☐ Fail |
| 6 | Check tenant filter | NOT visible (owns only 1 tenant) | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

### TC-1.3: Invalid Login Attempt
**Priority:** High  
**Precondition:** None

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Enter username: `invalid_user` | Username field populated | ☐ Pass ☐ Fail |
| 2 | Enter password: `wrong_pass` | Password masked | ☐ Pass ☐ Fail |
| 3 | Click "Login" | Error message displayed | ☐ Pass ☐ Fail |
| 4 | Check error message | Shows "Invalid credentials" | ☐ Pass ☐ Fail |
| 5 | Verify still on login page | Login form still visible | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

## TEST CASE #2: Tenant Management

### TC-2.1: Super Admin - Create New Tenant
**Priority:** High  
**Precondition:** Logged in as `superadmin`

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to "Tenants" menu | Tenants page displayed | ☐ Pass ☐ Fail |
| 2 | Click "Add Tenant" button | Create form modal opens | ☐ Pass ☐ Fail |
| 3 | Enter name: "Sushi House" | Name field populated | ☐ Pass ☐ Fail |
| 4 | Enter slug: "sushi-house" | Slug field populated | ☐ Pass ☐ Fail |
| 5 | Enter email: "sushi@test.com" | Email field populated | ☐ Pass ☐ Fail |
| 6 | Select color: #FF5722 | Color picker shows selection | ☐ Pass ☐ Fail |
| 7 | Enable "Active" checkbox | Checkbox checked | ☐ Pass ☐ Fail |
| 8 | Click "Create" button | Success message appears | ☐ Pass ☐ Fail |
| 9 | Check tenants list | "Sushi House" appears in list | ☐ Pass ☐ Fail |
| 10 | Check tenant count stat | Total increased by 1 | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

### TC-2.2: Admin - Cannot Create Tenant
**Priority:** High  
**Precondition:** Logged in as `admin`

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to "Tenants" menu | Tenants page displayed | ☐ Pass ☐ Fail |
| 2 | Check for "Add Tenant" button | Button NOT visible or disabled | ☐ Pass ☐ Fail |
| 3 | Try to access create URL directly | Access denied or redirect | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

### TC-2.3: Tenant Owner - Cannot Access Tenants
**Priority:** High  
**Precondition:** Logged in as `pizza_owner`

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Check sidebar navigation | "Tenants" menu NOT visible | ☐ Pass ☐ Fail |
| 2 | Try navigate to /tenants | 403 Forbidden or redirect | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

## TEST CASE #3: Product Management

### TC-3.1: Create Product with Modifiers
**Priority:** High  
**Precondition:** Logged in as `pizza_owner`

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to "Products" menu | Products page displayed | ☐ Pass ☐ Fail |
| 2 | Click "Add Product" button | Create form opens | ☐ Pass ☐ Fail |
| 3 | Enter name: "Hawaiian Pizza" | Name field populated | ☐ Pass ☐ Fail |
| 4 | Enter SKU: "PIZZA-005" | SKU field populated | ☐ Pass ☐ Fail |
| 5 | Select category: "Pizza" | Category selected | ☐ Pass ☐ Fail |
| 6 | Enter price: 90000 | Price shows "Rp 90,000" | ☐ Pass ☐ Fail |
| 7 | Enter stock: 15 | Stock field shows 15 | ☐ Pass ☐ Fail |
| 8 | Enable "Available" | Checkbox checked | ☐ Pass ☐ Fail |
| 9 | Enable "Featured" | Checkbox checked | ☐ Pass ☐ Fail |
| 10 | Click "Create" | Success message appears | ☐ Pass ☐ Fail |
| 11 | Check products list | "Hawaiian Pizza" appears | ☐ Pass ☐ Fail |
| 12 | Verify modifiers available | Product has global modifiers | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

### TC-3.2: Tenant Filter - Products
**Priority:** High  
**Precondition:** Logged in as `admin`

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to "Products" menu | Products page displayed | ☐ Pass ☐ Fail |
| 2 | Check tenant selector | Dropdown visible in header | ☐ Pass ☐ Fail |
| 3 | Select "All Tenants" | All 12 products visible | ☐ Pass ☐ Fail |
| 4 | Select "Pizza Paradise" | Only Pizza products (4) shown | ☐ Pass ☐ Fail |
| 5 | Select "Burger Station" | Only Burger products (4) shown | ☐ Pass ☐ Fail |
| 6 | Select "Noodle House" | Only Noodle products (4) shown | ☐ Pass ☐ Fail |
| 7 | Check stats card | Stats update per tenant | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

## TEST CASE #4: Spicy Levels Management

### TC-4.1: View Spicy Levels
**Priority:** Medium  
**Precondition:** Logged in as any admin/manager

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to "Menu" → "Spicy Levels" | Spicy levels page displayed | ☐ Pass ☐ Fail |
| 2 | Check stats cards | Shows total, active, inactive | ☐ Pass ☐ Fail |
| 3 | Check table data | 5 levels visible (Level 1-5) | ☐ Pass ☐ Fail |
| 4 | Verify level names | All levels named correctly | ☐ Pass ☐ Fail |
| 5 | Check price adjustment | All show "Rp 0" | ☐ Pass ☐ Fail |
| 6 | Check sort order | Levels 1-5 in order | ☐ Pass ☐ Fail |
| 7 | Check status | All show "Active" badge | ☐ Pass ☐ Fail |
| 8 | Check action icons | ✏️ Edit and 🗑️ Delete visible | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

### TC-4.2: Create New Spicy Level
**Priority:** Medium  
**Precondition:** Logged in as `pizza_owner`

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to "Spicy Levels" | Page displayed | ☐ Pass ☐ Fail |
| 2 | Click "Add Spicy Level" | Create modal opens | ☐ Pass ☐ Fail |
| 3 | Enter name: "Level 6 (Maut)" | Name field populated | ☐ Pass ☐ Fail |
| 4 | Leave product: "Global" | Dropdown shows "Global" | ☐ Pass ☐ Fail |
| 5 | Enter price adjustment: 0 | Shows "Rp 0" | ☐ Pass ☐ Fail |
| 6 | Enter sort order: 6 | Field shows 6 | ☐ Pass ☐ Fail |
| 7 | Check "Active" | Checkbox checked | ☐ Pass ☐ Fail |
| 8 | Click "Create" | Success toast appears | ☐ Pass ☐ Fail |
| 9 | Check table | New level appears in list | ☐ Pass ☐ Fail |
| 10 | Check stats | Total count increased | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

### TC-4.3: Edit Spicy Level
**Priority:** Medium  
**Precondition:** Spicy levels exist

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to "Spicy Levels" | Page displayed | ☐ Pass ☐ Fail |
| 2 | Click ✏️ on "Level 1" | Edit modal opens | ☐ Pass ☐ Fail |
| 3 | Verify form populated | Shows current values | ☐ Pass ☐ Fail |
| 4 | Change name to "Level 1 (Mild)" | Name field updated | ☐ Pass ☐ Fail |
| 5 | Click "Update" | Success message appears | ☐ Pass ☐ Fail |
| 6 | Check table | Name changed to "Level 1 (Mild)" | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

### TC-4.4: Delete Spicy Level
**Priority:** Medium  
**Precondition:** Extra spicy level exists

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to "Spicy Levels" | Page displayed | ☐ Pass ☐ Fail |
| 2 | Click 🗑️ on "Level 6" | Delete confirmation modal | ☐ Pass ☐ Fail |
| 3 | Verify modal message | Shows level name in bold | ☐ Pass ☐ Fail |
| 4 | Click "Cancel" | Modal closes, no change | ☐ Pass ☐ Fail |
| 5 | Click 🗑️ again | Confirmation modal opens | ☐ Pass ☐ Fail |
| 6 | Click "Delete" (red button) | Success toast appears | ☐ Pass ☐ Fail |
| 7 | Check table | Level 6 removed from list | ☐ Pass ☐ Fail |
| 8 | Check stats | Total count decreased | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

## TEST CASE #5: Kiosk - Customer Experience

### TC-5.1: Browse Products in Kiosk
**Priority:** Critical  
**Precondition:** None (no login required)

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to http://localhost:5174/kiosk | Kiosk page loads | ☐ Pass ☐ Fail |
| 2 | Check layout | Product grid displayed | ☐ Pass ☐ Fail |
| 3 | Count visible products | All 12 products visible | ☐ Pass ☐ Fail |
| 4 | Check product cards | Image, name, price shown | ☐ Pass ☐ Fail |
| 5 | Check tenant badges | Each product shows tenant name | ☐ Pass ☐ Fail |
| 6 | Check category filter | Categories listed in sidebar | ☐ Pass ☐ Fail |
| 7 | Check tenant filter | All 3 tenants listed | ☐ Pass ☐ Fail |
| 8 | Check search box | Search input visible | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

### TC-5.2: Add Product to Cart with Modifiers
**Priority:** Critical  
**Precondition:** On kiosk page

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Click on "Margherita Pizza" | Modifier modal opens | ☐ Pass ☐ Fail |
| 2 | Verify modal title | Shows "Margherita Pizza" | ☐ Pass ☐ Fail |
| 3 | Check modifier sections | Shows 🧀 Toppings section | ☐ Pass ☐ Fail |
| 4 | Check spicy section | Shows 🌶️ Level Pedas section | ☐ Pass ☐ Fail |
| 5 | Select "Extra Cheese" | Checkbox checked, price updates | ☐ Pass ☐ Fail |
| 6 | Select "Mushrooms" | Checkbox checked, price updates | ☐ Pass ☐ Fail |
| 7 | Select "Level 3 (Pedas)" | Radio selected | ☐ Pass ☐ Fail |
| 8 | Check total price | Shows base + modifiers | ☐ Pass ☐ Fail |
| 9 | Calculation | Rp 85,000 + 5,000 + 3,000 = Rp 93,000 | ☐ Pass ☐ Fail |
| 10 | Enter quantity: 2 | Quantity field shows 2 | ☐ Pass ☐ Fail |
| 11 | Check final total | Shows Rp 186,000 (93k × 2) | ☐ Pass ☐ Fail |
| 12 | Add special notes: "No onions" | Notes field populated | ☐ Pass ☐ Fail |
| 13 | Click "Add to Cart" | Success, modal closes | ☐ Pass ☐ Fail |
| 14 | Check cart icon | Shows badge with "1" | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

### TC-5.3: Modify Cart Items
**Priority:** High  
**Precondition:** Items in cart

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Click cart icon | Cart sidebar opens | ☐ Pass ☐ Fail |
| 2 | Verify item details | Shows product, modifiers, price | ☐ Pass ☐ Fail |
| 3 | Check modifier display | Shows "Extra Cheese, Mushrooms" | ☐ Pass ☐ Fail |
| 4 | Check spicy level | Shows "Level 3 (Pedas)" | ☐ Pass ☐ Fail |
| 5 | Check notes | Shows "No onions" | ☐ Pass ☐ Fail |
| 6 | Click "+" quantity | Quantity increases to 3 | ☐ Pass ☐ Fail |
| 7 | Check total update | Price recalculated (93k × 3) | ☐ Pass ☐ Fail |
| 8 | Click "-" quantity | Quantity decreases to 2 | ☐ Pass ☐ Fail |
| 9 | Click remove item | Confirmation prompt appears | ☐ Pass ☐ Fail |
| 10 | Confirm removal | Item removed from cart | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

### TC-5.4: Checkout Process
**Priority:** Critical  
**Precondition:** Cart has items

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Add 2-3 different products | Cart shows multiple items | ☐ Pass ☐ Fail |
| 2 | Check cart total | Subtotal calculated correctly | ☐ Pass ☐ Fail |
| 3 | Click "Checkout" button | Payment modal opens | ☐ Pass ☐ Fail |
| 4 | Verify order summary | All items and totals shown | ☐ Pass ☐ Fail |
| 5 | Select payment: "Cash" | Cash option selected | ☐ Pass ☐ Fail |
| 6 | Enter amount: 500000 | Amount field shows Rp 500,000 | ☐ Pass ☐ Fail |
| 7 | Check change calculation | Change calculated automatically | ☐ Pass ☐ Fail |
| 8 | Click "Complete Order" | Processing indicator shows | ☐ Pass ☐ Fail |
| 9 | Wait for completion | Success modal appears | ☐ Pass ☐ Fail |
| 10 | Check order number | Unique order # displayed | ☐ Pass ☐ Fail |
| 11 | Check receipt | Full receipt shown | ☐ Pass ☐ Fail |
| 12 | Click "New Order" | Returns to product list | ☐ Pass ☐ Fail |
| 13 | Check cart | Cart is empty | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

## TEST CASE #6: Reports & Analytics

### TC-6.1: View Dashboard Analytics
**Priority:** High  
**Precondition:** Logged in as `admin`

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to "Dashboard" | Dashboard page loads | ☐ Pass ☐ Fail |
| 2 | Check stats cards | 4 stat cards visible | ☐ Pass ☐ Fail |
| 3 | Verify sales stat | Shows total sales amount | ☐ Pass ☐ Fail |
| 4 | Verify orders stat | Shows order count | ☐ Pass ☐ Fail |
| 5 | Check charts | Sales chart displayed | ☐ Pass ☐ Fail |
| 6 | Change date range | Data updates accordingly | ☐ Pass ☐ Fail |
| 7 | Select tenant filter | Dashboard filters by tenant | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

### TC-6.2: Tenant Owner - Limited Reports
**Priority:** High  
**Precondition:** Logged in as `pizza_owner`

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to "Reports" | Reports page loads | ☐ Pass ☐ Fail |
| 2 | Check tenant filter | NOT visible (auto-filtered) | ☐ Pass ☐ Fail |
| 3 | Check data shown | Only Pizza Paradise data | ☐ Pass ☐ Fail |
| 4 | Try to access other tenant | Cannot see other tenants | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

## TEST CASE #7: Outlet Management

### TC-7.1: Create Outlet
**Priority:** High  
**Precondition:** Logged in as `superadmin`

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to "Outlets" | Outlets page displayed | ☐ Pass ☐ Fail |
| 2 | Click "Add Outlet" | Create form opens | ☐ Pass ☐ Fail |
| 3 | Select tenant: "Pizza Paradise" | Tenant dropdown selected | ☐ Pass ☐ Fail |
| 4 | Enter name: "South Branch" | Name field populated | ☐ Pass ☐ Fail |
| 5 | Enter address: "South Street 123" | Address field populated | ☐ Pass ☐ Fail |
| 6 | Enter phone: "081234567890" | Phone field populated | ☐ Pass ☐ Fail |
| 7 | Enable "Active" | Checkbox checked | ☐ Pass ☐ Fail |
| 8 | Click "Create" | Success message appears | ☐ Pass ☐ Fail |
| 9 | Check outlets list | "South Branch" appears | ☐ Pass ☐ Fail |
| 10 | Verify tenant badge | Shows "Pizza Paradise" | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

### TC-7.2: Manager - Outlet Switching
**Priority:** High  
**Precondition:** Logged in as `pizza_manager`

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Check header area | Outlet selector visible | ☐ Pass ☐ Fail |
| 2 | Click outlet dropdown | Shows both outlets | ☐ Pass ☐ Fail |
| 3 | Select "Main Branch" | Badge updates to "Main Branch" | ☐ Pass ☐ Fail |
| 4 | Navigate to "Products" | Sees Main Branch + global products | ☐ Pass ☐ Fail |
| 5 | Switch to "North Branch" | Badge updates to "North Branch" | ☐ Pass ☐ Fail |
| 6 | Check products | Sees North Branch + global products | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

### TC-7.3: Cashier - Single Outlet Restriction
**Priority:** High  
**Precondition:** Logged in as `burger_cashier`

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Check header area | Outlet selector NOT visible | ☐ Pass ☐ Fail |
| 2 | Check outlet badge | Shows "Central" only | ☐ Pass ☐ Fail |
| 3 | Navigate to "Products" | Only Central + global products | ☐ Pass ☐ Fail |
| 4 | Check for "West" products | West-specific products NOT shown | ☐ Pass ☐ Fail |
| 5 | Try to access other outlet | Cannot switch outlets | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

## TEST CASE #8: Permissions & Access Control

### TC-8.1: Kitchen Staff - Limited Access
**Priority:** High  
**Precondition:** Logged in as `noodle_kitchen`

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Check sidebar menu | Limited menu items | ☐ Pass ☐ Fail |
| 2 | Verify visible menus | Only: Dashboard, Orders, Kitchen | ☐ Pass ☐ Fail |
| 3 | Check for Products menu | NOT visible | ☐ Pass ☐ Fail |
| 4 | Check for Reports menu | NOT visible | ☐ Pass ☐ Fail |
| 5 | Try access /products URL | 403 Forbidden or redirect | ☐ Pass ☐ Fail |
| 6 | Navigate to "Kitchen Display" | Kitchen page accessible | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

### TC-8.2: Cross-Tenant Access Prevention
**Priority:** Critical  
**Precondition:** Logged in as `pizza_owner`

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Navigate to "Products" | Products page loads | ☐ Pass ☐ Fail |
| 2 | Check visible products | Only Pizza products (4 items) | ☐ Pass ☐ Fail |
| 3 | Verify no Burger products | Burger products NOT visible | ☐ Pass ☐ Fail |
| 4 | Verify no Noodle products | Noodle products NOT visible | ☐ Pass ☐ Fail |
| 5 | Check tenant selector | NOT visible (single tenant) | ☐ Pass ☐ Fail |
| 6 | Try edit Burger product (API) | 403 Forbidden response | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

## TEST CASE #9: Responsive & UI/UX

### TC-9.1: Mobile Responsiveness
**Priority:** Medium  
**Precondition:** Any logged in user

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Resize browser to 375px width | Mobile view activated | ☐ Pass ☐ Fail |
| 2 | Check sidebar | Collapses to hamburger menu | ☐ Pass ☐ Fail |
| 3 | Check header | Responsive layout | ☐ Pass ☐ Fail |
| 4 | Check tables | Horizontal scroll or stacked | ☐ Pass ☐ Fail |
| 5 | Check forms | Full width, touch-friendly | ☐ Pass ☐ Fail |
| 6 | Check modals | Fit screen, readable | ☐ Pass ☐ Fail |
| 7 | Test kiosk on mobile | Touch-friendly, readable | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

### TC-9.2: Kiosk Touch Interface
**Priority:** High  
**Precondition:** On kiosk page

| Step | Action | Expected Result | Status |
|------|--------|----------------|--------|
| 1 | Check product cards | Large, touch-friendly buttons | ☐ Pass ☐ Fail |
| 2 | Check modifier selections | Easy to tap checkboxes/radios | ☐ Pass ☐ Fail |
| 3 | Check quantity controls | Large +/- buttons | ☐ Pass ☐ Fail |
| 4 | Check cart button | Fixed position, always visible | ☐ Pass ☐ Fail |
| 5 | Test fullscreen mode | Press F11, app fills screen | ☐ Pass ☐ Fail |

**Notes:**
_____________________________________

---

## 🐛 Bug Report Template

When you find a bug, document it using this format:

```markdown
### BUG-XXX: [Brief Description]

**Severity:** ☐ Critical ☐ High ☐ Medium ☐ Low
**Priority:** ☐ P1 ☐ P2 ☐ P3 ☐ P4

**Environment:**
- Date: [YYYY-MM-DD]
- Browser: [Chrome/Firefox/Edge]
- Version: [Version number]
- User Role: [Role used during test]

**Preconditions:**
1. [Step 1]
2. [Step 2]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Result:**
[What should happen]

**Actual Result:**
[What actually happens]

**Screenshots/Evidence:**
[Attach screenshots or video]

**Console Errors:**
```
[Paste any console errors]
```

**Additional Notes:**
[Any other relevant information]
```

---

## ✅ Test Checklist

### Authentication & Authorization
- [ ] Super Admin can login
- [ ] Admin can login
- [ ] Tenant Owner can login
- [ ] Manager can login
- [ ] Cashier can login
- [ ] Kitchen staff can login
- [ ] Invalid credentials rejected
- [ ] Logout works correctly
- [ ] Session persistence works
- [ ] Password reset works (if implemented)

### Tenant Management
- [ ] Super Admin can create tenants
- [ ] Super Admin can edit tenants
- [ ] Super Admin can delete tenants
- [ ] Admin cannot create/delete tenants
- [ ] Tenant Owner cannot access tenant management
- [ ] Tenant data isolated correctly

### Outlet Management
- [ ] Super Admin can create outlets
- [ ] Tenant Owner can create outlets
- [ ] Manager can see assigned outlets
- [ ] Cashier sees only their outlet
- [ ] Outlet switching works for managers
- [ ] Products filter by outlet correctly

### Product Management
- [ ] Create product works
- [ ] Edit product works
- [ ] Delete product works
- [ ] Product images upload correctly
- [ ] Stock tracking works
- [ ] Outlet-specific products shown correctly
- [ ] Global products visible to all outlets
- [ ] Tenant filter works (for admin)

### Modifiers Management
- [ ] View toppings list
- [ ] Create new topping
- [ ] Edit topping
- [ ] Delete topping
- [ ] View spicy levels list
- [ ] Create new spicy level
- [ ] Edit spicy level
- [ ] Delete spicy level
- [ ] Global modifiers visible to all products
- [ ] Product-specific modifiers work

### Kiosk - Customer Experience
- [ ] Products display correctly
- [ ] Product images load
- [ ] Tenant badges show
- [ ] Category filter works
- [ ] Tenant filter works
- [ ] Search works
- [ ] Quick filters work (Popular, Promo, Available)
- [ ] Product detail modal opens
- [ ] Modifier selection works
- [ ] Spicy level selection works
- [ ] Multiple toppings selection works
- [ ] Price calculation correct
- [ ] Quantity control works
- [ ] Special notes input works
- [ ] Add to cart works
- [ ] Cart shows all items
- [ ] Cart grouped by tenant
- [ ] Modify cart quantity works
- [ ] Remove from cart works
- [ ] Clear cart works
- [ ] Checkout process works
- [ ] Payment methods selectable
- [ ] Cash payment with change calculation
- [ ] Order confirmation shows
- [ ] Receipt displays correctly

### Orders Management
- [ ] View orders list
- [ ] Filter orders by status
- [ ] Filter orders by date
- [ ] Filter orders by outlet (for managers)
- [ ] Order details display
- [ ] Update order status
- [ ] Cancel order
- [ ] Print receipt
- [ ] Kitchen display shows new orders
- [ ] Kitchen can mark orders complete

### Reports & Analytics
- [ ] Dashboard loads correctly
- [ ] Sales stats accurate
- [ ] Charts display data
- [ ] Date range filter works
- [ ] Tenant filter works (for admin)
- [ ] Export reports works
- [ ] Tenant Owner sees only own data
- [ ] Manager sees assigned outlets data

### User Management
- [ ] Create user works
- [ ] Edit user works
- [ ] Delete user works
- [ ] Role assignment works
- [ ] Outlet assignment works (for managers/cashiers)
- [ ] Cannot create users for other tenants
- [ ] Email validation works

### UI/UX
- [ ] Sidebar navigation works
- [ ] Grouped navigation displays correctly
- [ ] Page titles correct
- [ ] Breadcrumbs work
- [ ] Toast notifications appear
- [ ] Loading states show
- [ ] Error messages clear
- [ ] Form validation works
- [ ] Modals open/close correctly
- [ ] Responsive on mobile
- [ ] Touch-friendly on tablet
- [ ] Fullscreen mode works (kiosk)

### Performance
- [ ] Page load < 3 seconds
- [ ] API responses < 1 second
- [ ] No memory leaks
- [ ] Images optimized
- [ ] No console errors
- [ ] Smooth scrolling
- [ ] Quick transitions

---

## 📊 Test Summary Report

**Test Session:** __________  
**Tester Name:** __________  
**Date:** __________  
**Duration:** __________ hours

### Summary Statistics

| Category | Total Tests | Passed | Failed | Blocked | Pass Rate |
|----------|-------------|--------|--------|---------|-----------|
| Authentication | | | | | % |
| Tenant Management | | | | | % |
| Product Management | | | | | % |
| Modifiers | | | | | % |
| Kiosk | | | | | % |
| Orders | | | | | % |
| Reports | | | | | % |
| Permissions | | | | | % |
| UI/UX | | | | | % |
| **TOTAL** | | | | | % |

### Critical Issues Found
1. [Bug ID] - [Brief description]
2. [Bug ID] - [Brief description]

### Recommendations
1. [Recommendation 1]
2. [Recommendation 2]

### Sign-off
- [ ] All critical tests passed
- [ ] All high-priority tests passed
- [ ] No critical bugs found
- [ ] Ready for production

**Tester Signature:** __________  
**Date:** __________

---

## 📞 Support & Questions

For questions or issues during testing:
- **Developer:** [Contact info]
- **Test Lead:** [Contact info]
- **Bug Reports:** Create issue in repository

---

**Document End** 🎉
