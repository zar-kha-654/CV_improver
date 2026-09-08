import json
import streamlit as st
from pypdf import PdfReader
from groq import Groq


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="CV Match AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main-title {
    font-size: 46px;
    font-weight: 800;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #666666;
    margin-bottom: 35px;
}

.score-container {
    text-align: center;
    padding: 25px;
    border-radius: 15px;
    background-color: #f5f7fa;
    margin-bottom: 25px;
}

.score-number {
    font-size: 55px;
    font-weight: 800;
}

.card {
    padding: 20px;
    border-radius: 12px;
    background-color: #f8f9fa;
    margin-bottom: 15px;
}

.small-text {
    color: #666666;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">📄 CV Match AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered resume analysis and job matching'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("⚙️ CV Match AI")

    st.markdown("""
    ### How it works

    **1.** Upload your resume

    **2.** Paste the job requirements

    **3.** Click Analyze CV

    **4.** Get your AI-powered match report
    """)

    st.divider()

    st.markdown("""
    ### Analysis includes

    ✅ Match Score

    ✅ Matching Skills

    ❌ Missing Skills

    💼 Experience Analysis

    🎓 Education Match

    🔑 Keywords

    ✏️ CV Improvements

    📚 Learning Plan

    🤖 ATS Tips
    """)

    st.divider()

    st.caption("CV Match AI • Powered by Groq")


# =========================================================
# GET GROQ API KEY
# =========================================================

try:

    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

except Exception:

    st.error(
        "Groq API key is not configured. "
        "Please add GROQ_API_KEY to your Streamlit Secrets."
    )

    st.stop()


# =========================================================
# CREATE GROQ CLIENT
# =========================================================

client = Groq(
    api_key=GROQ_API_KEY
)


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_resume_text(uploaded_file):

    reader = PdfReader(uploaded_file)

    text = ""

    for page_number, page in enumerate(reader.pages, start=1):

        try:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        except Exception:

            continue

    return text.strip()


# =========================================================
# AI ANALYSIS FUNCTION
# =========================================================

def analyze_resume(resume_text, job_description):

    prompt = f"""
You are an expert recruiter, ATS specialist, career coach,
and technical hiring manager.

Your task is to carefully compare a candidate's resume with
the provided job description.

IMPORTANT RULES:

1. Do NOT invent experience.
2. Do NOT assume the candidate has a skill that is not shown
   in the resume.
3. Distinguish between required qualifications and preferred
   qualifications.
4. Be honest and practical.
5. Give specific CV improvement suggestions.
6. Never tell the candidate to lie or falsely claim experience.
7. If something is missing, clearly identify it as missing.
8. Evaluate the actual relevance of the candidate's experience,
   not just keyword matching.

=========================================================
CANDIDATE RESUME
=========================================================

{resume_text}

=========================================================
JOB DESCRIPTION
=========================================================

{job_description}

=========================================================
SCORING SYSTEM
=========================================================

Calculate a match score from 0 to 100.

Use approximately:

Skills: 30%
Relevant Experience: 30%
Job Responsibilities: 20%
Education: 10%
Tools / Keywords: 10%

=========================================================
REQUIRED JSON FORMAT
=========================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "match_score": 0,

    "recommendation": "Strong Match",

    "summary": "Short but meaningful explanation of the overall match.",

    "skills_score": 0,

    "experience_score": 0,

    "responsibilities_score": 0,

    "education_score": 0,

    "keywords_score": 0,

    "matching_skills": [
        "Python",
        "Git"
    ],

    "missing_skills": [
        "Docker",
        "TensorFlow"
    ],

    "matching_experience": [
        "Specific relevant experience found in the resume"
    ],

    "missing_experience": [
        "Specific experience required by the job but not demonstrated"
    ],

    "education_match": "Explain whether the candidate's education matches the requirement.",

    "matching_keywords": [
        "Python",
        "Machine Learning"
    ],

    "missing_keywords": [
        "FastAPI",
        "Docker"
    ],

    "cv_changes": [
        "Specific change the candidate should make to their CV."
    ],

    "experience_required": [
        "Experience the candidate should gain to become a stronger candidate."
    ],

    "learning_plan": [
        "Specific skill or technology the candidate should learn."
    ],

    "ats_tips": [
        "Specific ATS optimization suggestion."
    ],

    "strengths": [
        "Major strength of the candidate."
    ],

    "weaknesses": [
        "Major weakness or gap."
    ]
}}

The recommendation must be one of:

"Strong Match"
"Good Match"
"Moderate Match"
"Weak Match"
"Very Weak Match"

Keep the analysis specific to THIS resume and THIS job.
"""


    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional recruitment AI "
                    "that produces accurate and honest resume "
                    "analysis."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2,

        response_format={
            "type": "json_object"
        }
    )


    result = response.choices[0].message.content

    return json.loads(result)


