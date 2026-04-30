import streamlit as st
import requests
import plotly.express as px
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Resume Screening Platform", layout="wide")
st.title("AI-Powered Resume Screening Platform")

tab1, tab2 = st.tabs(["Recruiter Panel", "Student / ATS Score"])

# ══════════════════════════════════════════════════════════════════
# TAB 1 — RECRUITER PANEL
# ══════════════════════════════════════════════════════════════════
with tab1:
    st.header("Rank Candidates for a Job")

    jd_text = st.text_area("Paste Job Description here", height=200,
                            placeholder="e.g. We are looking for a Data Analyst with Python, SQL, Power BI...")

    uploaded_files = st.file_uploader(
        "Upload Resumes (PDF or DOCX)", type=["pdf", "docx"], accept_multiple_files=True
    )

    if st.button("Rank Candidates") and uploaded_files and jd_text:
        with st.spinner("Analyzing resumes..."):
            files = [("files", (f.name, f.read(), f.type)) for f in uploaded_files]
            data = {"jd_text": jd_text}
            response = requests.post(f"{API_URL}/rank-candidates", files=files, data=data)

        if response.status_code == 200:
            result = response.json()
            candidates = result["ranked_candidates"]

            st.success(f"Ranked {result['total_candidates']} candidates")

            # ── Summary table ──────────────────────────────────────
            st.subheader("Candidate Rankings")
            df = pd.DataFrame([{
                "Rank": i+1,
                "Name": c["candidate_name"],
                "Email": c["email"],
                "Final Score": f"{c['final_score']}%",
                "Skill Match": f"{c['skill_match_percent']}%",
                "Experience": f"{c['experience_years']} yrs",
                "Missing Skills": ", ".join(c["missing_skills"][:3]) or "None"
            } for i, c in enumerate(candidates)])
            st.dataframe(df, use_container_width=True)

            # ── Bar chart ──────────────────────────────────────────
            st.subheader("Score Comparison")
            chart_df = pd.DataFrame({
                "Candidate": [c["candidate_name"] for c in candidates],
                "Final Score": [c["final_score"] for c in candidates],
                "Skill Match": [c["skill_match_percent"] for c in candidates],
                "Semantic Score": [c["sbert_score"] for c in candidates],
            })
            fig = px.bar(chart_df, x="Candidate",
                         y=["Final Score", "Skill Match", "Semantic Score"],
                         barmode="group", title="Candidate Score Breakdown")
            st.plotly_chart(fig, use_container_width=True)

            # ── Per-candidate detail ───────────────────────────────
            st.subheader("Detailed Breakdown")
            for i, c in enumerate(candidates):
                with st.expander(f"#{i+1} {c['candidate_name']} — {c['final_score']}%"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Final Score", f"{c['final_score']}%")
                        st.metric("Skill Match", f"{c['skill_match_percent']}%")
                        st.metric("Experience", f"{c['experience_years']} years")
                    with col2:
                        st.write("**Matched Skills**")
                        st.success(", ".join(c["matched_skills"]) or "None found")
                        st.write("**Missing Skills**")
                        st.error(", ".join(c["missing_skills"]) or "None — great match!")
        else:
            st.error(f"API Error: {response.text}")

# ══════════════════════════════════════════════════════════════════
# TAB 2 — STUDENT / ATS SCORE
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.header("Check Your ATS Score")

    jd_input = st.text_area("Paste the Job Description you're applying for", height=150)
    resume_file = st.file_uploader("Upload Your Resume", type=["pdf", "docx"], key="student")

    if st.button("Get My Score") and resume_file and jd_input:
        with st.spinner("Analyzing your resume..."):
            files = [("file", (resume_file.name, resume_file.read(), resume_file.type))]
            data = {"jd_text": jd_input}
            response = requests.post(f"{API_URL}/match", files=files, data=data)

        if response.status_code == 200:
            result = response.json()

            st.subheader(f"Your ATS Score: {result['final_score']}%")
            col1, col2, col3 = st.columns(3)
            col1.metric("Semantic Match", f"{result['sbert_score']}%")
            col2.metric("Skill Match", f"{result['skill_match_percent']}%")
            col3.metric("Experience", f"{result['experience_years']} yrs")

            st.write("**Skills you have that match:**")
            if result["matched_skills"]:
                st.success(", ".join(result["matched_skills"]))
            else:
                st.warning("No matching skills detected")

            st.write("**Skills you're missing (learn these!):**")
            if result["missing_skills"]:
                st.error(", ".join(result["missing_skills"]))
                st.info(f"Skill Gap Roadmap: To qualify for this role, focus on learning: {', '.join(result['missing_skills'][:5])}")
            else:
                st.success("You have all the required skills — excellent match!")


# Add this as Tab 3 in your existing app.py

tab1, tab2, tab3 = st.tabs(["Recruiter Panel", "Student / ATS Score", "College Dashboard"])

with tab3:
    st.header("Placement Readiness Dashboard")
    st.caption("Faculty view — upload your students' resumes to analyze department-wide readiness")

    dept = st.selectbox("Department", ["Computer Engineering", "IT", "Data Science", "Electronics"])
    target_jd = st.text_area("Target Job Description (e.g. Data Analyst)", height=120)
    student_resumes = st.file_uploader(
        "Upload All Student Resumes", type=["pdf", "docx"],
        accept_multiple_files=True, key="college"
    )

    if st.button("Analyze Batch") and student_resumes and target_jd:
        with st.spinner(f"Analyzing {len(student_resumes)} students..."):
            files = [("files", (f.name, f.read(), f.type)) for f in student_resumes]
            data = {"jd_text": target_jd}
            response = requests.post(f"{API_URL}/rank-candidates", files=files, data=data)

        if response.status_code == 200:
            result = response.json()
            candidates = result["ranked_candidates"]

            # ── Summary metrics ────────────────────────────────────
            scores = [c["final_score"] for c in candidates]
            avg_score = round(sum(scores) / len(scores), 1)
            ready_count = sum(1 for s in scores if s >= 70)

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Students", len(candidates))
            col2.metric("Avg Match Score", f"{avg_score}%")
            col3.metric("Placement Ready (≥70%)", ready_count)

            # ── Score distribution ─────────────────────────────────
            import plotly.express as px, pandas as pd

            df = pd.DataFrame({"Student": [c["candidate_name"] for c in candidates],
                               "Score": [c["final_score"] for c in candidates]})
            fig1 = px.histogram(df, x="Score", nbins=10,
                                title="Score Distribution Across Students",
                                color_discrete_sequence=["#534AB7"])
            st.plotly_chart(fig1, use_container_width=True)

            # ── Common missing skills ──────────────────────────────
            from collections import Counter
            all_missing = []
            for c in candidates:
                all_missing.extend(c["missing_skills"])

            if all_missing:
                skill_counts = Counter(all_missing).most_common(8)
                skill_df = pd.DataFrame(skill_counts, columns=["Skill", "Count"])
                fig2 = px.bar(skill_df, x="Skill", y="Count",
                              title="Most Common Missing Skills (Department Gap Analysis)",
                              color_discrete_sequence=["#D85A30"])
                st.plotly_chart(fig2, use_container_width=True)
                st.info(f"Top skill to teach in {dept}: **{skill_counts[0][0]}**")

            # ── Full student table ─────────────────────────────────
            st.subheader("Student-wise Report")
            df2 = pd.DataFrame([{
                "Student": c["candidate_name"],
                "Score": f"{c['final_score']}%",
                "Skills Matched": len(c["matched_skills"]),
                "Skills Missing": len(c["missing_skills"]),
                "Status": "Ready" if c["final_score"] >= 70 else "Needs Work"
            } for c in candidates])
            st.dataframe(df2, use_container_width=True)