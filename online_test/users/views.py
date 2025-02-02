from django.utils import timezone
import spacy
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from exams.models import Subject, Test,Question,QuestionOption
from results.models import Result,ResultDetail
from users.models import Candidate
from videos.models import MonitoringLog
from django.db.models import Sum, Count
from nltk.corpus import wordnet as wn
from spacy.matcher import PhraseMatcher
import spacy
from nltk.corpus import wordnet as wn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.contrib import messages
from .models import Admin, Candidate
import threading
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from scipy.spatial.transform import Rotation as R
from exams.models import Test
from videos.utils import capture_screen, monitor_webcam
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken  # For JWT
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db.models import F
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from import_export import resources


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
# Create your views here.
# Candidate registration
def candidate_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        full_name = request.POST['full_name']
        candidate = Candidate.objects.create_user(username=username, password=password, full_name=full_name)
        return redirect('candidate_login')
    return render(request, 'register.html')



class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Login successful",
                    "access_token": str(refresh.access_token),  # Access token for frontend use
                    "refresh_token": str(refresh),  # Refresh token
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    }
                }, status=status.HTTP_200_OK)

            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def candidate_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:

            # Check user role and redirect accordingly
            if user.is_admin:
                print('admin logging')
                try:
                    admin = Admin.objects.get(user=user)
                    
                    # If everything is okay, log the user in
                    login(request, user)
                    return redirect('admin_dashboard')

                except admin.DoesNotExist:
                    messages.error(request, "Candidate profile not found.")
                    return render(request, 'login.html')
            elif user.is_candidate:
                print('candidate logging')
                try:
                    candidate = Candidate.objects.get(user=user)
                    current_time = now()
                    
                    # Check if the candidate's access is within the allowed time window
                    if candidate.access_start_time and current_time < candidate.access_start_time:
                        messages.error(request, "You are not allowed to access the system yet.")
                        return render(request, 'login.html')
                    
                    if candidate.access_end_time and current_time > candidate.access_end_time:
                        messages.error(request, "Your access time has expired.")
                        return render(request, 'login.html')

                    # If everything is okay, log the user in
                    login(request, user)
                    return redirect('dashboard')

                except Candidate.DoesNotExist:
                    messages.error(request, "Candidate profile not found.")
                    return render(request, 'login.html')
            else:
                messages.error(request, "Invalid user role.")
                return redirect('login')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'login.html')


@login_required
def candidate_logout(request):
    logout(request)
    return redirect('login')

# Dashboard to view tests
@login_required
def candidate_dashboard(request):

    candidate = Candidate.objects.get(user=request.user.id)
    tests = candidate.tests.all().order_by('-id')
    results = Result.objects.filter(candidate=request.user.candidate).select_related('test')
    attempt_count = results.count()
    
            
    return render(request, 'dashboard.html', {'tests': tests,'results':results,'now': timezone.now(), 'attempt_count': attempt_count,})
@login_required
def result_list(request):

    candidate = Candidate.objects.get(user=request.user.id)
    tests = candidate.tests.all()
    results = Result.objects.filter(candidate=request.user.candidate).select_related('test')
    return render(request, 'result_list.html', {'tests': tests,'results':results})
@login_required
def admin_dashboard(request):

    admin = Admin.objects.get(user=request.user)
    
    search_query = request.GET.get('search', '')
    
    tests = Test.objects.filter(subject__company=admin.company,title__icontains=search_query).order_by('-id')
    current_time = timezone.now()
    for test in tests:
        # Add a custom attribute to each test indicating if the monitoring button should be shown
        test.show_monitor_button = test.end_time > current_time
    
    return render(request, 'admin_dashboard.html', {'tests': tests})
@login_required
def admin_test_result(request):

    admin = Admin.objects.get(user=request.user)

    results = Result.objects.filter(candidate__company=admin.company)

    return render(request, 'admin_result.html', {'results':results})



