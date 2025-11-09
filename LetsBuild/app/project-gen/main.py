

from app.models import SurveySubmission, SurveyAnswer
import os
import django


def setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LetsBuild.settings")
    django.setup()

def get_latest_submission_with_answers():
    
    submission = (
        SurveySubmission.objects
        .order_by('-created_at')
        .select_related('quiz')
        .first()
    )

    if submission is None:
        return None, []

    answers = (
        SurveyAnswer.objects
        .filter(submission=submission)
        .select_related('question', 'answer')
    )

    return submission, list(answers)


if __name__ == '__main__':
    get_latest_submission_with_answers()