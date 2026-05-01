import sys
import traceback

try:
    from fastapi import FastAPI, UploadFile, File, Form, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import shutil, os, uuid
    from backend.ml.parser import parse_resume
    from backend.ml.matcher import rank_candidates, match_resume_to_jd
    from backend.ml.bias_filter import anonymize_resume
    from backend.ml.explainer import explain_match_score
    print("✅ All imports successful")
except Exception as e:
    print("❌ IMPORT ERROR:", str(e))
    traceback.print_exc()
    sys.exit(1)

app = FastAPI(title="Resume Screening API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def root():
    return {"message": "Resume Screening API is running ✅"}

@app.post("/parse-resume")
async def parse_resume_endpoint(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX allowed")
    file_path = f"{UPLOAD_DIR}/{uuid.uuid4()}.{ext}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    result = parse_resume(file_path)
    os.remove(file_path)
    return result

@app.post("/match")
async def match_endpoint(
    file: UploadFile = File(...),
    jd_text: str = Form(...)
):
    ext = file.filename.split(".")[-1].lower()
    file_path = f"{UPLOAD_DIR}/{uuid.uuid4()}.{ext}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    parsed = parse_resume(file_path)
    result = match_resume_to_jd(parsed, jd_text)
    explanation = explain_match_score(result, jd_text)
    os.remove(file_path)
    return {**result, "explanation": explanation}

@app.post("/rank-candidates")
async def rank_candidates_endpoint(
    files: list[UploadFile] = File(...),
    jd_text: str = Form(...)
):
    parsed_list = []
    saved_paths = []
    for file in files:
        ext = file.filename.split(".")[-1].lower()
        path = f"{UPLOAD_DIR}/{uuid.uuid4()}.{ext}"
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        saved_paths.append(path)
        parsed_list.append(parse_resume(path))
    ranked = rank_candidates(parsed_list, jd_text)
    for path in saved_paths:
        os.remove(path)
    return {"total_candidates": len(ranked), "ranked_candidates": ranked}

@app.post("/rank-candidates-blind")
async def rank_blind(
    files: list[UploadFile] = File(...),
    jd_text: str = Form(...)
):
    parsed_list = []
    saved_paths = []
    for file in files:
        ext = file.filename.split(".")[-1].lower()
        path = f"{UPLOAD_DIR}/{uuid.uuid4()}.{ext}"
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        saved_paths.append(path)
        parsed = parse_resume(path)
        parsed_list.append(anonymize_resume(parsed))
    ranked = rank_candidates(parsed_list, jd_text)
    for path in saved_paths:
        os.remove(path)
    return {"mode": "bias-free", "total": len(ranked), "ranked_candidates": ranked}
