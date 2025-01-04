import threading
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .serializers import TestSerializer
from results.models import Result, ResultDetail
from videos.models import MonitoringLog
from videos.utils import capture_screen, monitor_webcam
from .models import Question, QuestionOption, Test
from rest_framework import generics, permissions

def test_detail(request, test_id,result_id):
    test = get_object_or_404(Test, id=test_id)
    results= Result.objects.get(id=result_id)
    #results_answer=results.details.all()
    # For a list of values of a specific field (e.g., 'selected_option_id')
    results_answers = ResultDetail.objects.filter(result_id=result_id)
    results_answer = ResultDetail.objects.filter(result_id=result_id).values('selected_option_id')
    selected_option_ids = [item['selected_option_id'] for item in results_answer if item['selected_option_id'] is not None]

    print(results_answers.values('question_id','answer_text'))
    questions = test.questions.all()
    
    context = {
        'test': test,
        'questions': questions,
        'results_answer':results_answer,
        'results_answers':results_answers,
        'selected_option_ids': selected_option_ids,
    }
    return render(request, 'test_details.html', context)

class CandidateTestListView(generics.ListAPIView):
    serializer_class = TestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Get the candidate linked to the authenticated user
        user = self.request.user
        candidate = getattr(user, 'candidate', None)
        if candidate:
            return Test.objects.filter(candidates=candidate)
        return Test.objects.none()

