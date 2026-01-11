"""
Django Channels Consumers for Real-time Updates
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class OrderConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time order updates
    Clients subscribe to outlet-specific channels
    """

    async def connect(self):
        """
        Called when WebSocket connection is established
        """
        # Get outlet_id from URL route
        self.outlet_id = self.scope['url_route']['kwargs'].get('outlet_id')
        
        if not self.outlet_id:
            await self.close(code=4000)
            return

        # Create room group name
        self.room_group_name = f'outlet_{self.outlet_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send confirmation message
        await self.send(text_data=json.dumps({
            'type': 'connection.established',
            'message': f'Connected to outlet {self.outlet_id} real-time channel',
            'outlet_id': self.outlet_id
        }))

        print(f'[Channels] Client connected to outlet {self.outlet_id} (channel: {self.channel_name})')

    async def disconnect(self, close_code):
        """
        Called when WebSocket connection is closed
        """
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print(f'[Channels] Client disconnected from outlet {self.outlet_id} (code: {close_code})')

    async def receive(self, text_data):
        """
        Receive message from WebSocket
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'ping':
                # Respond to ping
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))

            elif message_type == 'subscribe':
                # Client wants to subscribe (already done in connect)
                await self.send(text_data=json.dumps({
                    'type': 'subscribed',
                    'outlet_id': self.outlet_id,
                    'room': self.room_group_name
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    # Receive message from room group (broadcasted events)
    async def new_order(self, event):
        """
        Called when new order is created
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_order',
            'data': event['data']
        }))

    async def order_updated(self, event):
        """
        Called when order is updated
        """
        await self.send(text_data=json.dumps({
            'type': 'order_updated',
            'data': event['data']
        }))

    async def order_completed(self, event):
        """
        Called when order is completed
        """
        await self.send(text_data=json.dumps({
            'type': 'order_completed',
            'data': event['data']
        }))

    async def order_cancelled(self, event):
        """
        Called when order is cancelled
        """
        await self.send(text_data=json.dumps({
            'type': 'order_cancelled',
            'data': event['data']
        }))

    async def kitchen_status_changed(self, event):
        """
        Called when kitchen status changes
        """
        await self.send(text_data=json.dumps({
            'type': 'kitchen_status_changed',
            'data': event['data']
        }))
