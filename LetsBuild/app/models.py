from django.db import models
from django.conf import settings
# Create your models here.

class Quiz(models.Model):
    name = models.CharField(max_length=300)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

class SurveySubmission(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete= models.SET_NULL,
        null= True,
        blank= True
    )

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add= True)


class SurveyAnswer(models.Model):

    submission = models.ForeignKey(
        SurveySubmission,
        related_name= 'answers',
        on_delete= models.CASCADE,
    )

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add= True)

    
