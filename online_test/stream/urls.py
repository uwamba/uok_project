# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('camera_test/', views.camera_test, name='camera_test'),
    path('admin_video/', views.admin_video_view, name='admin_video_view'),
    path('offer/', views.offer, name='offer'),
    path('admin_offer/', views.admin_offer, name='admin_offer'),
    path('answer/', views.answer, name='answer'),
]
