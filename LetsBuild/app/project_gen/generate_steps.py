import json
import re
from langchain_ollama import ChatOllama
from app.models import UserProject

def clean_sub_steps(ai_output):
    if not isinstance(ai_output, str):
        return []

    # Remove code fences
    text = re.sub(r"```[a-zA-Z]*", "", ai_output).replace("```", "").strip()


    lines = [line.strip() for line in text.splitlines() if line.strip()]

    fixed_lines = []
    for line in lines:
        if not (line.startswith('"') and line.endswith('"')):
            line = line.replace('"', '')  
            line = f'"{line}"'
        fixed_lines.append(line)


    json_text = "[" + ",".join(fixed_lines) + "]"

    try:
        data = json.loads(json_text)
        return [s.strip() for s in data if isinstance(s, str)]
    except json.JSONDecodeError:
        print("FAILED TO PARSE JSON:", json_text)
        return []

def _convert_to_LLM_substep_prompt(selected_step: str):
    prompt = f"""
You are an AI assistant. The user has a project step:

"{selected_step}"

Generate exactly 5 actionable sub-steps to help the user complete this step. 
- Return plain step content only (we will add numbering automatically).
- Include resources like books, blogs, or YouTube tutorials if relevant.
- Return ONLY a JSON array of strings, like:

[
    "First sub-step",
    "Second sub-step",
    "Third sub-step",
    "Fourth sub-step",
    "Fifth sub-step"
]

Do not include any extra text, Markdown, or explanation.
"""
    return prompt

def get_sub_steps_from_ai(step_text: str):
    llm = ChatOllama(model="llama3.2:1b")
    prompt = _convert_to_LLM_substep_prompt(step_text)
    ai_msg = llm.invoke(prompt)
    return clean_sub_steps(ai_msg.content)

def insert_sub_steps(chosen_project: dict, step_text: str, sub_steps: list):
    steps = chosen_project.get("list_of_steps", [])
    merged = []
    step_number = None

    match = re.match(r"Step (\d+)", step_text)
    if match:
        step_number = match.group(1)


    trimmed_sub_steps = [s for s in sub_steps if s not in ("[", "]")]


    labeled_sub_steps = []
    if step_number:
        for i, sub in enumerate(trimmed_sub_steps):
            labeled_sub_steps.append(f"Step {step_number}{chr(97+i)}: {sub.strip().rstrip(',')}")

    for s in steps:
        merged.append(s)
        if s == step_text:
            merged.extend(labeled_sub_steps)

    chosen_project["list_of_steps"] = merged
    return chosen_project

def get_more_steps_function(user, step_text):
    user_project = UserProject.objects.filter(user=user).latest("created_at")
    project_data = user_project.project
    sub_steps = get_sub_steps_from_ai(step_text)
    new_project = insert_sub_steps(project_data, step_text, sub_steps)
    return new_project
