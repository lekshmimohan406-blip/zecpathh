import re
from .skills import SKILLS


def extract_skills(text):
    found_skills = []

    text_lower = text.lower()

    for skill in SKILLS:
        if skill.lower() in text_lower:
            found_skills.append(skill)

    return list(set(found_skills))

import re

def extract_experience(text):
    experience = re.findall(r'(\d+)\s*\+?\s*years?', text, re.IGNORECASE)

    if experience:
        return experience[0]

    return "Fresher"

def extract_education(text):
    education_keywords = [
        "B.Tech",
        "Bachelor",
        "M.Tech",
        "Master",
        "B.Sc",
        "M.Sc",
        "BCA",
        "MCA",
        "Diploma",
        "Higher Secondary",
        "SSLC"
    ]

    found = []

    text_lower = text.lower()

    for edu in education_keywords:
        if edu.lower() in text_lower:
            found.append(edu)

    return list(set(found))

def parse_resume(text):
    return {
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "education": extract_education(text),
    }