@login_required
def test_report(request,test_id):

    admin = Admin.objects.get(user=request.user)

    # Fetch the test instance based on the test_id and the admin's company
    test = Test.objects.get(id=test_id, candidates__company=admin.company)

    # Fetch results for the test, filtering by company and test_id
    results = Result.objects.filter(test=test).order_by('-total_marks')

    # Fetch monitoring logs for the test, grouped by candidate, and count the logs for each candidate
    logs_count = MonitoringLog.objects.filter(test=test).values('candidate', 'candidate__full_name')\
        .annotate(log_count=Count('id')).order_by('-log_count')

    # Combine the results and logs into a list of dictionaries
    combined_data = []

    for result in results:
        log_data = next((log for log in logs_count if log['candidate'] == result.candidate.id), None)
        combined_data.append({
            'candidate': result.candidate,
            'total_marks': result.total_marks,
            'log_count': log_data['log_count'] if log_data else 0,  # Default to 0 if no log data
        })

    # Prepare context with combined data
    context = {
        'test': test,
        'combined_data': combined_data,
    }
    
    return render(request, 'test_report.html', context)


def candidate_log_report(request, candidate_id):
    # Fetch the candidate by ID
    candidate = Candidate.objects.get(id=candidate_id)

    # Fetch all logs for the candidate
    logs = MonitoringLog.objects.filter(candidate=candidate).order_by('-timestamp')

    # Prepare the context to pass to the template
    context = {
        'candidate': candidate,
        'logs': logs,
    }

    return render(request, 'candidate_log_report.html', context)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt  # For simplicity, use @csrf_exempt while testing; use proper CSRF handling in production
