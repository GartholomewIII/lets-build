from django.contrib import admin

from .models import SurveySubmission, SurveyAnswer, UserProject

admin.site.register(SurveySubmission)
admin.site.register(SurveyAnswer)
admin.site.register(UserProject)