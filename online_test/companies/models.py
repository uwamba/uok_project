from django.db import models

# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.TextField()
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name