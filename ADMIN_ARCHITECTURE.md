# 🎯 Admin Web App Architecture - Best Practice

## Overview

Untuk fitur **Order Tracking**, **Reprint Receipts**, **Customer History**, **Dashboard**, dan **Promo Management**, saya rekomendasikan membuat **Admin Web Application** terpisah dari Kiosk.

---

## ✅ Mengapa Butuh Admin App Terpisah?

### Keuntungan:

1. **Separation of Concerns**
   - Kiosk = Customer-facing (simple, fast)
   - Admin = Management (complex, feature-rich)
   - Tidak membebani kiosk dengan fitur admin

2. **Security**
   - Admin butuh authentication & authorization
   - Role-based access (Owner, Manager, Cashier)
   - Audit trails untuk sensitive operations

3. **Different UX Requirements**
   - Kiosk: Touch-optimized, large buttons
   - Admin: Desktop-optimized, data-heavy tables, charts

4. **Scalability**
   - Admin bisa di-host terpisah
   - Tidak affect performa kiosk
   - Bisa dikembangkan independent

5. **Multi-Tenant Support**
   - Satu admin untuk manage multiple outlets
   - Centralized management

---

## 🏗️ Recommended Tech Stack

### Frontend: **SvelteKit** (Consistency with existing)

**Why SvelteKit for Admin?**
- ✅ Same tech stack = easier maintenance
- ✅ Code reuse (components, stores, utils)
- ✅ SSR for better initial load
- ✅ Built-in routing
- ✅ TypeScript support

**Alternative:** Next.js, Nuxt, or plain React/Vue
- Use if team sudah expert di framework lain

### Backend: **Django REST API** (Existing)

**Extend existing backend dengan:**
- ✅ Admin-specific endpoints
- ✅ Authentication middleware
- ✅ Permission decorators
- ✅ Analytics aggregations

### Real-time: **Django Channels (WebSocket)**

**For:**
- ✅ Live order updates
- ✅ Real-time dashboard metrics
- ✅ Kitchen display sync
- ✅ Notifications

### Database: **PostgreSQL** (Existing)

**New tables needed:**
- `customers` - Customer profiles
- `customer_orders` - Link customers to orders
- `promotions` - Promo campaigns
- `promo_products` - Products in promo
- `loyalty_points` - Optional loyalty system
- `audit_logs` - Admin action tracking

### UI Library: **shadcn/ui + Tailwind**

**Why:**
- ✅ Beautiful, modern components
- ✅ Accessible out of the box
- ✅ Customizable with Tailwind
- ✅ Copy-paste components (no npm bloat)

**Alternative:** DaisyUI, Flowbite, or Material UI

### Charts: **Chart.js** or **Apache ECharts**

**For:**
- Sales trends
- Product performance
- Revenue analytics

---

## 📂 Project Structure

