import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------- CRITICAL SKILLS PER ROLE ----------------

CRITICAL_SKILLS = {
    "Web Developer": ["html", "css", "javascript", "react"],
    "Backend Developer": ["python", "flask", "api", "sql"],
    "Data Analyst": ["python", "sql", "pandas", "statistics"],
    "ML Engineer": ["python", "machine learning", "numpy"],
    "Software Engineer": ["data structures", "algorithms", "java", "c++"]
}

def load_job_roles():
    path = os.path.join(BASE_DIR, "data", "job_roles.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def classify_missing_skills(role, missing_skills, required_skills):
    critical = []
    optional = []

    required_set = set(skill.lower() for skill in required_skills)

    for skill in missing_skills:
        if skill.lower() in required_set:
            critical.append(skill)
        else:
            optional.append(skill)

    return {
        "critical": critical,
        "optional": optional
    }

def calculate_ats_score(parsed_data, job_role):
    job_roles = load_job_roles()

    resume_skills = set(skill.lower() for skill in parsed_data.get("skills", []))
    required_skills = set(skill.lower() for skill in job_roles.get(job_role, []))

    matched_skills = resume_skills.intersection(required_skills)
    missing_skills = required_skills.difference(resume_skills)

    # 1️⃣ Skill Match (50 points)
    if len(required_skills) > 0:
        skill_score = int((len(matched_skills) / len(required_skills)) * 50)
    else:
        skill_score = 0

    # 2️⃣ Keyword Coverage (30 points)
    keyword_score = min(len(resume_skills) * 2, 30)

    # 3️⃣ Resume Completeness (20 points)
    completeness = 0
    if parsed_data.get("name"):
        completeness += 5
    if parsed_data.get("email"):
        completeness += 5
    if parsed_data.get("phone"):
        completeness += 5
    if parsed_data.get("skills"):
        completeness += 5

    total_score = skill_score + keyword_score + completeness
    total_score = min(total_score, 100)

    missing_classified = classify_missing_skills(
        job_role,
        list(missing_skills),
        job_roles.get(job_role, [])
    )


    return {
        "ats_score": total_score,
        "skill_score": skill_score,
        "keyword_score": keyword_score,
        "completeness_score": completeness,
        "matched_skills": list(matched_skills),
        "missing_skills": list(missing_skills),
        "missing_classified": missing_classified
    }