# =========================================================
# RESUME UPLOAD
# =========================================================

st.header("📄 1. Upload Your Resume")

uploaded_file = st.file_uploader(
    "Upload your resume as a PDF",
    type=["pdf"],
    help="Only PDF resumes are supported."
)


if uploaded_file:

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )


# =========================================================
# JOB REQUIREMENTS
# =========================================================

st.header("💼 2. Enter Job Requirements")

job_description = st.text_area(

    "Paste the complete job description here",

    height=300,

    placeholder="""Example:

Junior Machine Learning Engineer

We are looking for a Junior Machine Learning Engineer
to join our AI team.

Requirements:
- Bachelor's degree in Computer Science
- Strong Python programming
- Machine Learning fundamentals
- NumPy, Pandas and Scikit-learn
- SQL
- REST APIs
- Git and GitHub
- Data Structures and Algorithms
- Experience with ML projects

Preferred:
- TensorFlow or PyTorch
- LLMs and Generative AI
- Hugging Face
- Streamlit
- Docker
"""
)


# =========================================================
# ANALYZE BUTTON
# =========================================================

st.divider()

analyze_button = st.button(
    "🚀 Analyze My CV",
    type="primary",
    use_container_width=True
)


if analyze_button:

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if uploaded_file is None:

        st.error(
            "❌ Please upload your resume first."
        )

        st.stop()


    if not job_description.strip():

        st.error(
            "❌ Please enter the job requirements."
        )

        st.stop()


    # -----------------------------------------------------
    # EXTRACT RESUME
    # -----------------------------------------------------

    with st.spinner("📖 Reading your resume..."):

        resume_text = extract_resume_text(
            uploaded_file
        )


    if not resume_text:

        st.error(
            "❌ I couldn't extract text from this PDF. "
            "Please make sure your PDF contains selectable text."
        )

        st.stop()


    # -----------------------------------------------------
    # LIMIT EXTREMELY LARGE RESUMES
    # -----------------------------------------------------

    if len(resume_text) > 50000:

        resume_text = resume_text[:50000]


    # -----------------------------------------------------
    # AI ANALYSIS
    # -----------------------------------------------------

    with st.spinner(
        "🤖 AI is comparing your CV with the job requirements..."
    ):

        try:

            analysis = analyze_resume(
                resume_text,
                job_description
            )

        except json.JSONDecodeError:

            st.error(
                "❌ The AI returned an invalid analysis format. "
                "Please try again."
            )

            st.stop()

        except Exception as e:

            st.error(
                f"❌ Something went wrong: {str(e)}"
            )

            st.stop()


    # Save result

    st.session_state["analysis"] = analysis


# =========================================================
# DISPLAY RESULTS
# =========================================================

