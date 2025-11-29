import os
import sys
import django
import json
import re
import ast

from langchain_ollama import ChatOllama
from app.models import UserProject
from django.contrib.auth import get_user_model

def clean_expanded_steps(ai_output):

    if not isinstance(ai_output, str):
        return {}

    # Remove code fences
    text = re.sub(r"```[a-zA-Z]*", "", ai_output).replace("```", "").strip()

    # Find first { and last } — may truncate if missing final }
    start = text.find("{")
    end = text.rfind("}")
    if start == -1:
        print(f"LLM OUTPUT ERROR: No JSON object found in output: {ai_output}")
        return {}

    if end == -1:
        # Attempt to close missing JSON
        text += "}"
        end = len(text) - 1

    text = text[start:end+1]

    # Remove trailing commas like ,} or ,]
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)

    # Try loading JSON
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Attempt to close list_of_steps array if needed
        if '"list_of_steps": [' in text:
            text += "]}"
            try:
                data = json.loads(text)
            except:
                print(f"FAILED TO PARSE JSON even after auto-closing: {text}")
                return {}
        else:
            print(f"FAILED TO PARSE JSON: {text}")
            return {}

    # Clean step strings of extra quotes
    if "list_of_steps" in data and isinstance(data["list_of_steps"], list):
        cleaned_steps = []
        for step in data["list_of_steps"]:
            if isinstance(step, str):
                step = step.strip('"').strip("'")
                cleaned_steps.append(step)
        data["list_of_steps"] = cleaned_steps

    return data


def _convert_to_LLM_text(chosen_project, step):
    
    step = str(step)
    chosen_json = json.dumps(chosen_project, indent=2)

    prompt = f"""
        You are an AI that recommended a project to the user.

        The current project is:

        {chosen_json}

        The user has requested 5 new sub-steps for the following step:

        "{step}"

        INSTRUCTIONS:

        1. Return a **valid JSON object** that is identical to the current project.
        2. Do **NOT modify any keys or values** except for "list_of_steps".
        3. In "list_of_steps":
        - Find the step that matches "{step}" exactly.
        - Insert exactly 5 new sub-steps **immediately after this step**.
        - Label them as "{step}a", "{step}b", "{step}c", "{step}d", "{step}e".
        4. Preserve all other steps **exactly as they are** in the original array.
        5. The new sub-steps should be actionable, specific, and may include resources (books, blogs, YouTube).
        6. Do NOT add extra steps, do NOT renumber unrelated steps, and DO NOT change the order of existing steps.
        7. Do NOT include Markdown, explanations, or text outside the JSON.
        8. Ensure strings are properly quoted and JSON is valid.

        Example structure:

        {{
        "project_name": "Original Project Name",
        "difficulty": "Original difficulty",
        "areas_of_focus": ["Original areas"],
        "list_of_steps": [
            "Step 1: Original step",
            "Step 1a: New sub-step with resources",
            "Step 1b: New sub-step with resources",
            "Step 1c: New sub-step with resources",
            "Step 1d: New sub-step with resources",
            "Step 1e: New sub-step with resources",
            "Step 2: Original step",
            "Step 3: Original step"
        ]
        }}
        """
    return prompt


def get_prompt(user, step):

    user_project = UserProject.objects.filter(user=user).latest("created_at")

    
    project_data = user_project.project

    return _convert_to_LLM_text(project_data, step)

def get_more_steps_function(user, step):

    llm = ChatOllama(model="llama3.2:1b")
    prompt = get_prompt(user, step)
    ai_msg = llm.invoke(prompt)
    print(ai_msg.content)
    new_project = clean_expanded_steps(ai_msg.content)
    
    return new_project

