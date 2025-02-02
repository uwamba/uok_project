from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.candidate_register, name='register'),
    path('login/', views.candidate_login, name='login'),
    path('logout/', views.candidate_logout, name='logout'),
    path('dashboard/', views.candidate_dashboard, name='dashboard'),
    path('result_list/', views.result_list, name='result_list'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_test_result/', views.admin_test_result, name='admin_test_result'),
    path('test_report/<int:test_id>/', views.test_report, name='test_report'),
    path('candidate_log_report/<int:candidate_id>/', views.candidate_log_report, name='candidate_log_report'), 
    path('test/<int:test_id>/', views.take_test, name='test'),
    path('monitor/<int:test_id>/', views.test_monitor, name='monitor'),
    path('result/<int:result_id>/', views.view_result, name='result'),
    path('login_api/', views.LoginView.as_view(), name='login_api'),
    path('export/results/', views.export_results_to_excel, name='export_results_to_excel'),
    path('export/log_report/pdf/<int:candidate_id>/', views.export_log_report_to_pdf, name='export_log_report_to_pdf'),


]
