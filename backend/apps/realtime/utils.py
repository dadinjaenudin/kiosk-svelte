"""
Utility functions to broadcast events via Django Channels
"""
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def broadcast_new_order(order_data):
    """
    Broadcast new order event to outlet channel
    
    Args:
        order_data: Dict containing order information including outlet_id
    """
    channel_layer = get_channel_layer()
    outlet_id = order_data.get('outlet_id')
    
    if not outlet_id:
        print('[Channels] Warning: No outlet_id in order data, cannot broadcast')
        return
    
    group_name = f'outlet_{outlet_id}'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'new_order',
            'data': order_data
        }
    )
    
    print(f'[Channels] Broadcasted new_order to {group_name}')


def broadcast_order_updated(order_data):
    """
    Broadcast order updated event to outlet channel
    """
    channel_layer = get_channel_layer()
    outlet_id = order_data.get('outlet_id')
    
    if not outlet_id:
        print('[Channels] Warning: No outlet_id in order data, cannot broadcast')
        return
    
    group_name = f'outlet_{outlet_id}'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'order_updated',
            'data': order_data
        }
    )
    
    print(f'[Channels] Broadcasted order_updated to {group_name}')


def broadcast_order_completed(order_data):
    """
    Broadcast order completed event to outlet channel
    """
    channel_layer = get_channel_layer()
    outlet_id = order_data.get('outlet_id')
    
    if not outlet_id:
        return
    
    group_name = f'outlet_{outlet_id}'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'order_completed',
            'data': order_data
        }
    )
    
    print(f'[Channels] Broadcasted order_completed to {group_name}')


def broadcast_order_cancelled(order_data):
    """
    Broadcast order cancelled event to outlet channel
    """
    channel_layer = get_channel_layer()
    outlet_id = order_data.get('outlet_id')
    
    if not outlet_id:
        return
    
    group_name = f'outlet_{outlet_id}'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'order_cancelled',
            'data': order_data
        }
    )
    
    print(f'[Channels] Broadcasted order_cancelled to {group_name}')


def broadcast_kitchen_status(kitchen_data):
    """
    Broadcast kitchen status change to outlet channel
    """
    channel_layer = get_channel_layer()
    outlet_id = kitchen_data.get('outlet_id')
    
    if not outlet_id:
        return
    
    group_name = f'outlet_{outlet_id}'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'kitchen_status_changed',
            'data': kitchen_data
        }
    )
    
    print(f'[Channels] Broadcasted kitchen_status_changed to {group_name}')
