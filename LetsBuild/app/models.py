'''
Author: Quinn (Gigawttz)

What it Does: Creates user object that data is recorded into
'''
from django.db import models
from django.conf import settings


class Quiz(models.Model):
    name = models.CharField(max_length=300)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)



#HOLDS USERS INTERESTS
class SurveySubmission(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete= models.SET_NULL,
        null= True,
        blank= True
    )

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add= True)

    def __str__(self):

        return f'Submission Number {self.id} for quiz {self.quiz.name}'

    interests = models.JSONField(default= list, blank= True)

    def set_interests(self, slugs):

        clean, seen = [], set()

        for s in slugs:
            s = str(s).strip()

            if s and s not in seen:
                seen.add(s)
                clean.append(s)

            if len(clean) == 5:
                break

        self.interests = clean
        self.save(update_fields= ["interests"])

    def get_interests(self):
        return self.interests

# HOLDS QUIZ DATA (NO INTERESTS)
class SurveyAnswer(models.Model):

    submission = models.ForeignKey(
        SurveySubmission,
        related_name= 'answers',
        on_delete= models.CASCADE,
    )

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add= True)

    @classmethod
    
    def get_answers_for_submission(cls, submission: SurveySubmission):
        qs = cls.objects.filter(submission=submission).select_related("question", "answer")
        return [
            {
                "question_id": sa.question_id,
                "question_text": sa.question.text,
                "answer_id": sa.answer_id,
                "answer_text": sa.answer.text,
            }
            for sa in qs
        ]
    

    def __str__(self):

        return f'Q: {self.question.text} A: {self.answer.text }'

