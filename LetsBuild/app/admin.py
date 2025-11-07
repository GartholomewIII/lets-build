from django.contrib import admin

from .models import SurveySubmission, SurveyAnswer

admin.site.register(SurveySubmission)
admin.site.register(SurveyAnswer)
