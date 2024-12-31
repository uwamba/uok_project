from django.db import models
from users.models import Candidate
from exams.models import Test,Question,QuestionOption

class Result(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    total_marks = models.IntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)
    attempt_number = models.IntegerField(default=0)  # Attempt number for this user


    def __str__(self):
        return f"{self.candidate.user.username} - {self.test.title} - {self.total_marks} marks"
class ResultDetail(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name="details")  # Link to Result model
    question = models.ForeignKey(Question, on_delete=models.CASCADE)  # Link to Question model
    selected_option = models.ForeignKey(QuestionOption, null=True, on_delete=models.CASCADE)  # Link to Option model
    answer_text = models.TextField(null=True, blank=True)  # For storing text answers
    def __str__(self):
        return f"Result Detail: {self.result.id} - Question: {self.question.id}"