from django.urls import path
from . import views

urlpatterns = [
    path('create_company/', views.create_company, name='create_company'),
    # Add other paths for listing or managing companies
]
