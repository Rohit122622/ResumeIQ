ROLE_SKILLS = {
    "Web Developer": ["html", "css", "javascript", "react", "sql"],
    "Backend Developer": ["python", "java", "sql", "flask", "api"],
    "Data Analyst": ["python", "sql", "pandas", "excel", "statistics"],
    "Software Engineer": ["c", "c++", "java", "data structures"],
    "ML Engineer": ["python", "machine learning", "numpy", "pandas"]
}

def get_confidence_reason(role, matched_skills):
    matched = set(skill.lower() for skill in matched_skills)

    if role == "Web Developer" and matched.intersection({"html", "css", "javascript", "react"}):
        return "Strong frontend skill overlap"

    if role == "Backend Developer" and matched.intersection({"python", "flask", "api", "sql"}):
        return "Backend development skill alignment"

    if role == "ML Engineer" and matched.intersection({"python", "machine learning", "numpy", "pandas"}):
        return "Programming + Python dominance"

    if role == "Data Analyst" and matched.intersection({"python", "sql", "pandas", "statistics"}):
        return "Data analysis and statistics focus"

    if role == "Software Engineer":
        return "General engineering skill alignment"

    return "Relevant skill match"


def predict_multiple_roles(resume_skills):
    scores = []

    resume_skills_lower = [skill.lower() for skill in resume_skills]

    for role, skills in ROLE_SKILLS.items():
        matched = set(resume_skills_lower).intersection(
            set(skill.lower() for skill in skills)
        )

        score = int((len(matched) / len(skills)) * 100)

        scores.append({
            "role": role,
            "score": score,
            "matched_skills": list(matched),
            "missing_skills": list(set(skills) - matched),
            "reason": get_confidence_reason(role, matched)
        })

    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores[:3]   # Top 3 roles
