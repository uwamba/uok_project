from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.candidate_register, name='register'),
    path('login/', views.candidate_login, name='login'),
    path('logout/', views.candidate_logout, name='logout'),
    path('dashboard/', views.candidate_dashboard, name='dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('test/<int:test_id>/', views.take_test, name='test'),
    path('monitor/<int:test_id>/', views.test_monitor, name='monitor'),
    path('result/<int:result_id>/', views.view_result, name='result'),
    path('login_api/', views.LoginView.as_view(), name='login_api'),


]
