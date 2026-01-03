"""
Fix pending orders - Update status to confirmed
Run this to fix orders stuck in pending status
"""

from apps.orders.models import Order
from apps.payments.models import Payment

print("\n=== FIXING PENDING ORDERS ===\n")

# Get all pending orders
pending_orders = Order.objects.filter(status='pending', payment_status='unpaid')

print(f"Found {pending_orders.count()} pending orders")

if pending_orders.count() == 0:
    print("No pending orders to fix!")
else:
    for order in pending_orders:
        print(f"\nFixing Order: {order.order_number}")
        print(f"  Tenant: {order.tenant.name if order.tenant else 'N/A'}")
        print(f"  Items: {order.items.count()}")
        print(f"  Total: Rp {order.total_amount:,.0f}")
        
        # Update order status
        order.status = 'confirmed'
        order.payment_status = 'paid'
        order.save()
        
        # Update payment status if exists
        payments = Payment.objects.filter(order=order)
        for payment in payments:
            payment.status = 'success'
            payment.save()
            print(f"  Payment {payment.transaction_id}: UPDATED to success")
        
        print(f"  Order status: {order.status} ✓")
        print(f"  Payment status: {order.payment_status} ✓")

print(f"\n=== FIXED {pending_orders.count()} ORDERS ===\n")

# Verify
confirmed_orders = Order.objects.filter(status__in=['confirmed', 'preparing', 'ready'])
print(f"Total orders in Kitchen Display filter: {confirmed_orders.count()}")

for order in confirmed_orders:
    print(f"  {order.order_number} - {order.tenant.name} - {order.status}")

print()
