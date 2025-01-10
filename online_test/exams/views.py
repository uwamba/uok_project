import threading
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .serializers import TestSerializer
from results.models import Result, ResultDetail
from videos.models import MonitoringLog
from videos.utils import capture_screen, monitor_webcam
from .models import Question, QuestionOption, Test
from rest_framework import generics, permissions

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import TestForm
from .forms import QuestionForm, QuestionOptionFormSet

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

def create_test(request):
    if request.method == 'POST':
        form = TestForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()  # Save the new test to the database
            return redirect('admin_dashboard')  # Redirect to a list or confirmation page after saving
    else:
        print('request user', request.user.id)  
        form = TestForm(user=request.user.id)  # Pass the logged-in user to the form

    return render(request, 'create_test.html', {'form': form})
from .forms import QuestionForm

def create_question(request):
    if request.method == 'POST':
        question_form = QuestionForm(request.POST, request.FILES)
        option_formset = QuestionOptionFormSet(request.POST)
        if question_form.is_valid() and option_formset.is_valid():
            question = question_form.save()
            option_formset.instance = question
            option_formset.save()
            return redirect('success_page')  # Replace with your success URL
    else:
        question_form = QuestionForm()
        option_formset = QuestionOptionFormSet()

    return render(request, 'create_question.html', {
        'question_form': question_form,
        'option_formset': option_formset
    })