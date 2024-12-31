from django import forms
from .models import Question, QuestionOption

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
