import os
import sys 
import django
import json

from langchain_ollama import ChatOllama

#Priv function allows for testing as a script
def _setup_django(): # Accesses the root directory project_gen -> app -> LetsBuild -> Root
    BASE_DIRECTORY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(BASE_DIRECTORY)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LetsBuild.settings")

    django.setup()

def _convert_to_LLM_text(data):

    answer_json = json.dumps(data, indent=2)

    prompt = f"""
        You are an AI that recommends software development projects.

        Here is a JSON array of the user's survey answers:

        {answer_json}

        Using this data, suggest 5 projects for the user, for each project please provide at least 5 steps in reaching that goal, they can be broad
        but easy to figure out on your own or learn. The purpose of this project is to provide fun projects that makes programming more fun.

        Format the output like this:

        create an array of dicts, with each dict representing one project, in each project dict you will have these keys: project_name, difficulty, areas_of_focus and list_of_steps which will have a value of an array with the chosen steps to reach project creation

        """

    return prompt


def get_logged_in_prompt(user): #pass through user obj to peek at data
    if not user.is_authenticated:
        return

    #last submission (should be only one after logged in)
    submission = (
        SurveySubmission.objects
        .filter(user=user)
        .order_by('-created_at')
        .first()
    )

    if submission is None:
        return []

    # Get their answers as dicts
    answers_data = SurveyAnswer.get_answers_for_submission(submission)

    return _convert_to_LLM_text(answers_data) 


def get_project_recs(prompt):

    llm = ChatOllama(
        model="llama3.2:1b",
    )


    ai_msg = llm.invoke(prompt)

    return ai_msg


if __name__ == '__main__':
    
    _setup_django()

    from app.models import SurveySubmission, SurveyAnswer
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.get(username="quinn")

    prompt = get_logged_in_prompt(user)
    ai_msg = get_project_recs(prompt)

    print(ai_msg.content)