def take_test_api(request, test_id):
   
    
    test = Test.objects.get(id=test_id)
    questions = test.questions.all().order_by('?')
    candidate = Candidate.objects.get(user=request.user)
    now = timezone.now()
    remaining_time = (test.end_time - now).total_seconds() if test.end_time else 0
    
    # Monitoring logic
    user = request.user
    exam = Test.objects.get(id=test_id)
    screen_thread = threading.Thread(target=capture_screen, args=(user, exam))
    webcam_thread = threading.Thread(target=monitor_webcam, args=(user, exam))
    #screen_thread.start()
    #webcam_thread.start()

    # For GET request, return test data and remaining time
    if request.method == 'GET':
        return JsonResponse({
            'test': {
                'id': test.id,
                'name': test.title,
                'description': test.title,
                'questions': [{
                    'id': q.id,
                    'text': q.text,
                    'question_type': q.question_type,
                    'max_selection':q.max_selection,
                    'options': [{
                        'id': o.id,
                        'text': o.text
                    } for o in q.options.all()]
                } for q in questions]
            },
            'remaining_time': max(0, int(remaining_time))
        })

    # For POST request, calculate and save score
    elif request.method == 'POST':
        score = 0
        result = Result.objects.create(candidate=candidate, test=test, total_marks=score)
        answers_data = request.data.get('answers', [])
        print(answers_data)
        score = 0
        result = Result.objects.create(candidate=candidate, test=test, total_marks=score)
        answers_data = request.data.get('answers', [])

        for question in questions:
            selected_option_ids = [
                item['answer'] for item in answers_data if item['question_id'] == question.id
            ]
            selected_option_ids = selected_option_ids[0] if selected_option_ids else []

            if question.question_type == 'multiple':
                correct_option_count = QuestionOption.objects.filter(
                    question_id=question.id, is_correct=True
                ).count()
                for option_id in selected_option_ids:
                    selected_option = QuestionOption.objects.get(id=option_id)
                    ResultDetail.objects.create(
                        result=result, question=question, selected_option=selected_option
                    )
                    if selected_option.is_correct:
                        score += question.marks / correct_option_count

            elif question.question_type == 'single':
                if selected_option_ids:
                    selected_option = QuestionOption.objects.get(id=selected_option_ids[0])
                    ResultDetail.objects.create(
                        result=result, question=question, selected_option=selected_option
                    )
                    if selected_option.is_correct:
                        score += question.marks

            elif question.question_type == 'text':
                answer_text=""
                if selected_option_ids:
                 answer_text = selected_option_ids[0]
                answer = mark_text_question(answer_text, question.answer_text)
                
                ResultDetail.objects.create(
                    result=result, question=question, selected_option=None, answer_text=answer_text
                )
                score += question.marks * answer["percentage_score"] / 100

        result.total_marks = score
        result.save()


        return JsonResponse({'result_id': result.id})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def take_test(request, test_id):
    test = Test.objects.get(id=test_id)
    questions = test.questions.all().order_by('?')

    # Ensure the user has an associated Candidate instance
    candidate = Candidate.objects.get(user=request.user)
    now = timezone.now()  # Use Django's timezone.now()
    print('time now',now)
    remaining_time = (test.end_time - now).total_seconds() if test.end_time else 0
    
    print('test time',test.end_time)
    print('remaining time ',remaining_time)
    
    #start monitoring user test session
    print('start minitoring')
    user = request.user
    exam = Test.objects.get(id=test_id)

    # Start monitoring in separate threads
    screen_thread = threading.Thread(target=capture_screen, args=(user, exam))
    webcam_thread = threading.Thread(target=monitor_webcam, args=(user, exam))
    #screen_thread.start()
    #webcam_thread.start()
   


    if request.method == 'POST':
        # Get the current attempt number
        result = Result.objects.filter(candidate=candidate, test=test).first()
    
        if result:
           attempt_number = result.attempt_number
        else:
           attempt_number = 0  # If no previous attempt, set to 0
        
        score = 0
        # Create the result object
            # Get the last attempt number
        last_result = Result.objects.filter(candidate=candidate, test=test).order_by('-attempt_number').first()
        
        if last_result:
            attempt_number = last_result.attempt_number + 1
        else:
            attempt_number = 1  # First attempt
        result = Result.objects.create(candidate=candidate, test=test, total_marks=score,attempt_number=attempt_number)
        
        # Loop through the questions and store result details
        for question in questions:
            selected_option_ids = request.POST.getlist(str(question.id))  # This will get all selected options for multiple choice
            qm=question.marks
            if question.question_type == 'multiple':  # For multiple answers
                # Iterate through selected options for multiple-choice questions  
               
                correct_option_count = QuestionOption.objects.filter(question_id=int(question.id)).count()
                print("multiple question found")
                for option_id in selected_option_ids:
                    selected_option = QuestionOption.objects.get(id=int(option_id))
                    
                    
                    ResultDetail.objects.create(result=result, question=question, selected_option=selected_option)
                    # Check if the option is correct
                    if selected_option.is_correct: # Assuming 'correct_options' is a many-to-many field
                        score += qm/correct_option_count
            elif question.question_type == 'single':  # For single choice (single option selected)
               
                if selected_option_ids:
                    print("single question found")
                    selected_option = QuestionOption.objects.get(id=int(selected_option_ids[0]))
                    # Check if the option is correct
                    ResultDetail.objects.create(result=result, question=question, selected_option=selected_option)
                    if selected_option.is_correct: # Assuming 'correct_options' is a many-to-many field
                        score += qm
                  
                    
            elif question.question_type == 'text':  # For text input questions
                answer_text = request.POST.get(str(question.id))  # Get the user's answer as text

                # Compute similarity
                answer = mark_text_question(answer_text, question.answer_text)
                score += qm * answer["percentage_score"]/100
                
                #answer = mark_text_question(sentence1, sentence2)
                print("Is Correct:", answer["is_correct"])
                print("Similarity Score:", answer["similarity_score"])
                print("percentage Score:", answer["percentage_score"])
                print("Feedback:", answer["feedback"])
                
                

                ResultDetail.objects.create(result=result, question=question, selected_option=None, answer_text=answer_text)
                if answer_text == question.answer_text:  # Compare with correct answer
                    score += 1
                    # Optionally, store text answer as a ResultDetail if required
                    

        # After processing all answers, update the total marks in the result object
        result.total_marks = score
        result.save()

        # Redirect to the result view page
        return redirect('dashboard')
    else:
        
        if remaining_time > 0:
            return render(request, 'take_test.html', {'test': test, 'questions': questions,'remaining_time': max(0, int(remaining_time)),'userId':candidate.id })
        else:
            return redirect('dashboard')
