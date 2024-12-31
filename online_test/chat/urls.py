# chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('rooms/', views.room_list, name='room_list'),
    path('video_chat/<str:room_name>/', views.video_chat, name='video_chat'),
]