```
kiosk-svelte/
├── frontend/              # Existing Kiosk
├── kitchen/               # Existing Kitchen Display
├── admin/                 # NEW: Admin Web App
│   ├── src/
│   │   ├── routes/
│   │   │   ├── +layout.svelte          # Main layout with sidebar
│   │   │   ├── +page.svelte            # Dashboard home
│   │   │   ├── login/
│   │   │   │   └── +page.svelte        # Login page
│   │   │   ├── dashboard/
│   │   │   │   └── +page.svelte        # Main dashboard
│   │   │   ├── orders/
│   │   │   │   ├── +page.svelte        # Order list
│   │   │   │   └── [id]/
│   │   │   │       └── +page.svelte    # Order detail & reprint
│   │   │   ├── customers/
│   │   │   │   ├── +page.svelte        # Customer list
│   │   │   │   └── [id]/
│   │   │   │       └── +page.svelte    # Customer history
│   │   │   ├── promotions/
│   │   │   │   ├── +page.svelte        # Promo list
│   │   │   │   ├── create/
│   │   │   │   │   └── +page.svelte    # Create promo
│   │   │   │   └── [id]/
│   │   │   │       └── +page.svelte    # Edit promo
│   │   │   ├── products/
│   │   │   │   ├── +page.svelte        # Product management
│   │   │   │   └── [id]/
│   │   │   │       └── +page.svelte    # Edit product
│   │   │   ├── reports/
│   │   │   │   ├── +page.svelte        # Reports hub
│   │   │   │   ├── sales/
│   │   │   │   ├── products/
│   │   │   │   └── customers/
│   │   │   └── settings/
│   │   │       ├── +page.svelte        # Settings
│   │   │       ├── users/              # User management
│   │   │       └── outlets/            # Outlet management
│   │   ├── lib/
│   │   │   ├── components/
│   │   │   │   ├── Dashboard/
│   │   │   │   │   ├── SalesChart.svelte
│   │   │   │   │   ├── RevenueCard.svelte
│   │   │   │   │   ├── TopProducts.svelte
│   │   │   │   │   └── RecentOrders.svelte
│   │   │   │   ├── Orders/
│   │   │   │   │   ├── OrderList.svelte
│   │   │   │   │   ├── OrderDetailModal.svelte
│   │   │   │   │   ├── OrderTimeline.svelte
│   │   │   │   │   └── ReprintReceipt.svelte
│   │   │   │   ├── Customers/
│   │   │   │   │   ├── CustomerList.svelte
│   │   │   │   │   ├── CustomerCard.svelte
│   │   │   │   │   ├── PurchaseHistory.svelte
│   │   │   │   │   └── LoyaltyPoints.svelte
│   │   │   │   ├── Promotions/
│   │   │   │   │   ├── PromoForm.svelte
│   │   │   │   │   ├── PromoCard.svelte
│   │   │   │   │   ├── ProductSelector.svelte
│   │   │   │   │   └── PromoSchedule.svelte
│   │   │   │   ├── UI/
│   │   │   │   │   ├── Sidebar.svelte
│   │   │   │   │   ├── Header.svelte
│   │   │   │   │   ├── DataTable.svelte
│   │   │   │   │   ├── SearchInput.svelte
│   │   │   │   │   ├── DateRangePicker.svelte
│   │   │   │   │   └── Badge.svelte
│   │   │   │   └── shared/
│   │   │   │       ├── Modal.svelte
│   │   │   │       ├── ConfirmDialog.svelte
│   │   │   │       └── Toast.svelte
│   │   │   ├── stores/
│   │   │   │   ├── auth.js
│   │   │   │   ├── orders.js
│   │   │   │   ├── customers.js
│   │   │   │   ├── promotions.js
│   │   │   │   └── dashboard.js
│   │   │   ├── api/
│   │   │   │   ├── index.js
│   │   │   │   ├── auth.js
│   │   │   │   ├── orders.js
│   │   │   │   ├── customers.js
│   │   │   │   ├── promotions.js
│   │   │   │   └── analytics.js
│   │   │   └── utils/
│   │   │       ├── format.js
│   │   │       ├── date.js
│   │   │       ├── currency.js
│   │   │       └── permissions.js
│   │   ├── static/
│   │   └── app.html
│   ├── package.json
│   ├── svelte.config.js
│   ├── tailwind.config.js
│   └── vite.config.js
├── backend/               # Existing Django API
│   ├── apps/
│   │   ├── customers/     # NEW: Customer management
│   │   ├── promotions/    # NEW: Promo management
│   │   ├── analytics/     # NEW: Dashboard analytics
│   │   └── audit/         # NEW: Audit logs
│   └── ...
└── docker-compose.yml
```

---

## 🔐 Authentication & Authorization

### Role-Based Access Control (RBAC)

```python
# Django Backend
class UserRole(models.TextChoices):
    SUPER_ADMIN = 'super_admin', 'Super Admin'
    OWNER = 'owner', 'Owner'
    MANAGER = 'manager', 'Manager'
    CASHIER = 'cashier', 'Cashier'
    KITCHEN = 'kitchen', 'Kitchen Staff'

class User(AbstractUser):
    role = models.CharField(max_length=20, choices=UserRole.choices)
    tenant = models.ForeignKey(Tenant, on_delete=CASCADE)
    outlet = models.ForeignKey(Outlet, on_delete=CASCADE, null=True)
```

### Permissions Matrix