def test_monitor(request, test_id):
    test = Test.objects.get(id=test_id)

    admin = Admin.objects.get(user=request.user)
    now = timezone.now()  # Use Django's timezone.now()
    print('time now',now)
    remaining_time = (test.end_time - now).total_seconds() if test.end_time else 0
    
    print('test time',test.end_time)
    print('remaining time ',remaining_time)
    
    #start monitoring user test session
    print('start minitoring')
    user = request.user
    exam = Test.objects.get(id=test_id)
    candidates = exam.candidates.all()

    # Start monitoring in separate threads
    screen_thread = threading.Thread(target=capture_screen, args=(user, exam))
    webcam_thread = threading.Thread(target=monitor_webcam, args=(user, exam))
    #screen_thread.start()
    #webcam_thread.start()

    return render(request, 'test_monitor.html', {'test': test,'remaining_time': max(0, int(remaining_time)), 'candidates': candidates})
   
    

@login_required
def view_result(request, result_id):
    result = Result.objects.get(id=result_id)
    return render(request, 'test_result.html', {'result': result})

@login_required
def active_test(request, test_id):
    tests = Test.objects.get(id=test_id)
    return render(request, 'dashboard.html', {'test': tests})


# Load pre-trained spaCy model for text processing
nlp = spacy.load("en_core_web_md")  # Use "en_core_web_sm" for a smaller model

def get_lemmas(word):
    """
    Get the lemmatized forms of a word along with its synonyms using WordNet.
    """
    synsets = wn.synsets(word)
    lemmas = set()

    # Add the lemmatized form of the word itself
    lemmas.add(word.lower())

    for synset in synsets:
        for lemma in synset.lemmas():
            lemmas.add(lemma.name().lower())

    return lemmas

def clean_answer(question, answer):
    """
    Clean the candidate's answer by removing common question words and lemmatizing.
    """
    # Remove question context by eliminating common question words
    question_words = ["what", "how", "why", "explain", "describe", "list"]
    cleaned_answer = " ".join([word for word in answer.lower().split() if word not in question_words])

    # Further clean using lemmatization and synonym replacement
    cleaned_answer_tokens = cleaned_answer.split()

    # Create a set to store cleaned tokens
    final_tokens = []

    # Process each token in the cleaned answer
    for token in cleaned_answer_tokens:
        # Get the token object from spaCy, which allows access to the lemma
        token_doc = nlp(token)
        lemma_token = token_doc[0].lemma_  # Get the lemma (base form) of the word
        if lemma_token not in final_tokens:
            final_tokens.append(lemma_token)
    
    # Join the final tokens back into a cleaned answer string
    cleaned_answer = " ".join(final_tokens)

    # Optionally, remove any extra spaces
    cleaned_answer = " ".join(cleaned_answer.split())

    return cleaned_answer

