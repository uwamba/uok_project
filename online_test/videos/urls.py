from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('upload/', views.upload_chunk, name='upload_chunk'),
    path('stream/', views.stream_video, name='stream_video'),
    #path('', views.video_record_page, name='video_record_page'),  # Frontend page
    path('video-size/', views.get_video_size, name='get_video_size'),
    path('view_video/', views.view_video, name='view_video'),
    path('upload_video/', views.upload_video, name='upload_video'),
    path('view_screen/', views.view_screen, name='view_screen'),
    path('start_monitoring/<int:exam_id>/', views.start_monitoring, name='start_monitoring'),
    path('view_logs/<int:exam_id>/', views.view_logs, name='view_logs'),
    path('create_session/', views.create_session, name='create_session'),
    path('generate_token/<str:session_id>/', views.generate_token, name='generate_token'),
    path('video_conf/', views.video_conf, name='video_conf'),
    path('testing/', views.testing, name='testing'),
    path('', TemplateView.as_view(template_name='index.html')),


]