import os
import sys 
import django

#Priv function allows for testing as a script
def _setup_django(): # Accesses the root directory project_gen -> app -> LetsBuild -> Root
    BASE_DIRECTORY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(BASE_DIRECTORY)

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

    _setup_django()

    from app.models import SurveySubmission, SurveyAnswer

    submission = SurveySubmission.objects.order_by('-created_at').first()

    answers_data = SurveyAnswer.get_answers_for_submission(submission)

    print(answers_data)