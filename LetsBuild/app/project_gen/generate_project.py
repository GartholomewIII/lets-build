import os
import sys 
import django
import json
import re
import ast

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
    interest_json = json.dumps(interest_data, indent=2)

    # Added "Strict JSON" instruction to prompt
    prompt = f"""
        You are an AI that recommends software development projects.
        
        User Survey Answers:
        {answer_json}

        User Interests:
        {interest_json}

        Suggest 3 projects. They must be thematically focused on the user's interests and match their skill level from the survey.
        
        Structure the output as a strictly valid JSON array of objects.
        Each object must have these keys: "project_name", "difficulty", "areas_of_focus", "list_of_steps".
        
        Example format:
        [
            {{
                "project_name": "Planetary Sim",
                "difficulty": "Intermediate",
                "areas_of_focus": "Physics, Game Dev",
                "list_of_steps": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"]
            }}
        ]

        Return ONLY the JSON array. Do not include "Here is your project" or Markdown formatting.
    """

    return prompt

def _clean_text(text):

    if not isinstance(text, str):
        return [] 

    text = re.sub(r"```[a-zA-Z]*", "", text)
    text = text.replace("```", "")


    start_index = text.find('[')
    end_index = text.rfind(']')

    if start_index == -1 or end_index == -1:
        # Fallback: Sometimes models output just one dict without the list brackets
        if text.strip().startswith('{') and text.strip().endswith('}'):
            text = f"[{text}]"
        else:
            print(f"LLM OUTPUT ERROR: Could not find brackets. Output: {text}")
            return []

    
    if start_index != -1 and end_index != -1:
        text = text[start_index : end_index + 1]

    
    try:
        
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    try:
        text_fixed = re.sub(r",\s*]", "]", text)
        text_fixed = re.sub(r",\s*}", "}", text_fixed)
        return json.loads(text_fixed)
    except json.JSONDecodeError:
        pass

    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError):
        pass
        
    print(f"FAILED TO PARSE JSON: {text}")
    return []

def get_logged_in_prompt(user): 
    if not user.is_authenticated:
        return

    
    submission = (
        SurveySubmission.objects
        .filter(user=user)
        .order_by('-created_at')
        .first()
    )
    
    
    if submission is None:
        return []

    
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
    return _clean_text(ai_msg.content)


if __name__ == '__main__':
    
    _setup_django()

    from app.models import SurveySubmission, SurveyAnswer
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.get(username="quinn")

    prompt = get_logged_in_prompt(user)
    ai_msg = get_project_recs(prompt)

    print(ai_msg.content)