def mark_text_question(candidate_answer, correct_answer, threshold=0.1, min_score=0.1):
    """
    Mark a text-based question by comparing the candidate's answer to the correct answer.
    This version focuses on domain-specific content, removing irrelevant context from the question.
    """
    if not candidate_answer or not correct_answer:
        return {
            "is_correct": False,
            "similarity_score": 0.0,
            "percentage_score": 0,
            "feedback": "No answer provided or correct answer missing."
        }

    # Clean the answers to remove question context and irrelevant words
    cleaned_candidate_answer = clean_answer(correct_answer, candidate_answer)
    cleaned_correct_answer = clean_answer(correct_answer, correct_answer)

    # Process the cleaned answers with spaCy
    candidate_doc = nlp(cleaned_candidate_answer)
    correct_doc = nlp(cleaned_correct_answer)

    # Compute semantic similarity using cosine similarity (for more specific matching)
    vectorizer = TfidfVectorizer().fit([cleaned_candidate_answer, cleaned_correct_answer])
    tfidf_matrix = vectorizer.transform([cleaned_candidate_answer, cleaned_correct_answer])
    similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    print('similarirt scoresss',similarity_score)
    # Calculate percentage score based on similarity
    percentage_score = similarity_to_percentage(similarity_score, min_score=min_score)

    # Check if the similarity score exceeds the threshold
    is_correct = similarity_score >= threshold

    # Generate feedback
    if is_correct:
        feedback = "Your answer is correct!"
    else:
        feedback = f"Your answer is not correct. The similarity score is {percentage_score}%. Consider reviewing the key points."

    return {
        "is_correct": is_correct,
        "similarity_score": similarity_score,
        "percentage_score": percentage_score,
        "feedback": feedback
    }

def similarity_to_percentage(similarity_score, min_score=0.1, quick_rise_factor=2,max_score=1):
    """
    Converts a similarity score into a percentage, scaling it from min_score to 100.
    """
    print('sim score',similarity_score)
    if similarity_score < 0.2:
        return 0  # 0% for scores in the range 0-0.1
    elif 0.2 <= similarity_score < 0.5:
        # Map 0.3-0.5 to 30%-80%
        return 30 + (similarity_score - 0.2) * (50 / 0.2)
    elif 0.5 <= similarity_score <= 1:
        # Map 0.5-1 to 80%-100%
        return 90 + (similarity_score - 0.5) * (20)
    elif similarity_score >1 :
        return 100
    else:
        raise ValueError("Similarity score must be between 0 and 1.")


def export_log_report_to_pdf(request, candidate_id):
    candidate = Candidate.objects.get(id=candidate_id)
    logs = MonitoringLog.objects.filter(candidate=candidate)

    # Create the HttpResponse object with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="log_report_{candidate.full_name}.pdf"'

    # Create a PDF canvas
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 40, f"Log Report for {candidate.full_name}")

    y_position = height - 80  # Set starting y position for content
    line_height = 14  # The space between lines (text height)

    # Add candidate email
    p.setFont("Helvetica", 12)
    p.drawString(50, y_position, f"Email: {candidate.user.email}")
    y_position -= line_height  # Move to next line

    # Loop through logs and add them to the PDF
    for i, log in enumerate(logs, start=1):
        if y_position < 40:  # Check if the content fits on the current page
            p.showPage()  # Start a new page
            p.setFont("Helvetica-Bold", 16)
            p.drawString(200, height - 40, f"Log Report for {candidate.full_name}")  # Add title again
            y_position = height - 80  # Reset y position for new page

        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, f"{i}. Activity Type: {log.get_activity_type_display()}")
        y_position -= line_height

        p.setFont("Helvetica", 12)
        p.drawString(50, y_position, f"Timestamp: {log.timestamp}")
        y_position -= line_height

        p.setFont("Helvetica", 12)
        p.drawString(50, y_position, f"Data: {log.data}")
        y_position -= line_height

        # Check for screenshot availability
        if log.screenshot:
            p.drawString(50, y_position, "Screenshot available.")
            y_position -= line_height
        else:
            p.drawString(50, y_position, "No screenshot available.")
            y_position -= line_height

        y_position -= 10  # Extra spacing between logs

    # Save the PDF
    p.showPage()
    p.save()

    return response




def export_results_to_excel(request):
    # Define the resource for exporting
    class ResultResource(resources.ModelResource):
        class Meta:
            model = Result

    # Create the resource and export
    result_resource = ResultResource()
    dataset = result_resource.export()

    # Return as HTTP response with Excel content type
    response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="results.xlsx"'
    return response