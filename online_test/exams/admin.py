from django.contrib import admin

from users.models import Candidate
from .models import Subject
from .models import Test
from .models import Question, QuestionOption
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, get_object_or_404
from .models import Test
from videos.models import MonitoringLog
from import_export.admin import ExportMixin, ImportMixin
# Register your models here.

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 1 # Allow 3 options to be added initially
    fields = ['text', 'is_correct']

class QuestionAdmin(ImportMixin, ExportMixin,admin.ModelAdmin):
    list_display = ['text', 'question_type', 'marks']
    list_filter = ['question_type','test']
    inlines = [QuestionOptionInline]



# Custom admin class for the Test model
class TestAdmin(ImportMixin, ExportMixin,admin.ModelAdmin):
    list_display = ('title', 'start_time','end_time', 'total_marks','duration','counterType','created_by')
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:  # Admins can see all records
            return queryset
        return queryset.filter(created_by=request.user)  # Only show records created by the logged-in user

    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.created_by == request.user:
            return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.created_by == request.user:
            return True
        return super().has_delete_permission(request, obj)
admin.site.register(Test, TestAdmin)
   

admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionOption)  # Optionally register QuestionOption separately
admin.site.register(Subject)


