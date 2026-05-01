import re
import pdfplumber
from docx import Document

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

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text(file_path: str) -> str:
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Only PDF and DOCX files are supported")

def extract_email(text: str) -> str:
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else ""

def extract_phone(text: str) -> str:
    match = re.search(
        r"(\+91[\-\s]?)?[6-9]\d{9}|(\+\d{1,3}[\-\s]?)?\(?\d{3}\)?[\-\s]?\d{3}[\-\s]?\d{4}",
        text
    )
    return match.group(0) if match else ""

def extract_name(text: str) -> str:
    skip_keywords = [
        "resume", "curriculum", "vitae", "cv", "profile", "objective",
        "summary", "education", "experience", "skills", "projects",
        "contact", "address", "phone", "email", "linkedin", "github"
    ]
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:8]:
        line_lower = line.lower()
        if re.search(r"[@:/\\]|\d{7,}", line):
            continue
        if any(kw in line_lower for kw in skip_keywords):
            continue
        if re.match(r"^[A-Za-z][A-Za-z\s\.]{2,40}$", line):
            words = line.split()
            if 1 <= len(words) <= 5:
                return line
    return lines[0] if lines else "Unknown"

def extract_skills(text: str) -> list:
    text_lower = text.lower()
    found = [skill for skill in SKILLS_LIST if skill in text_lower]
    return list(set(found))

def extract_education(text: str) -> list:
    education = []
    degrees = [
        "b.tech", "btech", "b.e", "m.tech", "mtech", "mca", "bca",
        "bachelor", "master", "phd", "b.sc", "m.sc", "mba"
    ]
    lines = text.split("\n")
    for line in lines:
        if any(deg in line.lower() for deg in degrees):
            education.append(line.strip())
    return education[:3]

def extract_experience_years(text: str) -> float:
    matches = re.findall(r"(\d+\.?\d*)\s*\+?\s*years?", text.lower())
    if matches:
        return max(float(m) for m in matches)
    return 0.0

def parse_resume(file_path: str) -> dict:
    text = extract_text(file_path)
    return {
        "raw_text": text,
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience_years": extract_experience_years(text),
    }
