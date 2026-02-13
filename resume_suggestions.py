def generate_suggestions(insights, missing_skills, jd_result):
    suggestions = []

    # Resume length
    if "Too Short" in insights["length"]:
        suggestions.append("Add more project details and responsibilities to increase resume depth.")

    if "Too Long" in insights["length"]:
        suggestions.append("Shorten descriptions and remove less relevant content.")

    # Missing sections
    for sec in insights["missing_sections"]:
        suggestions.append(f"Add a dedicated {sec} section to improve ATS score.")

    # Missing skills
    for skill in missing_skills[:3]:
        suggestions.append(f"Consider learning or mentioning {skill} if you have experience.")

    # JD match improvement
    if jd_result["match_percentage"] < 70:
        suggestions.append("Customize your resume keywords according to the job description.")

    if not suggestions:
        suggestions.append("Your resume is well optimized. Minor improvements can make it even stronger.")

    return suggestions