| Feature | Super Admin | Owner | Manager | Cashier | Kitchen |
|---------|-------------|-------|---------|---------|---------|
| Dashboard | ✅ Full | ✅ Tenant | ✅ Outlet | ❌ | ❌ |
| Orders | ✅ All | ✅ Tenant | ✅ Outlet | ✅ Reprint | ✅ View |
| Customers | ✅ All | ✅ Tenant | ✅ Outlet | ✅ View | ❌ |
| Promotions | ✅ All | ✅ Tenant | ✅ Create | ❌ | ❌ |
| Products | ✅ All | ✅ Tenant | ✅ Edit | ❌ | ❌ |
| Reports | ✅ All | ✅ Tenant | ✅ Outlet | ❌ | ❌ |
| Users | ✅ All | ✅ Tenant | ✅ Outlet | ❌ | ❌ |
| Settings | ✅ System | ✅ Tenant | ✅ Outlet | ❌ | ❌ |

### Implementation

```javascript
// Svelte Store (admin/src/lib/stores/auth.js)
import { writable } from 'svelte/store';

export const user = writable(null);
export const permissions = writable({});

export function hasPermission(feature, action) {
    // Check if user has permission
    const perms = get(permissions);
    return perms[feature]?.[action] || false;
}
```

---

## 📊 Dashboard Components

### 1. **Revenue Card**
```svelte
<!-- admin/src/lib/components/Dashboard/RevenueCard.svelte -->
<script>
    export let title = 'Total Revenue';
    export let value = 0;
    export let change = 0; // percentage
    export let period = 'today';
</script>

<div class="card">
    <h3>{title}</h3>
    <p class="value">Rp {value.toLocaleString('id-ID')}</p>
    <span class="change {change >= 0 ? 'positive' : 'negative'}">
        {change >= 0 ? '↑' : '↓'} {Math.abs(change)}%
    </span>
</div>
```

### 2. **Sales Chart**
```svelte
<!-- admin/src/lib/components/Dashboard/SalesChart.svelte -->
<script>
    import { onMount } from 'svelte';
    import Chart from 'chart.js/auto';
    
    export let data = [];
    export let period = 'week'; // week, month, year
    
    let canvas;
    let chart;
    
    onMount(() => {
        chart = new Chart(canvas, {
            type: 'line',
            data: {
                labels: data.map(d => d.date),
                datasets: [{
                    label: 'Sales',
                    data: data.map(d => d.amount),
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            }
        });
    });
</script>

<canvas bind:this={canvas}></canvas>
```

### 3. **Top Products**
```svelte
<!-- admin/src/lib/components/Dashboard/TopProducts.svelte -->
<script>
    export let products = [];
</script>

<div class="top-products">
    <h3>Top Selling Products</h3>
    {#each products as product, i}
        <div class="product-row">
            <span class="rank">#{i + 1}</span>
            <span class="name">{product.name}</span>
            <span class="sales">{product.total_sold} sold</span>
            <span class="revenue">Rp {product.revenue.toLocaleString('id-ID')}</span>
        </div>
    {/each}
</div>
```

---

## 📦 Order Tracking Implementation

### Backend API

```python
# backend/apps/orders/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_tracking(request, order_number):
    """Get order status and timeline"""
    order = Order.objects.get(order_number=order_number)
    
    # Build timeline
    timeline = [
        {
            'status': 'received',
            'timestamp': order.created_at,
            'message': 'Order received'
        },
        {
            'status': 'preparing',
            'timestamp': order.preparing_at,
            'message': 'Kitchen is preparing'
        },
        {
            'status': 'ready',
            'timestamp': order.ready_at,
            'message': 'Order ready for pickup'
        },
        {
            'status': 'completed',
            'timestamp': order.completed_at,
            'message': 'Order completed'
        }
    ]
    
    return Response({
        'order': OrderSerializer(order).data,
        'timeline': timeline,
        'current_status': order.status,
        'estimated_time': calculate_eta(order)
    })
```

### Frontend Component

```svelte
<!-- admin/src/lib/components/Orders/OrderTimeline.svelte -->
<script>
    export let timeline = [];
    export let currentStatus = 'received';
    
    const statusColors = {
        received: 'blue',
        preparing: 'yellow',
        ready: 'green',
        completed: 'gray'
    };
</script>

<div class="timeline">
    {#each timeline as event}
        <div class="timeline-item {event.status === currentStatus ? 'active' : ''} {event.timestamp ? 'completed' : ''}">
            <div class="dot {statusColors[event.status]}"></div>
            <div class="content">
                <h4>{event.message}</h4>
                {#if event.timestamp}
                    <time>{new Date(event.timestamp).toLocaleString('id-ID')}</time>
                {:else}
                    <span class="pending">Pending...</span>
                {/if}
            </div>
        </div>
    {/each}
</div>
```

