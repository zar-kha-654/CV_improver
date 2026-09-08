import os
import json
import streamlit as st
from pypdf import PdfReader
from openai import OpenAI


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="CV Match AI",
    page_icon="📄",
    layout="wide"
)


# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #666;
    font-size: 18px;
    margin-bottom: 35px;
}

.score-box {
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    background-color: #f5f5f5;
    margin-bottom: 20px;
}

.score {
    font-size: 55px;
    font-weight: bold;
}

.section {
    padding: 10px 0;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">📄 CV Match AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Analyze your resume against any job description using AI'
    '</div>',
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# API KEY
# ---------------------------------------------------------

st.sidebar.title("⚙️ Settings")

api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    help="Enter your OpenAI API key."
)

if not api_key:
    st.sidebar.info(
        "Enter your OpenAI API key to analyze your resume."
    )


# ---------------------------------------------------------
# RESUME UPLOAD
# ---------------------------------------------------------

st.header("1️⃣ Upload Your Resume")

uploaded_file = st.file_uploader(
    "Upload your resume in PDF format",
    type=["pdf"]
)


# ---------------------------------------------------------
# JOB DESCRIPTION
# ---------------------------------------------------------

st.header("2️⃣ Enter Job Requirements")

job_description = st.text_area(
    "Paste the job description here",
    height=300,
    placeholder="""
Example:

We are looking for a Python Developer.

Requirements:
- Strong Python programming skills
- Experience with FastAPI
- Knowledge of SQL databases
- Experience with Git and GitHub
- Good understanding of REST APIs
- Bachelor's degree in Computer Science
"""
)


# ---------------------------------------------------------
# EXTRACT PDF TEXT
# ---------------------------------------------------------

