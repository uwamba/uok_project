from django import forms
from .models import Question, QuestionOption
from .models import Test
from .models import Test, Candidate
from .models import Question
from django.forms import inlineformset_factory
from .models import Test, Question, QuestionOption, Candidate
from django_select2.forms import Select2Widget # type: ignore
from dal import autocomplete
from django.core.exceptions import ValidationError



# Form for Test
class TestForm(forms.ModelForm):
        
    candidates = forms.ModelMultipleChoiceField(
        queryset=Candidate.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(
            url='candidate-autocomplete'  # URL for the autocomplete view
        )
    )
   
    class Meta:
        model = Test
        fields = ['title', 'subject', 'start_time', 'end_time', 'total_marks', 'max_attempts', 'duration', 'counterType', 'candidates']

# Form for Question
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'marks', 'question_type', 'max_selection', 'show_num_selection', 'duration', 'image']

# Form for QuestionOption
class QuestionOptionForm(forms.ModelForm):
    class Meta:
        model = QuestionOption
        fields = ['text', 'is_correct']
from django.forms import modelformset_factory, inlineformset_factory

# Formset for Questions
QuestionFormSet = modelformset_factory(
    Question,
    form=QuestionForm,
    extra=1  # Adjust the number of extra forms to display
)

# Inline formset for Question Options
QuestionOptionFormSet = inlineformset_factory(
    Question,
    QuestionOption,
    form=QuestionOptionForm,
    extra=1  # Adjust the number of extra forms to display
)

from django import forms
from .models import Subject

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'description']  # Include 'company' if it's necessary for the form
from users.models import Candidate, User
from django.contrib.auth.forms import UserCreationForm
class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['user', 'company', 'date_of_birth', 'phone_number', 'full_name', 'access_start_time', 'access_end_time']
        widgets = {
            'access_start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'access_end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class UserRegistrationForm(UserCreationForm):
    # Don't need is_candidate field, it will be set automatically in the view.
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']
        
class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['full_name', 'phone_number', 'date_of_birth', 'access_start_time', 'access_end_time']
        
class ImportQuestionsForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file.name.endswith('.xlsx'):
            raise ValidationError("Only Excel (.xlsx) files are allowed.")
        return file
