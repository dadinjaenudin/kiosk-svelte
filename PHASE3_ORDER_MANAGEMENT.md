# Phase 3: Order Management System - Complete Guide

**Status**: ✅ COMPLETED  
**Date**: 2025-12-28  
**Version**: 1.0

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Backend API](#backend-api)
4. [Frontend UI](#frontend-ui)
5. [User Guide](#user-guide)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

Phase 3 introduces a comprehensive **Order Management System** for the Admin Panel, enabling administrators, tenant owners, and outlet managers to view, filter, track, and manage orders in real-time.

### What's New

- **Order List with Advanced Filters** - Search, filter, and sort orders
- **Order Detail View** - Complete order information with timeline
- **Status Management** - Update order status with workflow controls
- **Receipt Generation** - Print-ready receipt data
- **Analytics** - Order statistics and insights
- **Role-Based Access** - Different permissions for different user roles

---

## ✨ Features

### 1. Order List Page

**Location**: `/orders`

**Features**:
- 🔍 **Search**: Order number, customer name, phone, table number
- 🏷️ **Status Filters**: Filter by multiple order statuses (pending, preparing, ready, etc.)
- 💳 **Payment Filters**: Filter by payment status (unpaid, pending, paid)
- 📅 **Date Range**: Filter orders by date range
- 📊 **Sorting**: Sort by date (newest/oldest) or amount (highest/lowest)
- 📱 **Responsive**: Desktop table view, mobile card view
- 📄 **Pagination**: Navigate through large order lists

**Available Filters**:
- Order Status: `pending`, `confirmed`, `preparing`, `ready`, `served`, `completed`, `cancelled`
- Payment Status: `unpaid`, `pending`, `paid`, `refunded`
- Date Range: Start date and end date
- Search: Text search across order number, customer info, table number
- Sort: Created date, total amount (ascending/descending)

### 2. Order Detail Page

**Location**: `/orders/{id}`

**Displays**:
- **Order Summary**: Order number, date, status, payment status
- **Customer Information**: Name, phone, table number, notes
- **Tenant Information**: Restaurant/tenant name
- **Order Items**: Complete list with quantities, prices, modifiers, notes
- **Order Timeline**: Visual timeline of order status progression
- **Totals Breakdown**: Subtotal, tax, service charge, discount, total

**Actions**:
- ✏️ **Update Status**: Change order status based on workflow
- 🖨️ **Print Receipt**: Generate printable receipt

### 3. Order Timeline

Tracks order progression through these stages:

1. **Order Placed** (Pending) - Customer places order
2. **Confirmed** - Order confirmed by restaurant
3. **Preparing** - Kitchen preparing the order
4. **Ready** - Order ready for pickup/serving
5. **Served** - Order served to customer
6. **Completed** - Order completed and paid

**Special Statuses**:
- **Cancelled** - Order cancelled at any stage
- **Draft** - Order in draft state (not shown to customer)

### 4. Status Workflow

**Status Transitions** (what can be changed from current status):

- From `pending` → `confirmed`, `cancelled`
- From `confirmed` → `preparing`, `cancelled`
- From `preparing` → `ready`, `cancelled`
- From `ready` → `served`, `cancelled`
- From `served` → `completed`
- `completed` and `cancelled` are final states (no further changes)

### 5. Role-Based Access

**Admin (Super Admin)**:
- View ALL orders across all tenants
- Full access to all features

**Tenant Owner**:
- View only THEIR tenant's orders
- Manage orders for their restaurants

**Outlet Manager**:
- View only THEIR outlet's orders
- Manage orders for their specific location

**Other Roles**:
- No access to order management

---

## 🔧 Backend API

### Base URL
```
/api/admin/orders/
```

### Endpoints

#### 1. List Orders
```http
GET /api/admin/orders/
```

**Query Parameters**:
- `status` (multiple): Filter by status(es)
- `payment_status`: Filter by payment status
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `search`: Search term
- `tenant`: Tenant ID
- `outlet`: Outlet ID
- `ordering`: Sort field (e.g., `-created_at`, `total_amount`)
- `page`: Page number

**Example**:
```http
GET /api/admin/orders/?status=pending&status=preparing&start_date=2025-12-01&ordering=-created_at
```

**Response**:
```json
{
  "count": 150,
  "next": "/api/admin/orders/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "order_number": "ORD-20251228-A1B2",
      "tenant": 1,
      "tenant_name": "Warung Nasi Padang",
      "tenant_color": "#FF5722",
      "outlet": 1,
      "status": "preparing",
      "customer_name": "John Doe",
      "customer_phone": "08123456789",
      "table_number": "A5",
      "total_amount": "125000.00",
      "payment_status": "paid",
      "items": [...],
      "created_at": "2025-12-28T10:30:00Z",
      "updated_at": "2025-12-28T10:35:00Z"
    }
  ]
}
```

#### 2. Get Order Detail
```http
GET /api/admin/orders/{id}/
```

**Response**: Single order object with all details

#### 3. Update Order Status
```http
POST /api/admin/orders/{id}/update_status/
```

**Body**:
```json
{
  "status": "preparing"
}
```

**Response**:
```json
{
  "message": "Order status updated successfully",
  "order_number": "ORD-20251228-A1B2",
  "old_status": "confirmed",
  "new_status": "preparing",
  "order": {...}
}
```

#### 4. Get Order Timeline
```http
GET /api/admin/orders/{id}/timeline/
```

**Response**:
```json
{
  "order_number": "ORD-20251228-A1B2",
  "current_status": "preparing",
  "timeline": [
    {
      "status": "pending",
      "label": "Order Placed",
      "timestamp": "2025-12-28T10:30:00Z",
      "completed": true
    },
    {
      "status": "confirmed",
      "label": "Confirmed",
      "timestamp": "2025-12-28T10:32:00Z",
      "completed": true
    },
    {
      "status": "preparing",
      "label": "Preparing",
      "timestamp": "2025-12-28T10:35:00Z",
      "completed": true
    },
    {
      "status": "ready",
      "label": "Ready to Serve",
      "timestamp": null,
      "completed": false
    }
  ]
}
```

#### 5. Get Receipt Data
```http
GET /api/admin/orders/{id}/receipt/
```

**Response**: Complete receipt data for printing (order info, items, totals, tenant/outlet info)

#### 6. Get Order Statistics
```http
GET /api/admin/orders/statistics/?period=today
```

**Query Parameters**:
- `period`: `today`, `week`, `month`, `year`

**Response**:
```json
{
  "period": "today",
  "start_date": "2025-12-28T00:00:00Z",
  "end_date": "2025-12-28T23:59:59Z",
  "total_orders": 45,
  "total_revenue": 5625000.0,
  "orders_by_status": {
    "pending": 8,
    "preparing": 12,
    "ready": 5,
    "completed": 20
  },
  "orders_by_payment_status": {
    "unpaid": 10,
    "paid": 35
  },
  "top_selling_items": [
    {
      "product_name": "Ayam Geprek Keju",
      "total_quantity": 45,
      "total_revenue": 1575000.0
    }
  ],
  "average_order_value": 125000.0
}
```

---

## 🎨 Frontend UI

### Files Created

1. **API Client**: `admin/src/lib/api/orders.js`
   - API functions for all order operations
   - Utility functions for formatting (currency, dates, status)

2. **Order List Page**: `admin/src/routes/orders/+page.svelte`
   - Main order list with filters
   - Search and sort functionality
   - Pagination

3. **Order Detail Page**: `admin/src/routes/orders/[id]/+page.svelte`
   - Complete order information
   - Interactive timeline
   - Status update modal
   - Receipt print functionality

### UI Components

**Status Badges**:
- Color-coded status pills
- Clear visual indication of order state

**Timeline Component**:
- Vertical timeline with checkpoints
- Completed steps in primary color
- Pending steps in gray
- Timestamp for each completed step

**Filters Panel**:
- Collapsible filter section
- Multi-select status filter
- Date range picker
- Payment status dropdown

**Responsive Design**:
- Desktop: Full table layout
- Mobile: Card-based layout
- Touch-friendly buttons and actions

---

## 📖 User Guide

### How to Use Order Management

#### Viewing Orders

1. **Navigate to Orders**:
   - Click "Orders" in the sidebar
   - Or go to `/orders` in your browser

2. **Search for an Order**:
   - Use the search box to find orders by:
     - Order number (e.g., "ORD-20251228")
     - Customer name
     - Phone number
     - Table number

3. **Filter Orders**:
   - Click "▼ Filters" to show filter options
   - Select status(es) by clicking status pills
   - Choose payment status from dropdown
   - Set date range if needed
   - Click "Reset Filters" to clear all filters

4. **Sort Orders**:
   - Use the sort dropdown to change order
   - Options: Newest First, Oldest First, Highest Amount, Lowest Amount

#### Viewing Order Details

1. **Click on an Order**:
   - Click any order row in the table
   - Or click "View →" button

2. **Review Order Information**:
   - See order summary at the top
   - Check customer information on the right
   - Review order items with modifiers
   - View order totals breakdown
   - See order timeline

#### Updating Order Status

1. **Click "Update Status"** button
2. **Select New Status** from dropdown
   - Only valid next statuses are shown
3. **Click "Update Status"** to confirm
4. Order timeline updates automatically

#### Printing Receipt

1. **Click "🖨️ Print Receipt"** button
2. Receipt data loads in modal
3. Click browser print (Ctrl+P or Cmd+P)
4. Print or save as PDF

---

## 🧪 Testing

### Testing Checklist

#### Backend Testing

1. **API Endpoints**:
   ```bash
   # Test order list
   curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8001/api/admin/orders/
   
   # Test order detail
   curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8001/api/admin/orders/1/
   
   # Test status update
   curl -X POST \
     -H "Authorization: Token YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"status":"preparing"}' \
     http://localhost:8001/api/admin/orders/1/update_status/
   
   # Test statistics
   curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8001/api/admin/orders/statistics/?period=today
   ```

2. **Role-Based Access**:
   - Test as Admin: Should see all orders
   - Test as Tenant Owner: Should see only their tenant's orders
   - Test as Outlet Manager: Should see only their outlet's orders

3. **Filters**:
   - Test status filters
   - Test payment status filters
   - Test date range filters
   - Test search functionality
   - Test sorting

#### Frontend Testing

1. **Order List Page**:
   - ✅ Page loads without errors
   - ✅ Orders display correctly
   - ✅ Search works
   - ✅ Filters work
   - ✅ Sorting works
   - ✅ Pagination works
   - ✅ Click order navigates to detail

2. **Order Detail Page**:
   - ✅ Order details load correctly
   - ✅ All order information displays
   - ✅ Timeline shows correct progression
   - ✅ Status update modal opens
   - ✅ Status update works
   - ✅ Receipt data loads

3. **Responsive Design**:
   - ✅ Desktop view looks good
   - ✅ Mobile view looks good
   - ✅ Tablets display correctly

### Test Scenarios

#### Scenario 1: Create and Track Order

1. Create a new order from Kiosk (`http://localhost:5174/kiosk`)
2. Go to Admin Panel (`http://localhost:5175/orders`)
3. Find the new order (it should appear at the top)
4. Click to view details
5. Update status: pending → confirmed → preparing → ready → served → completed
6. Verify timeline updates after each status change

#### Scenario 2: Filter and Search

1. Go to Orders page
2. Toggle filters panel
3. Select "Preparing" and "Ready" statuses
4. Orders should filter to show only those statuses
5. Clear filters
6. Search for an order number
7. Order should appear in results

#### Scenario 3: Receipt Printing

1. Open an order detail
2. Click "Print Receipt"
3. Verify receipt data loads correctly
4. Print or save as PDF

---

## 🔧 Troubleshooting

### Common Issues

#### Issue 1: Orders Not Loading

**Symptoms**: Blank page, spinner doesn't stop, or error message

**Solutions**:
1. Check backend is running: `docker-compose ps backend`
2. Check backend logs: `docker-compose logs backend --tail=50`
3. Verify authentication: Check token in browser DevTools → Application → Local Storage
4. Check API endpoint: `curl http://localhost:8001/api/admin/orders/` with token

#### Issue 2: Status Update Fails

**Symptoms**: Error when updating status

**Solutions**:
1. Check if status transition is valid (e.g., can't go from `completed` to `preparing`)
2. Verify user has permission to update orders
3. Check backend logs for errors
4. Ensure order ID is correct

#### Issue 3: Filters Not Working

**Symptoms**: Filters applied but no results change

**Solutions**:
1. Check browser console for errors
2. Verify filter parameters are being sent (Network tab in DevTools)
3. Check backend logs for query errors
4. Try resetting filters

#### Issue 4: Receipt Not Printing

**Symptoms**: Receipt data doesn't load or print dialog doesn't open

**Solutions**:
1. Check order has all required data
2. Verify receipt endpoint returns data: `curl http://localhost:8001/api/admin/orders/{id}/receipt/`
3. Check browser print settings
4. Try different browser

### Debug Mode

Enable detailed logging in browser console:

```javascript
// In browser console
localStorage.setItem('debug', 'true');
// Reload page
```

View API requests:
1. Open DevTools (F12)
2. Go to Network tab
3. Filter by "Fetch/XHR"
4. Click any request to see details

---

## 📊 Database Schema

### Order Model

```python
class Order(models.Model):
    # Relations
    tenant = ForeignKey(Tenant)
    outlet = ForeignKey(Outlet)
    cashier = ForeignKey(User)
    
    # Identification
    order_number = CharField(max_length=50, unique=True)
    
    # Status
    status = CharField(choices=STATUS_CHOICES)
    payment_status = CharField()
    
    # Customer
    customer_name = CharField()
    customer_phone = CharField()
    customer_email = EmailField()
    
    # Details
    table_number = CharField()
    notes = TextField()
    
    # Pricing
    subtotal = DecimalField()
    tax_amount = DecimalField()
    service_charge_amount = DecimalField()
    discount_amount = DecimalField()
    total_amount = DecimalField()
    paid_amount = DecimalField()
    
    # Timestamps
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    completed_at = DateTimeField(null=True)
```

### OrderItem Model

```python
class OrderItem(models.Model):
    order = ForeignKey(Order)
    product = ForeignKey(Product)
    
    product_name = CharField()  # Snapshot
    product_sku = CharField()
    
    quantity = IntegerField()
    unit_price = DecimalField()
    modifiers = JSONField()  # List of modifiers
    modifiers_price = DecimalField()
    total_price = DecimalField()
    notes = TextField()
```

---

## 🚀 Deployment Notes

### Environment Variables

No additional environment variables needed for Phase 3.

### Database Migrations

Run migrations after deploying:

```bash
docker-compose exec backend python manage.py migrate
```

### Static Files

Collect static files:

```bash
docker-compose exec backend python manage.py collectstatic --noinput
```

---

## 📝 API Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/orders/` | GET | List orders with filters |
| `/api/admin/orders/{id}/` | GET | Get order detail |
| `/api/admin/orders/{id}/update_status/` | POST | Update order status |
| `/api/admin/orders/{id}/timeline/` | GET | Get order timeline |
| `/api/admin/orders/{id}/receipt/` | GET | Get receipt data |
| `/api/admin/orders/statistics/` | GET | Get order statistics |

---

## ✅ Phase 3 Complete!

**What's Been Built**:
- ✅ Complete Order Management System
- ✅ Advanced filtering and search
- ✅ Order detail with timeline
- ✅ Status update workflow
- ✅ Receipt generation
- ✅ Role-based permissions
- ✅ Responsive design
- ✅ Analytics and statistics

**Next Steps** (Phase 4):
- Customer Management
- Promo Management (advanced)
- Reports and Analytics Dashboard
- Export functionality

---

## 📞 Support

For issues or questions:
1. Check this documentation
2. Check backend logs: `docker-compose logs backend`
3. Check browser console (F12)
4. Review API responses in Network tab

---

**Last Updated**: 2025-12-28  
**Version**: 1.0  
**Status**: Production Ready ✅