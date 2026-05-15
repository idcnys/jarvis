
import json
import os

from helpers.skill_helpers import SKILLS_FILE


def view_skills():
    if not os.path.exists(SKILLS_FILE):
        return "I haven't learned any skills yet."

    with open(SKILLS_FILE, "r") as f:
        skills = json.load(f)

    if not skills:
        return "I haven't learned any skills yet."

    skill_list = "\n".join([f"- {skill_name}" for skill_name in skills.keys()])
    return f"Here are the skills I've learned:\n{skill_list} total {len(skills)} skills."