def extract_resume_text(pdf_file):

    reader = PdfReader(pdf_file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# ---------------------------------------------------------
# AI ANALYSIS
# ---------------------------------------------------------

def analyze_resume(resume_text, job_description, api_key):

    client = OpenAI(api_key=api_key)

    prompt = f"""
You are an expert recruiter, ATS specialist, and career advisor.

Your task is to analyze a candidate's resume against a specific job description.

RESUME:
----------------
{resume_text}
----------------

JOB DESCRIPTION:
----------------
{job_description}
----------------

Analyze the candidate fairly.

Do NOT invent experience, skills, education, or qualifications that are not present in the resume.

Calculate a match score from 0 to 100 using these approximate weights:

Skills: 30%
Relevant Experience: 30%
Job Responsibilities: 20%
Education: 10%
Tools / Keywords: 10%

Return ONLY valid JSON in this exact structure:

{{
    "match_score": 0,
    "recommendation": "Strong Match / Moderate Match / Weak Match",

    "summary": "Short explanation of the overall match.",

    "matching_skills": [
        "skill 1",
        "skill 2"
    ],

    "missing_skills": [
        "skill 1",
        "skill 2"
    ],

    "matching_experience": [
        "Relevant experience from resume"
    ],

    "missing_experience": [
        "Experience requirement not demonstrated in resume"
    ],

    "education_match": "Explanation of education match.",

    "matching_keywords": [
        "keyword 1",
        "keyword 2"
    ],

    "missing_keywords": [
        "keyword 1",
        "keyword 2"
    ],

    "cv_changes": [
        "Specific change that should be made to the CV"
    ],

    "improvement_plan": [
        "Skill or experience the candidate should work on"
    ],

    "ats_tips": [
        "Specific ATS optimization suggestion"
    ]
}}

Be specific and practical.

For CV changes, do not tell the candidate to lie or add experience they do not have.

If a job requirement is not demonstrated in the resume, clearly say that it is missing rather than assuming the candidate has it.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are an expert recruitment and CV analysis assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    result = response.choices[0].message.content

    return json.loads(result)


# ---------------------------------------------------------
# ANALYZE BUTTON
# ---------------------------------------------------------

if st.button(
    "🚀 Analyze My CV",
    type="primary",
    use_container_width=True
):

    if not api_key:

        st.error(
            "Please enter your OpenAI API key in the sidebar."
        )

    elif not uploaded_file:

        st.error(
            "Please upload your resume first."
        )

    elif not job_description.strip():

        st.error(
            "Please enter the job description."
        )

    else:

        with st.spinner(
            "🤖 AI is analyzing your resume..."
        ):

            try:

                resume_text = extract_resume_text(
                    uploaded_file
                )

                if not resume_text.strip():

                    st.error(
                        "Could not extract text from this PDF. "
                        "Try uploading a text-based PDF."
                    )

                    st.stop()

                result = analyze_resume(
                    resume_text,
                    job_description,
                    api_key
                )

                st.session_state["analysis"] = result

            except Exception as e:

                st.error(
                    f"Something went wrong: {str(e)}"
                )


# ---------------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------------

if "analysis" in st.session_state:

    result = st.session_state["analysis"]

    st.divider()

    st.header("📊 CV Analysis")

    # SCORE

    score = result.get("match_score", 0)

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "CV Match Score",
            f"{score}/100"
        )

    with col2:

        st.metric(
            "Recommendation",
            result.get(
                "recommendation",
                "N/A"
            )
        )

    with col3:

        if score >= 80:
            status = "Excellent"
        elif score >= 60:
            status = "Good"
        elif score >= 40:
            status = "Needs Improvement"
        else:
            status = "Low Match"

        st.metric(
            "Overall Fit",
            status
        )

    st.progress(
        min(max(score, 0), 100) / 100
    )

    # SUMMARY

    st.subheader("📝 Overall Summary")

    st.write(
        result.get("summary", "")
    )

    # SKILLS

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("✅ Matching Skills")

        skills = result.get(
            "matching_skills",
            []
        )

        if skills:

            for skill in skills:
                st.success(skill)

        else:
            st.info("No matching skills identified.")

    with col2:

        st.subheader("❌ Missing Skills")

        skills = result.get(
            "missing_skills",
            []
        )

        if skills:

            for skill in skills:
                st.error(skill)

        else:
            st.success(
                "No major missing skills identified."
            )

    # EXPERIENCE

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("💼 Relevant Experience")

        experience = result.get(
            "matching_experience",
            []
        )

        if experience:

            for item in experience:
                st.success(item)

        else:

            st.info(
                "No directly relevant experience identified."
            )

    with col2:

        st.subheader("⚠️ Missing Experience")

        experience = result.get(
            "missing_experience",
            []
        )

        if experience:

            for item in experience:
                st.warning(item)

        else:

            st.success(
                "No major experience gaps identified."
            )

    # EDUCATION

    st.divider()

    st.subheader("🎓 Education Match")

    st.write(
        result.get(
            "education_match",
            "No information available."
        )
    )

    # KEYWORDS

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🔑 Matching Keywords")

        keywords = result.get(
            "matching_keywords",
            []
        )

        for keyword in keywords:
            st.write(f"• {keyword}")

    with col2:

        st.subheader("🔎 Missing Keywords")

        keywords = result.get(
            "missing_keywords",
            []
        )

        for keyword in keywords:
            st.write(f"• {keyword}")

    # CV CHANGES

    st.divider()

    st.subheader("✏️ Changes Required in Your CV")

    changes = result.get(
        "cv_changes",
        []
    )

    for i, change in enumerate(changes, 1):

        st.write(
            f"**{i}.** {change}"
        )

    # IMPROVEMENT PLAN

    st.subheader(
        "📚 Skills & Experience You Should Improve"
    )

    improvements = result.get(
        "improvement_plan",
        []
    )

    for item in improvements:

        st.info(item)

    # ATS

    st.subheader(
        "🤖 ATS Optimization Tips"
    )

    ats_tips = result.get(
        "ats_tips",
        []
    )

    for tip in ats_tips:

        st.write(
            f"• {tip}"
        )

    # DOWNLOAD REPORT

    st.divider()

    report = f"""
CV MATCH AI REPORT

Match Score: {score}/100

Recommendation:
{result.get("recommendation", "")}

SUMMARY
{result.get("summary", "")}

MATCHING SKILLS
{chr(10).join("- " + x for x in result.get("matching_skills", []))}

MISSING SKILLS
{chr(10).join("- " + x for x in result.get("missing_skills", []))}

RELEVANT EXPERIENCE
{chr(10).join("- " + x for x in result.get("matching_experience", []))}

MISSING EXPERIENCE
{chr(10).join("- " + x for x in result.get("missing_experience", []))}

EDUCATION
{result.get("education_match", "")}

CV CHANGES
{chr(10).join("- " + x for x in result.get("cv_changes", []))}

IMPROVEMENT PLAN
{chr(10).join("- " + x for x in result.get("improvement_plan", []))}

ATS TIPS
{chr(10).join("- " + x for x in result.get("ats_tips", []))}
"""

    st.download_button(
        label="📥 Download Analysis Report",
        data=report,
        file_name="cv_match_report.txt",
        mime="text/plain",
        use_container_width=True
    )
