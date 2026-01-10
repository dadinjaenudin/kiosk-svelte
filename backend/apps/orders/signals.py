"""
Django signals for Order model
Emit Socket.IO events to Local Sync Server for real-time updates
"""
import logging
import requests
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Order

logger = logging.getLogger(__name__)

# Local Sync Server URL
SYNC_SERVER_URL = 'http://host.docker.internal:3001'  # From Docker to host machine


def emit_socket_event(event_name, data):
    """
    Emit socket event to Local Sync Server via HTTP API
    """
    try:
        url = f"{SYNC_SERVER_URL}/emit"
        payload = {
            'event': event_name,
            'data': data
        }
        response = requests.post(url, json=payload, timeout=2)
        
        if response.status_code == 200:
            logger.info(f"✅ Socket event '{event_name}' emitted for order {data.get('order_number')}")
        else:
            logger.warning(f"⚠️ Failed to emit socket event: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Socket event emission error: {e}")
        # Don't fail the request if socket emission fails


@receiver(post_save, sender=Order)
def order_created_handler(sender, instance, created, **kwargs):
    """
    Emit 'new_order' event when order is created
    """
    if created and instance.status in ['pending', 'confirmed']:
        # Serialize order data
        order_data = {
            'id': instance.id,
            'order_number': instance.order_number,
            'outlet_id': instance.outlet_id,
            'outlet_name': instance.outlet.name if instance.outlet else '',
            'tenant_id': instance.tenant_id,
            'status': instance.status,
            'total_amount': float(instance.total_amount),
            'customer_name': instance.customer_name,
            'table_number': instance.table_number,
            'notes': instance.notes,
            'created_at': instance.created_at.isoformat() if instance.created_at else None,
            'items': []
        }
        
        # Add order items
        for item in instance.items.all():
            order_data['items'].append({
                'product_name': item.product_name,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'total_price': float(item.total_price),
                'modifiers': item.modifiers,
                'notes': item.notes,
                'kitchen_station_code': item.kitchen_station_code
            })
        
        # Emit socket event
        emit_socket_event('new_order', order_data)
        logger.info(f"🔔 New order signal: {instance.order_number}")


@receiver(pre_save, sender=Order)
def order_status_changed_handler(sender, instance, **kwargs):
    """
    Emit 'order_updated' event when order status changes
    """
    if instance.pk:  # Only for existing orders
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            
            # Check if status changed
            if old_instance.status != instance.status:
                order_data = {
                    'id': instance.id,
                    'order_number': instance.order_number,
                    'outlet_id': instance.outlet_id,
                    'old_status': old_instance.status,
                    'status': instance.status,
                    'updated_at': instance.updated_at.isoformat() if instance.updated_at else None
                }
                
                # Emit socket event
                emit_socket_event('order_updated', order_data)
                logger.info(f"🔄 Order status changed: {instance.order_number} ({old_instance.status} → {instance.status})")
                
        except Order.DoesNotExist:
            pass
