
from pyexpat.errors import messages
from .serializers import TestSerializer
from django.shortcuts import render, redirect
from .forms import TestForm
from .forms import QuestionForm, QuestionOptionFormSet
from django.shortcuts import render, redirect, get_object_or_404
from .models import Subject, Test, Question, QuestionOption
from results.models import Result, ResultDetail
from users.models import Admin
from .forms import TestForm, QuestionFormSet, QuestionOptionFormSet
from datetime import timedelta, datetime
from .forms import TestForm
from dal import autocomplete
from .models import Candidate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CandidateForm, UserRegistrationForm

from django.contrib.auth import get_user_model
from .models import Candidate, Company


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


def add_test(request):
    if request.method == 'POST':
        # Save Test
        duration_minutes = int(request.POST.get('duration'))
       # admin = Admin.objects.get(user=request.user)  # Get the Admin object linked to the logged-in user
    
        # Get the company related to the logged-in admin
        #company = admin.company
        test = Test.objects.create(
            title=request.POST.get('test_title'),
            subject_id=request.POST.get('subject'),
            start_time = datetime.strptime(request.POST.get('start_time'), '%Y-%m-%dT%H:%M'),
            end_time = datetime.strptime(request.POST.get('end_time'), '%Y-%m-%dT%H:%M'),

            total_marks=request.POST.get('total_marks'),
            max_attempts=request.POST.get('max_attempts'),
            duration = timedelta(minutes=duration_minutes),
            created_by=request.user
        )

        # Save Questions and Options
        questions = request.POST.getlist('question_text')
        for i, question_text in enumerate(questions):
            question = Question.objects.create(
                test=test,
                text=question_text,
                marks=request.POST.getlist('question_marks')[i],
                question_type=request.POST.getlist('question_type')[i],
                answer_text=request.POST.get(f'answer_text_{i}', None)  # Handle text answers
            )

            # Save Options if the question is not a text question
            if question.question_type != 'text':
                options = request.POST.getlist(f'option_text_{i}')
                correct_options = request.POST.getlist(f'is_correct_{i}')
                for j, option_text in enumerate(options):
                    QuestionOption.objects.create(
                        question=question,
                        text=option_text,
                        is_correct=(str(j) in correct_options)
         
                    )

        selected_candidates = request.POST.getlist('candidates')  # Get the list of selected candidate IDs
        for candidate_id in selected_candidates:
            candidate = Candidate.objects.get(id=candidate_id)
            test.candidates.add(candidate)  # Associate the candidate with the test
        return redirect('admin_dashboard')
    form = TestForm()
    candidates = Candidate.objects.all() 
    return render(request, 'add_test.html', {'subjects': Subject.objects.filter(company=request.user.admin.company),'form': form,'candidates': candidates})



class CandidateAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Optionally filter candidates based on the search query
        qs = Candidate.objects.all()
        if self.q:
            qs = qs.filter(full_name__icontains=self.q)  # Search by full name
        return qs
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
    
from .forms import SubjectForm

def create_subject(request):
    # Get the company associated with the logged-in admin
    company = request.user.admin.company  # Assuming the admin has a related 'Company' via the 'Admin' model

    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            # Set the company automatically to the logged-in admin's company
            subject = form.save(commit=False)
            subject.company = company  # Assign the company
            subject.save()

            #messages.success(request, "Subject created successfully!")
            return redirect('admin_dashboard')  # Redirect to the subject list page
    else:
        form = SubjectForm()

    return render(request, 'create_subject.html', {'form': form})



@login_required
def register_candidate(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        date_of_birth = request.POST.get('date_of_birth')
        phone_number = request.POST.get('phone_number')

        # Create a new user using the custom user model
        User = get_user_model()
        user = User.objects.create_user(username=username, password=password)

        # Set user's full name and other information
        user.first_name = full_name
        user.save()

        # Get the company of the logged-in admin
        company = request.user.admin.company 
        
        # Create a new candidate
        Candidate.objects.create(
            user=user,
            company=company,
            date_of_birth=date_of_birth,
            phone_number=phone_number
        )

        return redirect('admin_dashboard')  # Redirect to a success page or any other page

    return render(request, 'register_candidate.html')
@login_required
def list_candidates(request):
    # Get the company of the logged-in admin
    company = request.user.admin.company  # Assuming logged-in admin has a Company linked to them
    
    # Fetch all candidates associated with that company
    candidates = Candidate.objects.filter(company=company)
    
    # Pass the list of candidates to the template
    return render(request, 'list_candidates.html', {'candidates': candidates})
@login_required
def candidate_detail(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    return render(request, 'candidate_detail.html', {'candidate': candidate})
@login_required
def candidate_edit(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)

    if request.method == 'POST':
        form = CandidateForm(request.POST, instance=candidate)
        if form.is_valid():
            form.save()
            return redirect('candidate_detail', candidate_id=candidate.id)  # Redirect to the candidate detail page
    else:
        form = CandidateForm(instance=candidate)

    return render(request, 'candidate_edit.html', {'form': form, 'candidate': candidate})
