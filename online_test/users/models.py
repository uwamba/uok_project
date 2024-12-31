from django.db import models
from django.contrib.auth.models import User
from companies.models import Company



# Create your models here.
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True)
    phone_number = models.CharField(max_length=20,null=True)
    full_name = models.CharField(max_length=100,null=True)

    def __str__(self):
        return self.user.username
class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True)
    phone_number = models.CharField(max_length=20,null=True)
    full_name = models.CharField(max_length=100,null=True)
    access_start_time = models.DateTimeField(null=True, blank=True)  # Start time for system access
    access_end_time = models.DateTimeField(null=True, blank=True)    # End time for system access

    def __str__(self):
        return self.user.username