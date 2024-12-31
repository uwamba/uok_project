from django.contrib import admin
from .models import Subject
from .models import Test
from .models import Question, QuestionOption

# Register your models here.

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 1 # Allow 3 options to be added initially
    fields = ['text', 'is_correct']

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'question_type', 'marks']
    list_filter = ['question_type']
    inlines = [QuestionOptionInline]

admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionOption)  # Optionally register QuestionOption separately
admin.site.register(Subject)
admin.site.register(Test)
