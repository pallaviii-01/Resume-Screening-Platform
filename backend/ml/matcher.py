from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np

# Load once at startup (takes ~5 seconds first time)
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

# ── Basic match: TF-IDF cosine similarity ────────────────────────
def tfidf_match(resume_text: str, jd_text: str) -> float:
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(score) * 100, 2)

# ── Advanced match: Sentence-BERT semantic similarity ────────────
def sbert_match(resume_text: str, jd_text: str) -> float:
    embeddings = sbert_model.encode([resume_text, jd_text])
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return round(float(score) * 100, 2)

# ── Skill gap analysis ────────────────────────────────────────────
def analyze_skills(resume_skills: list, jd_text: str) -> dict:
    from backend.ml.parser import SKILLS_LIST
    jd_lower = jd_text.lower()

    # Skills required by the JD
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

# ── Weighted final score ──────────────────────────────────────────
def calculate_final_score(
    sbert_score: float,
    skill_score: float,
    experience_years: float,
    required_experience: float = 2.0
) -> float:
    # Weights: semantic 40%, skills 40%, experience 20%
    exp_score = min((experience_years / max(required_experience, 1)) * 100, 100)
    final = (sbert_score * 0.40) + (skill_score * 0.40) + (exp_score * 0.20)
    return round(final, 2)

# ── Main match function ───────────────────────────────────────────
def match_resume_to_jd(parsed_resume: dict, jd_text: str) -> dict:
    tfidf_score = tfidf_match(parsed_resume["raw_text"], jd_text)
    sbert_score = sbert_match(parsed_resume["raw_text"], jd_text)
    skill_analysis = analyze_skills(parsed_resume["skills"], jd_text)
    final_score = calculate_final_score(
        sbert_score,
        skill_analysis["skill_match_percent"],
        parsed_resume["experience_years"]
    )

    return {
        "candidate_name": parsed_resume["name"],
        "email": parsed_resume["email"],
        "tfidf_score": tfidf_score,
        "sbert_score": sbert_score,
        "skill_match_percent": skill_analysis["skill_match_percent"],
        "matched_skills": skill_analysis["matched_skills"],
        "missing_skills": skill_analysis["missing_skills"],
        "experience_years": parsed_resume["experience_years"],
        "final_score": final_score,
    }

# ── Rank multiple resumes ─────────────────────────────────────────
def rank_candidates(parsed_resumes: list, jd_text: str) -> list:
    results = [match_resume_to_jd(r, jd_text) for r in parsed_resumes]
    return sorted(results, key=lambda x: x["final_score"], reverse=True)