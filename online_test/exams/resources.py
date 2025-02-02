# resources.py

from import_export import resources
from .models import Question, QuestionOption
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget


class QuestionOptionResource(resources.ModelResource):
    # Define a custom field to link the options to their respective questions
    question = Field(
        column_name='question_text', 
        attribute='question',
        widget=ForeignKeyWidget(Question, 'text')  # Match by the question text
    )
    
    class Meta:
        model = QuestionOption
        fields = ('question_text', 'text', 'is_correct')  # Customize fields as needed

class QuestionResource(resources.ModelResource):
    class Meta:
        model = Question
        fields = ('test', 'text', 'marks', 'max_selection', 'show_num_selection', 'question_type', 'image', 'answer_text', 'duration')
        export_order = ('test', 'text', 'marks', 'max_selection', 'show_num_selection', 'question_type', 'image', 'answer_text', 'duration')

    def before_import_row(self, row, **kwargs):
        # You can process the row data here before importing
        # For example, ensure test exists in the database
        return row
