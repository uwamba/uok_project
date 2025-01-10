from django.db import models
import os
from django.contrib.auth.models import User
from companies.models import Company
from django.conf import settings
from exams.models import Test
import json
from django.core.exceptions import ValidationError
from django.utils.timezone import now

def video_upload_path(instance, filename):
    return os.path.join('uploads', filename)

class Video(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=video_upload_path)
     #user = models.OneToOneField(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
class MonitoringLog(models.Model):
    ACTIVITY_TYPES = [
        ('webcam', 'Webcam'),
        ('screen', 'Screen'),
        ('audio', 'Audio'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    data = models.TextField()  # Store JSON or text data
    screenshot = models.ImageField(upload_to='monitoring_screenshots/', null=True, blank=True)
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(null=True, blank=True)

    def clean(self):
        try:
            json.loads(self.data)
        except json.JSONDecodeError:
            raise ValidationError("Data must be valid JSON.")

    @property
    def duration(self):
        if self.end_time:
            return self.end_time - self.start_time
        return None

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"
    
