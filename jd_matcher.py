# ---------------- SEMANTIC GROUPS ----------------

SEMANTIC_GROUPS = {
    "Backend Frameworks": ["flask", "django", "spring", "node"],
    "Concepts": ["rest", "api", "data structures", "algorithms"],
    "Databases": ["sql", "mysql", "postgresql", "mongodb"],
    "Programming Languages": ["python", "java", "c", "c++"],
    "Experience Indicators": ["experience", "understanding", "knowledge"]
}

def group_missing_keywords(missing_keywords):
    grouped = {}
    used = set()

    for group, keywords in SEMANTIC_GROUPS.items():
        matches = [kw for kw in missing_keywords if kw in keywords]
        if matches:
            grouped[group] = matches
            used.update(matches)

    remaining = [kw for kw in missing_keywords if kw not in used]
    if remaining:
        grouped["Other"] = remaining

    return grouped


def match_jd(resume_skills, job_description):
    job_description = job_description.lower()

    matched_skills = []
    missing_keywords = []

    stopwords = {
        "and","or","the","is","are","for","with","we","have",
        "to","of","in","a","an","should","must","candidate",
        "strong","knowledge","software","engineer"
    }

    # Match resume skills with JD
    for skill in resume_skills:
        if skill.lower() in job_description:
            matched_skills.append(skill)

    # Extract keywords from JD
    jd_words = set(
        word for word in job_description.split()
        if word.isalpha()
        and word not in stopwords
        and word not in [s.lower() for s in resume_skills]
    )

    missing_keywords.extend(jd_words)

    match_percentage = int(
        (len(matched_skills) / max(len(resume_skills), 1)) * 100
    )

    grouped_missing = group_missing_keywords(missing_keywords[:10])

    return {
        "match_percentage": match_percentage,
        "matched_skills": matched_skills,
        "missing_keywords": missing_keywords[:10],
        "grouped_missing": grouped_missing
    }

