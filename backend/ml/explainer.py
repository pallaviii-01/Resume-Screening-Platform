def explain_match_score(match_result: dict, jd_text: str) -> dict:
    explanations = []
    score = match_result["final_score"]

    # Skill-by-skill explanation
    for skill in match_result["matched_skills"]:
        explanations.append({"skill": skill, "status": "matched", "icon": "✓"})
    for skill in match_result["missing_skills"]:
        explanations.append({"skill": skill, "status": "missing", "icon": "✗"})

    # Score band label
    if score >= 80:
        band = "Strong Match"
        advice = "Shortlist this candidate immediately."
    elif score >= 60:
        band = "Good Match"
        advice = "Worth an interview. Some skill gaps present."
    elif score >= 40:
        band = "Partial Match"
        advice = "Candidate needs upskilling in key areas."
    else:
        band = "Weak Match"
        advice = "Resume does not align well with this JD."

    # Skill gap roadmap
    roadmap = []
    if match_result["missing_skills"]:
        roadmap = [
            f"Learn {skill} — available free on Coursera/YouTube"
            for skill in match_result["missing_skills"][:4]
        ]

    return {
        "final_score": score,
        "band": band,
        "advice": advice,
        "skill_breakdown": explanations,
        "roadmap": roadmap,
        "score_components": {
            "semantic_similarity": f"{match_result['sbert_score']}% (40% weight)",
            "skill_match": f"{match_result['skill_match_percent']}% (40% weight)",
            "experience": f"{match_result['experience_years']} years (20% weight)"
        }
    }