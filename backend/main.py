import re
import os
import uuid
import shutil
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pdfplumber
from docx import Document
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Resume Screening API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

SKILLS_LIST = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite",
    "react", "angular", "vue", "html", "css", "tailwind",
    "fastapi", "flask", "django", "node.js", "express",
    "machine learning", "deep learning", "nlp", "computer vision",
    "scikit-learn", "tensorflow", "pytorch", "keras", "pandas", "numpy",
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "linux",
    "power bi", "tableau", "excel", "data analysis", "data visualization",
    "rest api", "graphql", "microservices", "agile", "scrum"
]

def extract_text(file_path):
    if file_path.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        return text
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    return ""

def extract_email(text):
    m = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return m.group(0) if m else ""

def extract_phone(text):
    m = re.search(r"(\+91[\-\s]?)?[6-9]\d{9}|(\+\d{1,3}[\-\s]?)?\(?\d{3}\)?[\-\s]?\d{3}[\-\s]?\d{4}", text)
    return m.group(0) if m else ""

def extract_name(text):
    skip = ["resume","curriculum","vitae","cv","profile","objective","summary",
            "education","experience","skills","projects","contact","address",
            "phone","email","linkedin","github"]
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:8]:
        if re.search(r"[@:/\\]|\d{7,}", line):
            continue
        if any(k in line.lower() for k in skip):
            continue
        if re.match(r"^[A-Za-z][A-Za-z\s\.]{2,40}$", line):
            if 1 <= len(line.split()) <= 5:
                return line
    return lines[0] if lines else "Unknown"

def extract_skills(text):
    tl = text.lower()
    return list(set([s for s in SKILLS_LIST if s in tl]))

def extract_experience_years(text):
    matches = re.findall(r"(\d+\.?\d*)\s*\+?\s*years?", text.lower())
    return max([float(m) for m in matches]) if matches else 0.0

def parse_resume(file_path):
    text = extract_text(file_path)
    return {
        "raw_text": text,
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "experience_years": extract_experience_years(text),
    }

def tfidf_score(text1, text2):
    v = TfidfVectorizer(stop_words="english", ngram_range=(1,2))
    m = v.fit_transform([text1, text2])
    return round(float(cosine_similarity(m[0:1], m[1:2])[0][0]) * 100, 2)

def keyword_score(text1, text2):
    stop = {'the','and','for','with','have','that','this','from','are','was','will','you','your'}
    w1 = set(re.findall(r'\b[a-z][a-z+#.]{1,}\b', text1.lower())) - stop
    w2 = set(re.findall(r'\b[a-z][a-z+#.]{1,}\b', text2.lower())) - stop
    return round(len(w1 & w2) / len(w2) * 100, 2) if w2 else 0.0

def skill_analysis(resume_skills, jd_text):
    jd_lower = jd_text.lower()
    jd_skills = set([s for s in SKILLS_LIST if s in jd_lower])
    resume_set = set(resume_skills)
    matched = list(resume_set & jd_skills)
    missing = list(jd_skills - resume_set)
    pct = round(len(matched) / len(jd_skills) * 100, 2) if jd_skills else 0
    return matched, missing, pct

def match_resume(parsed, jd_text):
    tf = tfidf_score(parsed["raw_text"], jd_text)
    kw = keyword_score(parsed["raw_text"], jd_text)
    matched, missing, skill_pct = skill_analysis(parsed["skills"], jd_text)
    exp = parsed["experience_years"]
    exp_score = min((exp / 2.0) * 100, 100)
    final = round(tf*0.20 + kw*0.20 + skill_pct*0.40 + exp_score*0.20, 2)
    return {
        "candidate_name": parsed["name"],
        "email": parsed["email"],
        "tfidf_score": tf,
        "sbert_score": kw,
        "skill_match_percent": skill_pct,
        "matched_skills": matched,
        "missing_skills": missing,
        "experience_years": exp,
        "final_score": final,
    }

def anonymize(parsed):
    p = parsed.copy()
    p["name"] = "Candidate"
    p["email"] = "hidden@anonymous.com"
    p["phone"] = "XXXXXXXXXX"
    return p

@app.get("/")
def root():
    return {"message": "Resume Screening API is running ✅"}

@app.post("/parse-resume")
async def api_parse(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["pdf","docx"]:
        raise HTTPException(400, "Only PDF and DOCX allowed")
    path = f"{UPLOAD_DIR}/{uuid.uuid4()}.{ext}"
    with open(path,"wb") as f: shutil.copyfileobj(file.file, f)
    result = parse_resume(path)
    os.remove(path)
    result.pop("raw_text", None)
    return result

@app.post("/match")
async def api_match(file: UploadFile = File(...), jd_text: str = Form(...)):
    ext = file.filename.split(".")[-1].lower()
    path = f"{UPLOAD_DIR}/{uuid.uuid4()}.{ext}"
    with open(path,"wb") as f: shutil.copyfileobj(file.file, f)
    parsed = parse_resume(path)
    result = match_resume(parsed, jd_text)
    os.remove(path)
    return result

@app.post("/rank-candidates")
async def api_rank(files: list[UploadFile] = File(...), jd_text: str = Form(...)):
    parsed_list, paths = [], []
    for file in files:
        ext = file.filename.split(".")[-1].lower()
        path = f"{UPLOAD_DIR}/{uuid.uuid4()}.{ext}"
        with open(path,"wb") as f: shutil.copyfileobj(file.file, f)
        paths.append(path)
        parsed_list.append(parse_resume(path))
    ranked = sorted([match_resume(p, jd_text) for p in parsed_list], key=lambda x: x["final_score"], reverse=True)
    for p in paths: os.remove(p)
    return {"total_candidates": len(ranked), "ranked_candidates": ranked}

@app.post("/rank-candidates-blind")
async def api_rank_blind(files: list[UploadFile] = File(...), jd_text: str = Form(...)):
    parsed_list, paths = [], []
    for file in files:
        ext = file.filename.split(".")[-1].lower()
        path = f"{UPLOAD_DIR}/{uuid.uuid4()}.{ext}"
        with open(path,"wb") as f: shutil.copyfileobj(file.file, f)
        paths.append(path)
        parsed_list.append(anonymize(parse_resume(path)))
    ranked = sorted([match_resume(p, jd_text) for p in parsed_list], key=lambda x: x["final_score"], reverse=True)
    for p in paths: os.remove(p)
    return {"mode": "bias-free", "total": len(ranked), "ranked_candidates": ranked}
