from django.db import models
import os
from django.contrib.auth.models import User

from exams.models import Test

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    activity_type = models.CharField(max_length=50)  # e.g., "webcam", "screen"
    data = models.TextField()  # Store JSON or text data
    screenshot = models.ImageField(upload_to='monitoring_screenshots/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"