---

## 🖨️ Reprint Receipt Implementation

### Backend API

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reprint_receipt(request, order_id):
    """Generate receipt data for reprinting"""
    order = Order.objects.get(id=order_id)
    
    # Check permission
    if not request.user.has_perm('orders.reprint_receipt'):
        return Response({'error': 'Permission denied'}, status=403)
    
    # Log reprint action
    AuditLog.objects.create(
        user=request.user,
        action='reprint_receipt',
        resource='Order',
        resource_id=order_id,
        details=f'Reprinted order #{order.order_number}'
    )
    
    # Return receipt data
    return Response({
        'order': OrderSerializer(order).data,
        'items': OrderItemSerializer(order.items.all(), many=True).data,
        'payment': PaymentSerializer(order.payment).data,
        'reprint_count': order.reprint_count + 1
    })
```

### Frontend Component

```svelte
<!-- admin/src/lib/components/Orders/ReprintReceipt.svelte -->
<script>
    import { reprintReceipt } from '$lib/api/orders';
    
    export let orderId;
    
    async function handleReprint() {
        try {
            const data = await reprintReceipt(orderId);
            
            // Open print window
            const printWindow = window.open('', '_blank');
            printWindow.document.write(generateReceiptHTML(data));
            printWindow.document.close();
            printWindow.print();
        } catch (error) {
            alert('Failed to reprint receipt');
        }
    }
    
    function generateReceiptHTML(data) {
        return `
            <html>
                <head>
                    <title>Receipt #${data.order.order_number}</title>
                    <style>
                        /* Receipt styles */
                    </style>
                </head>
                <body>
                    <div class="receipt">
                        <!-- Receipt content -->
                    </div>
                </body>
            </html>
        `;
    }
</script>

<button on:click={handleReprint}>
    🖨️ Reprint Receipt
</button>
```

---

## 👥 Customer History Implementation

### Database Schema

```python
# backend/apps/customers/models.py
class Customer(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=CASCADE)
    phone = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    
    # Stats
    total_orders = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    loyalty_points = models.IntegerField(default=0)
    
    # Timestamps
    first_order_at = models.DateTimeField(null=True)
    last_order_at = models.DateTimeField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CustomerOrder(models.Model):
    """Link customers to orders"""
    customer = models.ForeignKey(Customer, on_delete=CASCADE)
    order = models.OneToOneField(Order, on_delete=CASCADE)
    points_earned = models.IntegerField(default=0)
```

### Backend API

```python
@api_view(['GET'])
def customer_history(request, customer_id):
    """Get customer purchase history"""
    customer = Customer.objects.get(id=customer_id)
    
    # Get orders
    orders = Order.objects.filter(
        customerorder__customer=customer
    ).order_by('-created_at')
    
    # Calculate stats
    stats = {
        'total_orders': customer.total_orders,
        'total_spent': customer.total_spent,
        'average_order': customer.total_spent / customer.total_orders if customer.total_orders > 0 else 0,
        'loyalty_points': customer.loyalty_points,
        'favorite_products': get_favorite_products(customer),
        'last_visit': customer.last_order_at
    }
    
    return Response({
        'customer': CustomerSerializer(customer).data,
        'stats': stats,
        'orders': OrderSerializer(orders, many=True).data
    })
```

### Frontend Component

```svelte
<!-- admin/src/routes/customers/[id]/+page.svelte -->
<script>
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { getCustomerHistory } from '$lib/api/customers';
    
    let customer = null;
    let stats = {};
    let orders = [];
    
    onMount(async () => {
        const data = await getCustomerHistory($page.params.id);
        customer = data.customer;
        stats = data.stats;
        orders = data.orders;
    });
</script>

