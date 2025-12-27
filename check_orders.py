"""
Kitchen Display - Database Check Script
Checks orders in database for debugging
"""

from apps.orders.models import Order
from apps.tenants.models import Tenant

print("\n=== ALL ORDERS ===")
orders = Order.objects.all()
print(f"Total orders: {orders.count()}")

for order in orders:
    print(f"\nOrder: {order.order_number}")
    print(f"  Tenant ID: {order.tenant_id}")
    print(f"  Tenant Name: {order.tenant.name if order.tenant else 'N/A'}")
    print(f"  Status: {order.status}")
    print(f"  Payment Status: {order.payment_status}")
    print(f"  Items: {order.items.count()}")
    print(f"  Created: {order.created_at}")

print("\n=== ORDERS BY STATUS ===")
for status_code, status_name in Order.STATUS_CHOICES:
    count = Order.objects.filter(status=status_code).count()
    print(f"{status_name}: {count}")

print("\n=== ORDERS BY TENANT ===")
tenants = Tenant.objects.all()
for tenant in tenants:
    count = Order.objects.filter(tenant_id=tenant.id).count()
    print(f"Tenant {tenant.id} ({tenant.name}): {count} orders")

print("\n=== KITCHEN DISPLAY FILTER ===")
print("Filters: status__in=['confirmed', 'preparing', 'ready']")
for tenant in tenants:
    kitchen_orders = Order.objects.filter(
        tenant_id=tenant.id,
        status__in=['confirmed', 'preparing', 'ready']
    ).count()
    print(f"Tenant {tenant.id} ({tenant.name}): {kitchen_orders} orders")

print()
