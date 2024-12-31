from django.contrib import admin
from .models import Candidate, Admin

admin.site.register(Admin)
admin.site.register(Candidate)