<div class="customer-profile">
    <div class="header">
        <h1>{customer.name}</h1>
        <p>{customer.phone}</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <h3>Total Orders</h3>
            <p class="value">{stats.total_orders}</p>
        </div>
        <div class="stat-card">
            <h3>Total Spent</h3>
            <p class="value">Rp {stats.total_spent?.toLocaleString('id-ID')}</p>
        </div>
        <div class="stat-card">
            <h3>Average Order</h3>
            <p class="value">Rp {stats.average_order?.toLocaleString('id-ID')}</p>
        </div>
        <div class="stat-card">
            <h3>Loyalty Points</h3>
            <p class="value">{stats.loyalty_points} pts</p>
        </div>
    </div>
    
    <div class="order-history">
        <h2>Purchase History</h2>
        {#each orders as order}
            <div class="order-card">
                <span class="order-number">#{order.order_number}</span>
                <span class="date">{new Date(order.created_at).toLocaleDateString('id-ID')}</span>
                <span class="total">Rp {order.total_amount.toLocaleString('id-ID')}</span>
                <a href="/orders/{order.id}">View Details</a>
            </div>
        {/each}
    </div>
</div>
```

---

## 🔥 Promo Management - Best Practice

### Rekomendasi: **Hybrid Approach**

**1. Simple Promos** → **Built-in Admin UI**
- Discount percentage (10%, 20%, etc)
- Fixed discount (Rp 5,000 off)
- Product-specific promos
- Time-based promos (Happy Hour)

**2. Complex Campaigns** → **Optional CMS Integration**
- Buy X Get Y
- Bundle deals
- Tiered discounts
- Customer segment targeting

### Why Hybrid?

- ✅ **80% use cases** covered with simple UI
- ✅ **No overhead** untuk cases yang jarang
- ✅ **Flexibility** untuk growth
- ✅ **Easy to use** untuk staff

---

## 💡 Promo Management Implementation

### Database Schema

```python
# backend/apps/promotions/models.py
class Promotion(TenantModel):
    TYPE_CHOICES = [
        ('percentage', 'Percentage Discount'),
        ('fixed', 'Fixed Amount Discount'),
        ('buy_x_get_y', 'Buy X Get Y'),
        ('bundle', 'Bundle Deal'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('disabled', 'Disabled'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Discount values
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Schedule
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Conditions
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Usage limits
    usage_limit = models.IntegerField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    per_customer_limit = models.IntegerField(null=True, blank=True)
    
    # Products
    apply_to_all = models.BooleanField(default=False)
    products = models.ManyToManyField(Product, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    
    # Auto-apply
    auto_apply = models.BooleanField(default=True)
    promo_code = models.CharField(max_length=50, blank=True, unique=True)
    
    created_by = models.ForeignKey(User, on_delete=SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Admin Form Component

```svelte
<!-- admin/src/lib/components/Promotions/PromoForm.svelte -->
<script>
    import { createPromotion, updatePromotion } from '$lib/api/promotions';
    import ProductSelector from './ProductSelector.svelte';
    import DateRangePicker from '../UI/DateRangePicker.svelte';
    
    export let promo = null; // null for create, object for edit
    
    let form = {
        name: promo?.name || '',
        description: promo?.description || '',
        type: promo?.type || 'percentage',
        discount_percentage: promo?.discount_percentage || 0,
        discount_amount: promo?.discount_amount || 0,
        start_date: promo?.start_date || '',
        end_date: promo?.end_date || '',
        min_purchase: promo?.min_purchase || 0,
        max_discount: promo?.max_discount || null,
        usage_limit: promo?.usage_limit || null,
        per_customer_limit: promo?.per_customer_limit || 1,
        apply_to_all: promo?.apply_to_all || false,
        products: promo?.products || [],
        categories: promo?.categories || [],
        auto_apply: promo?.auto_apply ?? true,
        promo_code: promo?.promo_code || ''
    };
    
    async function handleSubmit() {
        try {
            if (promo) {
                await updatePromotion(promo.id, form);
            } else {
                await createPromotion(form);
            }
            alert('Promo saved successfully!');
        } catch (error) {
            alert('Failed to save promo');
        }
    }
</script>

<form on:submit|preventDefault={handleSubmit}>
    <div class="form-group">
        <label>Promo Name *</label>
        <input type="text" bind:value={form.name} required />
    </div>
    
    <div class="form-group">
        <label>Description</label>
        <textarea bind:value={form.description}></textarea>
    </div>
    
    <div class="form-group">
        <label>Promo Type *</label>
        <select bind:value={form.type}>
            <option value="percentage">Percentage Discount</option>
            <option value="fixed">Fixed Amount Discount</option>
            <option value="buy_x_get_y">Buy X Get Y</option>
            <option value="bundle">Bundle Deal</option>
        </select>
    </div>
    
    {#if form.type === 'percentage'}
        <div class="form-group">
            <label>Discount Percentage *</label>
            <input type="number" bind:value={form.discount_percentage} min="0" max="100" required />
            <span>%</span>
        </div>
        
        <div class="form-group">
            <label>Max Discount Amount</label>
            <input type="number" bind:value={form.max_discount} min="0" />
            <small>Optional: Cap maximum discount (e.g., max Rp 50,000)</small>
        </div>
    {:else if form.type === 'fixed'}
        <div class="form-group">
            <label>Discount Amount *</label>
            <input type="number" bind:value={form.discount_amount} min="0" required />
            <span>Rupiah</span>
        </div>
    {/if}
    
    <div class="form-group">
        <label>Schedule *</label>
        <DateRangePicker 
            bind:startDate={form.start_date} 
            bind:endDate={form.end_date}
        />
    </div>
    
    <div class="form-group">
        <label>Minimum Purchase</label>
        <input type="number" bind:value={form.min_purchase} min="0" />
        <small>Minimum order amount to qualify for promo</small>
    </div>
    
    <div class="form-group">
        <label>Usage Limits</label>
        <div class="flex gap-4">
            <input 
                type="number" 
                bind:value={form.usage_limit} 
                placeholder="Total usage limit"
            />
            <input 
                type="number" 
                bind:value={form.per_customer_limit} 
                placeholder="Per customer limit"
            />
        </div>
    </div>
    
    <div class="form-group">
        <label>
            <input type="checkbox" bind:checked={form.apply_to_all} />
            Apply to all products
        </label>
    </div>
    
    {#if !form.apply_to_all}
        <div class="form-group">
            <label>Select Products</label>
            <ProductSelector bind:selected={form.products} />
        </div>
    {/if}
    
    <div class="form-group">
        <label>
            <input type="checkbox" bind:checked={form.auto_apply} />
            Auto-apply (no promo code needed)
        </label>
    </div>
    
    {#if !form.auto_apply}
        <div class="form-group">
            <label>Promo Code</label>
            <input type="text" bind:value={form.promo_code} />
        </div>
    {/if}
    
    <div class="form-actions">
        <button type="submit" class="btn-primary">
            {promo ? 'Update' : 'Create'} Promotion
        </button>
    </div>
</form>
```

---

## 📊 Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Setup admin SvelteKit app
- [ ] Authentication & authorization
- [ ] Basic layout with sidebar
- [ ] User management

### Phase 2: Dashboard (Week 2-3)
- [ ] Sales metrics cards
- [ ] Revenue charts
- [ ] Top products widget
- [ ] Recent orders list
- [ ] Real-time WebSocket

### Phase 3: Order Management (Week 3-4)
- [ ] Order list with filters
- [ ] Order detail view
- [ ] Order tracking timeline
- [ ] Reprint receipt functionality
- [ ] Order search

### Phase 4: Customer Management (Week 4-5)
- [ ] Customer database
- [ ] Customer list & search
- [ ] Customer profile page
- [ ] Purchase history
- [ ] Loyalty points (optional)

### Phase 5: Promo Management (Week 5-6)
- [ ] Promotion CRUD
- [ ] Product selector
- [ ] Schedule picker
- [ ] Promo list & status
- [ ] Apply promo logic to orders

### Phase 6: Reports & Analytics (Week 6-7)
- [ ] Sales reports
- [ ] Product performance
- [ ] Customer analytics
- [ ] Export to Excel/PDF

---

## 🎯 Next Steps

Saya akan mulai implementasi:

1. **Setup admin SvelteKit app** dengan structure
2. **Create authentication system**
3. **Build dashboard components**
4. **Implement order tracking**
5. **Add customer history**
6. **Create promo management**

**Apakah Anda setuju dengan arsitektur ini? Ada yang ingin diubah atau ditambahkan?** 🚀
