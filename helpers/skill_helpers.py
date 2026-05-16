import json
import os

from helpers.physical_helpers import close_app, enter_text, music_control, open_app, press_key, run_terminal_command
from constants import SKILLS_FILE

def save_skill(skill_name: str, commands: list[dict]):
    """
    Saves a sequence of actions as a named skill for later use.

    Args:
        skill_name: The unique name for this skill (e.g., 'open_work_tools').
        commands: A list of dictionaries, where each dict has 'tool' and 'arg' keys.
    """
    if not os.path.exists("memory"):
        os.makedirs("memory")
        
    skills = {}
    if os.path.exists(SKILLS_FILE):
        with open(SKILLS_FILE, "r") as f:
            skills = json.load(f)

    skills[skill_name.lower()] = commands
    
    with open(SKILLS_FILE, "w") as f:
        json.dump(skills, f, indent=4)
        
    return f"Successfully learned the skill: {skill_name}"

def run_skill(skill_name: str):
    """
    Executes a previously saved sequence of actions by its name.

    Args:
        skill_name: The name of the skill to execute (e.g., 'morning_routine').
    """
    if not os.path.exists(SKILLS_FILE):
        return "I haven't learned any skills yet."

    with open(SKILLS_FILE, "r") as f:
        skills = json.load(f)

    skill = skills.get(skill_name.lower())
    if not skill:
        return f"I don't know a skill called {skill_name}."

    # Logic to map strings to your imported physical_helpers
    mapping = {
        "open_app": open_app,
        "close_app": close_app,
        "run_terminal_command": run_terminal_command,
        "press_key": press_key,
        "enter_text": enter_text,
        "music_control": music_control
    }

    for action in skill:
        func = mapping.get(action['tool'])
        if func:
            func(action['arg']) 
            
    return f"Executed skill: {skill_name}"