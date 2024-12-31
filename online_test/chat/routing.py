from django.urls import path
from .consumers import VideoChatConsumer

websocket_urlpatterns = [
    path('ws/video_chat/', VideoChatConsumer.as_asgi()),
]