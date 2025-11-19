import os
import sys 
import django
import json

from langchain_ollama import ChatOllama
from app.models import SurveySubmission, SurveyAnswer
from django.contrib.auth import get_user_model

#Priv function allows for testing as a script
def _setup_django(): # Accesses the root directory project_gen -> app -> LetsBuild -> Root
    BASE_DIRECTORY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(BASE_DIRECTORY)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LetsBuild.settings")

    django.setup()

def _convert_to_LLM_text(quiz_data, interest_data):

    answer_json = json.dumps(quiz_data, indent=2)
    interest_json = json.dumps(interest_data, indent= 2)

    prompt = f"""
        You are an AI that recommends software development projects.

        Here is a JSON array of the user's survey answers:

        {answer_json}

        Here is a JSON array of the user's interests:

        {interest_json}

        Using this data, suggest 3 projects for the user, these projects need to be within grasp of the user based on the survey answer data. They also need to be thematically 
        focussed on at least one of their interests. An example could be this: user is interested in game development and astronomy, suggest a planetary simulation application
        that will help them learn physics (important for game engines). After defining the project, please provide 5 general steps to complete the project, at a later point the user can choose more specfic ones, but for now, they can be broad.

        Format the output like this:

        create an array of dicts, with each dict representing one project, in each project dict you will have these keys: project_name, difficulty, areas_of_focus and list_of_steps which will have a value of an array with the chosen steps to reach project creation

        IMPORTANT OUTPUT GUIDLINES: DO NOT RETURN ANYTHING BESIDES THE ARRAY OF DICTS SO I CAN BETTER PARSE THE DATA THAT INCLUDES ANY EXPLAINATION OR DESCRIBING THE PROJECTS AFTER THE 
        INITIAL DICT
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
    interest_data = submission.get_interests()
    quiz_data = SurveyAnswer.get_answers_for_submission(submission)

    return _convert_to_LLM_text(quiz_data, interest_data) 


def get_project_recs(user):

    llm = ChatOllama(
        model="llama3.2:1b",
    )

    prompt = get_logged_in_prompt(user)

    ai_msg = llm.invoke(prompt)

    print(ai_msg)
    try:
        projects = json.loads(ai_msg)

    except TypeError:
        projects = json.loads(ai_msg.content)
    except json.JSONDecodeError:

        cleaned = ai_msg.content.strip().split("\n")[0]
        projects = json.loads(clean)
    return projects


if __name__ == '__main__':
    
    _setup_django()

    from app.models import SurveySubmission, SurveyAnswer
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.get(username="quinn")

    prompt = get_logged_in_prompt(user)
    ai_msg = get_project_recs(prompt)

    print(ai_msg.content)