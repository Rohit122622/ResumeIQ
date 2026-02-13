import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_job_roles():
    path = os.path.join(BASE_DIR, "data", "job_roles.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def match_skills(resume_skills, job_role):
    job_roles = load_job_roles()

    if job_role not in job_roles:
        return {}

    required_skills = job_roles[job_role]

    resume_skills = set(skill.lower() for skill in resume_skills)
    required_skills = set(skill.lower() for skill in required_skills)

    matched = resume_skills.intersection(required_skills)
    missing = required_skills.difference(resume_skills)

    match_percentage = int((len(matched) / len(required_skills)) * 100)

    return {
        "job_role": job_role,
        "match_percentage": match_percentage,
        "matched_skills": list(matched),
        "missing_skills": list(missing)
    }
