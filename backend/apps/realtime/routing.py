"""
WebSocket URL Routing for Django Channels
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/outlet/(?P<outlet_id>\w+)/$', consumers.OrderConsumer.as_asgi()),
]
