from django.db import models

# Create your models here.
# chat/models.py
from django.db import models

from users.models import Candidate

class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
class Message(models.Model):
    sender = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    receiver = models.ForeignKey(Candidate, related_name="messages_received", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
