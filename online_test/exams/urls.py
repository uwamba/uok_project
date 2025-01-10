from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('test/<int:test_id>/<int:result_id>/', views.test_detail, name='test_detail'),
    path('api/tests/', views.CandidateTestListView.as_view(), name='candidate-test-list'),
    path('create-test/', views.create_test, name='create_test'),
    path('create-question/', views.create_question, name='create_question'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
