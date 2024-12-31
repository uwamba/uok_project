# chat/views.py
from django.shortcuts import render, get_object_or_404
from .models import Room

def room_list(request):
    rooms = Room.objects.all()
    return render(request, 'chat_list.html', {'rooms': rooms})

def video_chat(request, room_name):
    room = get_object_or_404(Room, name=room_name)
    return render(request, 'video_chat.html', {'room_name': room.name})
