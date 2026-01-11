"""
Integration example: Broadcasting order events via Django Channels

Add this code to your order creation/update logic:

# In apps/orders/views_order_group.py or wherever orders are created

from apps.realtime.utils import (
    broadcast_new_order, 
    broadcast_order_updated,
    broadcast_order_completed,
    broadcast_order_cancelled
)

# Example: After creating order
def create(self, request, *args, **kwargs):
    response = super().create(request, *args, **kwargs)
    
    # Broadcast to Django Channels (WebSocket)
    order_data = {
        'id': response.data['id'],
        'order_number': response.data['order_number'],
        'outlet_id': response.data['outlet_id'],
        'status': response.data['status'],
        'total_amount': str(response.data['total_amount']),
        'created_at': response.data['created_at'],
        # ... other fields
    }
    broadcast_new_order(order_data)
    
    return response

# Example: After updating order status
@action(detail=True, methods=['patch'])
def update_status(self, request, pk=None):
    order = self.get_object()
    new_status = request.data.get('status')
    
    order.status = new_status
    order.save()
    
    # Broadcast update
    order_data = {
        'id': order.id,
        'order_number': order.order_number,
        'outlet_id': order.outlet_id,
        'status': order.status,
        'updated_at': order.updated_at.isoformat()
    }
    
    if new_status == 'completed':
        broadcast_order_completed(order_data)
    elif new_status == 'cancelled':
        broadcast_order_cancelled(order_data)
    else:
        broadcast_order_updated(order_data)
    
    return Response({'status': 'updated'})
"""
