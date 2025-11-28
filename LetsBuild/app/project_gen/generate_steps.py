import os
import sys
import django
import json
import re
import ast

from langchain_ollama import ChatOllama
from app.models import UserProject
from django.contrib.auth import get_user_model
from generate_project import _clean_text



def _convert_to_LLM_text(chosen_project, step):
    

    step = str(step)
    chosen_json = json.dumps(chosen_project, indent=2)
    prompt = f"""
        You are an AI that previously reccomended a project to the user to inspire creativity and learning

        Here is your generated project and the one the user is currently working on:

        {chosen_json}

        The user has asked for 5 more clarifying steps for the given project step below:

        {step}

        Your job is to lead the developer in the right direction, the intention of the original steps is to be relatively vague, at this point I want you to
        reccomend precise steps to the user, not exceeding 40 words.

        With these steps I want you to provide resources, to understand A you must first understand B, and provide a linear learning path to complete the provided step

        I want these 5 steps to be placed within an array

        Example output:
            [
            step 1,
            step 2,
            step 3, 
            step 4,
            step 5,
            ]

        """

    return prompt


def get_prompt(user, step):

    user_project = UserProject.objects.filter(user=user).latest("created_at")

    
    project_data = user_project.project

    return _convert_to_LLM_text(project, step)


def get_more_steps(user, step):

    llm = ChatOllama(model="llama3.2:1b")
    prompt = get_prompt(user, step)
    ai_msg = llm.invoke(prompt)
    return _clean_text(ai_msg.content)

