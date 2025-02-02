from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('test/<int:test_id>/<int:result_id>/', views.test_detail, name='test_detail'),
    path('create-test/', views.create_test, name='create_test'),
    path('create-question/', views.create_question, name='create_question'),
    path('add_test/', views.add_test, name='add_test'),
    path('create_subject/', views.create_subject, name='create_subject'),
    path('register_candidate/', views.register_candidate, name='register_candidate'),
    path('candidates/', views.list_candidates, name='list_candidates'),
    path('candidate/<int:candidate_id>/detail/', views.candidate_detail, name='candidate_detail'),
    path('candidate/<int:candidate_id>/edit/', views.candidate_edit, name='candidate_edit'),
    path('import/', views.import_questions, name='import_questions'),
    path('export/', views.export_questions, name='export_questions'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

