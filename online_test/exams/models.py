from django.db import models
from companies.models import Company 
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from users.models import Candidate


class Subject(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Test(models.Model):
    TEST_DURATION = 'test_duration'
    QUESTION_DURATION = 'question_duration'

    DURATION_TYPE_CHOICES = [
        (TEST_DURATION, _('Duration counter by overall test')),
        (QUESTION_DURATION, _('Every question has its duration')),
    ]
    title = models.CharField(max_length=255)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_marks = models.IntegerField()
    max_attempts = models.IntegerField(default=1)  # Maximum allowed attempts
    candidates = models.ManyToManyField(Candidate, related_name="tests")
    duration = models.DurationField(null=True, blank=True) 
    counterType = models.CharField(
        max_length=100,
        choices=DURATION_TYPE_CHOICES,
        default=TEST_DURATION,
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    

    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        if not self.created_by:  # Set created_by if it's not already set
            self.created_by = kwargs.get('user', None)  # This assumes you pass the user when saving
        super().save(*args, **kwargs)
    
class Question(models.Model):
    SINGLE_ANSWER = 'single'
    MULTIPLE_ANSWER = 'multiple'
    TEXT_ANSWER = 'text'

    QUESTION_TYPE_CHOICES = [
        (SINGLE_ANSWER, _('Multiple Choice (Single Answer)')),
        (MULTIPLE_ANSWER, _('Multiple Choice (Multiple Answers)')),
        (TEXT_ANSWER, _('Text Answer')),
    ]

    test = models.ForeignKey(Test, on_delete=models.CASCADE,related_name='questions')
    text = models.TextField()
    marks = models.IntegerField()
    max_selection = models.IntegerField(default=1)
    show_num_selection=models.BooleanField(default=False)
    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPE_CHOICES,
        default=SINGLE_ANSWER,
    )
    image = models.ImageField(upload_to='questions/', blank=True, null=True)
    answer_text = models.TextField(null=True, blank=True)  # For storing text answers
    duration = models.DurationField(null=True, blank=True) 
    def __str__(self):
        return f"Question: {self.text[:50]}..."  # Truncate text for readability in the admin


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name="options", on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text[:50]