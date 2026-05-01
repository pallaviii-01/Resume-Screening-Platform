from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def tfidf_match(resume_text: str, jd_text: str) -> float:
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1,2))
    tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(score) * 100, 2)

def keyword_match(resume_text: str, jd_text: str) -> float:
    jd_words = set(re.findall(r'\b[a-z][a-z+#.]{1,}\b', jd_text.lower()))
    resume_words = set(re.findall(r'\b[a-z][a-z+#.]{1,}\b', resume_text.lower()))
    stop = {'the','and','for','with','have','that','this','from','are','was',
            'will','you','your','our','their','they','been','has','can','may'}
    jd_words -= stop
    resume_words -= stop
    if not jd_words:
        return 0.0
    overlap = len(jd_words & resume_words) / len(jd_words)
    return round(overlap * 100, 2)

def analyze_skills(resume_skills: list, jd_text: str) -> dict:
    from backend.ml.parser import SKILLS_LIST
    jd_lower = jd_text.lower()
    jd_skills = [s for s in SKILLS_LIST if s in jd_lower]
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)
    matched = list(resume_set & jd_set)
    missing = list(jd_set - resume_set)
    skill_score = (len(matched) / len(jd_set) * 100) if jd_set else 0
    return {
        "jd_required_skills": jd_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_match_percent": round(skill_score, 2)
    }

def calculate_final_score(tfidf_score, keyword_score, skill_score, experience_years, required_experience=2.0):
    exp_score = min((experience_years / max(required_experience, 1)) * 100, 100)
    final = (tfidf_score * 0.20) + (keyword_score * 0.20) + (skill_score * 0.40) + (exp_score * 0.20)
    return round(final, 2)

def match_resume_to_jd(parsed_resume: dict, jd_text: str) -> dict:
    tfidf_score = tfidf_match(parsed_resume["raw_text"], jd_text)
    kw_score = keyword_match(parsed_resume["raw_text"], jd_text)
    skill_analysis = analyze_skills(parsed_resume["skills"], jd_text)
    final_score = calculate_final_score(
        tfidf_score, kw_score,
        skill_analysis["skill_match_percent"],
        parsed_resume["experience_years"]
    )
    return {
        "candidate_name": parsed_resume["name"],
        "email": parsed_resume["email"],
        "tfidf_score": tfidf_score,
        "sbert_score": kw_score,
        "skill_match_percent": skill_analysis["skill_match_percent"],
        "matched_skills": skill_analysis["matched_skills"],
        "missing_skills": skill_analysis["missing_skills"],
        "experience_years": parsed_resume["experience_years"],
        "final_score": final_score,
    }

def rank_candidates(parsed_resumes: list, jd_text: str) -> list:
    results = [match_resume_to_jd(r, jd_text) for r in parsed_resumes]
    return sorted(results, key=lambda x: x["final_score"], reverse=True)
