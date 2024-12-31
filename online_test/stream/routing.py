# routing.py
from django.urls import path
from .consumers import VideoCallConsumer

websocket_urlpatterns = [
    path('ws/call/<str:room_name>/', VideoCallConsumer.as_asgi()),
]
