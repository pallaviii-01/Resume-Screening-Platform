# AI-Powered Resume Screening & Hiring Analytics Platform

An end-to-end intelligent recruitment platform that automates resume screening, ranks candidates against job descriptions, and provides hiring analytics dashboards using NLP and Machine Learning.

---

# 🚀 Project Overview

Companies receive hundreds of resumes for a single role. Manual screening is slow, inconsistent, and inefficient.

This platform solves that problem by using AI to:

- Parse resumes automatically
- Compare resumes with job descriptions
- Rank candidates intelligently
- Detect missing skills
- Provide ATS-style scoring
- Generate recruiter analytics dashboards
- Support fair / bias-free hiring

---

# 🎯 Problem Statement

HR teams face challenges such as:

- Manual resume shortlisting
- Time-consuming hiring process
- Difficulty matching resumes to JD requirements
- Inconsistent evaluation
- Missing hiring insights
- Unfair screening bias

This project builds an AI system to automate the first stage of recruitment.

---

# 💡 Proposed Solution

Build a smart web platform with two user panels:

## 👨‍💼 Recruiter Panel

- Upload Job Description
- Upload multiple resumes (PDF / DOCX)
- Get ranked candidates
- View skill match %
- View missing skills
- Shortlist top candidates
- Download results

## 👨‍🎓 Candidate / Student Panel

- Upload resume
- Paste target job description
- Get ATS score
- Resume improvement suggestions
- Skill gap roadmap
- Recommended skills to learn

---

# 🤖 Core AI / ML Features

## 1️⃣ Resume Parsing (NLP)

Extract:

- Name
- Email
- Phone
- Skills
- Education
- Experience
- Projects

### Technologies Used:

- SpaCy
- Regex
- pdfplumber
- python-docx

---

## 2️⃣ Job Description Matching Engine

Compare resume with JD.

### Output:

- Match Score (0–100%)
- Relevant skills matched
- Missing skills
- Candidate suitability score

### Methods:

### Basic:
- TF-IDF + Cosine Similarity

### Advanced:
- Sentence-BERT Embeddings

---

## 3️⃣ Candidate Ranking Model

Rank multiple resumes using:

- Skill Match
- Experience
- Semantic Match
- Education relevance
- Certifications

---

## 4️⃣ ATS Resume Score

Evaluate resume based on:

- Keyword optimization
- Readability
- Relevance
- Skills match
- Formatting quality

---

## 5️⃣ Hiring Analytics Dashboard

Provides:

- Total applicants
- Top skills available
- Average match score
- Shortlisting funnel
- Candidate distribution
- Hiring trends

---

# 🌟 Unique Features

## ✅ Explainable Match Score

Instead of just score:

Example:

- Python ✔
- SQL ✔
- AWS ✘

---

## ✅ Skill Gap Roadmap

Example:

To qualify for Data Analyst role learn:

- SQL Joins
- Excel
- Tableau
- Power BI

---

## ✅ Bias-Free Mode

Hide:

- Name
- Gender hints
- Photo
- Personal identifiers

Only skill-based ranking.

---

## ✅ Placement Analytics for Colleges

Faculty Dashboard:

- Placement readiness %
- Department performance
- Common missing skills
- Student employability score

---

## ✅ AI Resume Suggestions

Suggest:

- Better keywords
- Better projects section
- Better summary lines

---

# 🛠️ Tech Stack

## Backend

- Python
- FastAPI

## Machine Learning / NLP

- Pandas
- NumPy
- Scikit-learn
- SpaCy
- Sentence Transformers

## Resume Extraction

- pdfplumber
- python-docx
- PyMuPDF

## Frontend
- Streamlit (Fast Development)


## Database

-------

## Deployment

- Render (Backend)
- Streamlit Cloud / Vercel (Frontend)

---

# 📁 Project Structure

```bash
resume-screening-platform/
│── backend/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   └── ml/
│       ├── parser.py
│       ├── matcher.py
│       └── explainer.py
│
│── frontend/
│   └── app.py
│
│── data/
│   ├── sample_resumes/
│   └── uploads/
│
│── requirements.txt
│── README.md