if "analysis" in st.session_state:

    analysis = st.session_state["analysis"]

    st.divider()

    st.header("📊 Your CV Match Report")


    # =====================================================
    # SCORE
    # =====================================================

    score = int(
        analysis.get("match_score", 0)
    )

    recommendation = analysis.get(
        "recommendation",
        "Unknown"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "CV Match Score",
            f"{score}/100"
        )


    with col2:

        st.metric(
            "Recommendation",
            recommendation
        )


    with col3:

        if score >= 80:

            fit = "Excellent Fit"

        elif score >= 65:

            fit = "Good Fit"

        elif score >= 50:

            fit = "Needs Improvement"

        else:

            fit = "Low Fit"


        st.metric(
            "Overall Fit",
            fit
        )


    st.progress(
        max(0, min(score, 100)) / 100
    )


    # =====================================================
    # SUMMARY
    # =====================================================

    st.subheader("📝 Overall Assessment")

    st.write(
        analysis.get(
            "summary",
            "No summary available."
        )
    )


    # =====================================================
    # SCORE BREAKDOWN
    # =====================================================

    st.subheader("📈 Score Breakdown")


    score_col1, score_col2, score_col3 = st.columns(3)


    with score_col1:

        st.metric(
            "Skills",
            f"{analysis.get('skills_score', 0)}/100"
        )

        st.metric(
            "Experience",
            f"{analysis.get('experience_score', 0)}/100"
        )


    with score_col2:

        st.metric(
            "Responsibilities",
            f"{analysis.get('responsibilities_score', 0)}/100"
        )

        st.metric(
            "Education",
            f"{analysis.get('education_score', 0)}/100"
        )


    with score_col3:

        st.metric(
            "Keywords",
            f"{analysis.get('keywords_score', 0)}/100"
        )


    # =====================================================
    # STRENGTHS
    # =====================================================

    st.divider()

    st.subheader("💪 Your Strengths")


    strengths = analysis.get(
        "strengths",
        []
    )


    if strengths:

        for strength in strengths:

            st.success(
                f"✓ {strength}"
            )

    else:

        st.info(
            "No specific strengths were identified."
        )


    # =====================================================
    # SKILLS
    # =====================================================

    st.divider()

    skill_col1, skill_col2 = st.columns(2)


    with skill_col1:

        st.subheader("✅ Matching Skills")

        matching_skills = analysis.get(
            "matching_skills",
            []
        )


        if matching_skills:

            for skill in matching_skills:

                st.success(
                    f"✓ {skill}"
                )

        else:

            st.info(
                "No matching skills identified."
            )


    with skill_col2:

        st.subheader("❌ Missing Skills")

        missing_skills = analysis.get(
            "missing_skills",
            []
        )


        if missing_skills:

            for skill in missing_skills:

                st.error(
                    f"✗ {skill}"
                )

        else:

            st.success(
                "No major missing skills identified."
            )


    # =====================================================
    # EXPERIENCE
    # =====================================================

    st.divider()

    exp_col1, exp_col2 = st.columns(2)


    with exp_col1:

        st.subheader("💼 Relevant Experience")

        matching_experience = analysis.get(
            "matching_experience",
            []
        )


        if matching_experience:

            for experience in matching_experience:

                st.success(
                    f"✓ {experience}"
                )

        else:

            st.info(
                "No directly relevant experience was identified."
            )


    with exp_col2:

        st.subheader("⚠️ Missing Experience")

        missing_experience = analysis.get(
            "missing_experience",
            []
        )


        if missing_experience:

            for experience in missing_experience:

                st.warning(
                    f"⚠ {experience}"
                )

        else:

            st.success(
                "No major experience gaps identified."
            )


    # =====================================================
    # EDUCATION
    # =====================================================

    st.divider()

    st.subheader("🎓 Education Match")

    st.info(
        analysis.get(
            "education_match",
            "No education analysis available."
        )
    )


    # =====================================================
    # KEYWORDS
    # =====================================================

    st.divider()

    keyword_col1, keyword_col2 = st.columns(2)


    with keyword_col1:

        st.subheader("🔑 Matching Keywords")

        matching_keywords = analysis.get(
            "matching_keywords",
            []
        )


        for keyword in matching_keywords:

            st.write(
                f"• {keyword}"
            )


    with keyword_col2:

        st.subheader("🔎 Missing Keywords")

        missing_keywords = analysis.get(
            "missing_keywords",
            []
        )


        for keyword in missing_keywords:

            st.write(
                f"• {keyword}"
            )


    # =====================================================
    # CV CHANGES
    # =====================================================

    st.divider()

    st.subheader("✏️ Changes Required in Your CV")


    cv_changes = analysis.get(
        "cv_changes",
        []
    )


    if cv_changes:

        for number, change in enumerate(
            cv_changes,
            start=1
        ):

            st.write(
                f"**{number}.** {change}"
            )

    else:

        st.info(
            "No specific CV changes were identified."
        )


    # =====================================================
    # EXPERIENCE TO GAIN
    # =====================================================

    st.divider()

    st.subheader(
        "💼 Experience You Should Gain"
    )


    experience_required = analysis.get(
        "experience_required",
        []
    )


    if experience_required:

        for item in experience_required:

            st.warning(
                f"📌 {item}"
            )

    else:

        st.success(
            "Your current experience appears sufficient."
        )


    # =====================================================
    # LEARNING PLAN
    # =====================================================

    st.divider()

    st.subheader(
        "📚 Recommended Learning Plan"
    )


    learning_plan = analysis.get(
        "learning_plan",
        []
    )


    if learning_plan:

        for number, item in enumerate(
            learning_plan,
            start=1
        ):

            st.info(
                f"**{number}.** {item}"
            )

    else:

        st.success(
            "No major learning gaps identified."
        )


    # =====================================================
    # WEAKNESSES
    # =====================================================

    st.divider()

    st.subheader("⚠️ Areas to Improve")


    weaknesses = analysis.get(
        "weaknesses",
        []
    )


    if weaknesses:

        for weakness in weaknesses:

            st.warning(
                f"• {weakness}"
            )

    else:

        st.success(
            "No major weaknesses identified."
        )


    # =====================================================
    # ATS TIPS
    # =====================================================

    st.divider()

    st.subheader(
        "🤖 ATS Optimization Tips"
    )


    ats_tips = analysis.get(
        "ats_tips",
        []
    )


    if ats_tips:

        for tip in ats_tips:

            st.write(
                f"🔹 {tip}"
            )

    else:

        st.info(
            "No ATS tips available."
        )


    # =====================================================
    # DOWNLOAD REPORT
    # =====================================================

    st.divider()

    st.subheader(
        "📥 Download Your Report"
    )


    def create_report(data):

        report = []

        report.append("CV MATCH AI REPORT")
        report.append("=" * 50)

        report.append(
            f"\nMATCH SCORE: "
            f"{data.get('match_score', 0)}/100"
        )

        report.append(
            f"\nRECOMMENDATION: "
            f"{data.get('recommendation', '')}"
        )

        report.append(
            "\n\nOVERALL ASSESSMENT"
        )

        report.append(
            data.get("summary", "")
        )


        report.append(
            "\n\nSTRENGTHS"
        )

        for item in data.get("strengths", []):

            report.append(
                f"- {item}"
            )


        report.append(
            "\n\nMATCHING SKILLS"
        )

        for item in data.get("matching_skills", []):

            report.append(
                f"- {item}"
            )


        report.append(
            "\n\nMISSING SKILLS"
        )

        for item in data.get("missing_skills", []):

            report.append(
                f"- {item}"
            )


        report.append(
            "\n\nRELEVANT EXPERIENCE"
        )

        for item in data.get("matching_experience", []):

            report.append(
                f"- {item}"
            )


        report.append(
            "\n\nMISSING EXPERIENCE"
        )

        for item in data.get("missing_experience", []):

            report.append(
                f"- {item}"
            )


        report.append(
            "\n\nEDUCATION MATCH"
        )

        report.append(
            data.get("education_match", "")
        )


        report.append(
            "\n\nMATCHING KEYWORDS"
        )

        for item in data.get("matching_keywords", []):

            report.append(
                f"- {item}"
            )


        report.append(
            "\n\nMISSING KEYWORDS"
        )

        for item in data.get("missing_keywords", []):

            report.append(
                f"- {item}"
            )


        report.append(
            "\n\nCV CHANGES REQUIRED"
        )

        for item in data.get("cv_changes", []):

            report.append(
                f"- {item}"
            )


        report.append(
            "\n\nEXPERIENCE TO GAIN"
        )

        for item in data.get("experience_required", []):

            report.append(
                f"- {item}"
            )


        report.append(
            "\n\nLEARNING PLAN"
        )

        for item in data.get("learning_plan", []):

            report.append(
                f"- {item}"
            )


        report.append(
            "\n\nATS TIPS"
        )

        for item in data.get("ats_tips", []):

            report.append(
                f"- {item}"
            )


        return "\n".join(report)


    report = create_report(
        analysis
    )


    st.download_button(

        label="📄 Download Analysis Report",

        data=report,

        file_name="CV_Match_AI_Report.txt",

        mime="text/plain",

        use_container_width=True
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "CV Match AI analyzes your resume against the provided "
    "job description. AI-generated recommendations should "
    "be reviewed before making changes to your CV."
)
