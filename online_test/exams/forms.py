from django import forms
from .models import Question, QuestionOption
from .models import Test
from .models import Test, Candidate
from django_select2.forms import Select2MultipleWidget

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['test', 'text', 'marks', 'question_type', 'image']

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.fields['question_type'].widget = forms.Select(choices=Question.QUESTION_TYPE_CHOICES)

class QuestionOptionForm(forms.ModelForm):
    class Meta:
        model = QuestionOption
        fields = ['text', 'is_correct']
        


class TestForm(forms.ModelForm):
    
    class Meta:
        model = Test
        fields = ['title', 'subject', 'start_time', 'end_time', 'total_marks', 'max_attempts', 'candidates', 'duration', 'counterType']
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})  # This renders a datetime input field
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})  # This renders a datetime input field
    )
    candidates = forms.ModelMultipleChoiceField(
        queryset=Candidate.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Pop the logged-in user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        print(instance, self.user)  
        if self.user:
            instance.created_by = self.user  # Set the logged-in user as the creator
        if commit:
            instance.save()
        return instance
    
from django import forms
from .models import Question

from django import forms
from django.forms import inlineformset_factory
from .models import Question, QuestionOption

# Main Question Form
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['test', 'text', 'marks', 'max_selection', 'show_num_selection', 'question_type', 'image', 'answer_text', 'duration']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your question here...', 'rows': 3}),
            'marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_selection': forms.NumberInput(attrs={'class': 'form-control'}),
            'show_num_selection': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'answer_text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter the expected text answer...', 'rows': 2}),
            'duration': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Enter duration (HH:MM:SS)'}),
        }

# Question Option Form
class QuestionOptionForm(forms.ModelForm):
    class Meta:
        model = QuestionOption
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter option text'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# Formset for Question Options
QuestionOptionFormSet = inlineformset_factory(
    Question, QuestionOption, form=QuestionOptionForm,
    extra=1, can_delete=True
)
