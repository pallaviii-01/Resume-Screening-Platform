import re
import pdfplumber
from docx import Document
import spacy

nlp = None

def get_nlp():
    global nlp
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")
    return nlp


SKILLS_LIST = [
    "python","java","javascript","typescript","c++","sql",
    "react","angular","vue","html","css",
    "fastapi","flask","django",
    "machine learning","deep learning","nlp",
    "scikit-learn","tensorflow","pytorch",
    "pandas","numpy","aws","azure","docker","git"
]


def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text


def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Only PDF and DOCX supported")


def extract_email(text):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else ""


def extract_phone(text):
    match = re.search(r"(\+91[\-\s]?)?[6-9]\d{9}", text)
    return match.group(0) if match else ""


def extract_name(text):
    doc = get_nlp()(text[:500])
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return lines[0] if lines else "Unknown"


def extract_skills(text):
    text = text.lower()
    return list(set(skill for skill in SKILLS_LIST if skill in text))


def extract_education(text):
    degrees = ["b.tech","btech","m.tech","mba","bca","mca","phd","bachelor","master"]
    lines = text.split("\n")
    return [line for line in lines if any(d in line.lower() for d in degrees)][:3]


def extract_experience_years(text):
    matches = re.findall(r"(\d+\.?\d*)\s*\+?\s*years?", text.lower())
    if matches:
        return max(float(x) for x in matches)
    return 0.0


def parse_resume(file_path):
    text = extract_text(file_path)

    return {
        "raw_text": text,
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience_years": extract_experience_years(text)
    }
