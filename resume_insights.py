def analyze_resume_insights(resume_text, skills):
    insights = {}

    # 1️⃣ Resume Length Analysis
    word_count = len(resume_text.split())

    if word_count < 150:
        insights["length"] = "Too Short – Resume lacks detail"
    elif 150 <= word_count <= 400:
        insights["length"] = "Good Length – Ideal for ATS"
    else:
        insights["length"] = "Too Long – Consider shortening"

    # 2️⃣ Section Presence Check
    sections = {
        "education": "Education",
        "experience": "Experience",
        "project": "Projects",
        "skill": "Skills"
    }

    missing_sections = []
    for key in sections:
        if key not in resume_text.lower():
            missing_sections.append(sections[key])

    insights["missing_sections"] = missing_sections

    # 3️⃣ Skill Density
    skill_count = len(skills)
    insights["skill_density"] = f"{skill_count} skills detected"

    # 4️⃣ Overall Resume Strength
    score = 0

    if word_count >= 150:
        score += 1
    if len(missing_sections) <= 1:
        score += 1
    if skill_count >= 5:
        score += 1

    if score == 3:
        insights["strength"] = "Strong Resume"
    elif score == 2:
        insights["strength"] = "Moderate Resume"
    else:
        insights["strength"] = "Weak Resume"

    return insights
