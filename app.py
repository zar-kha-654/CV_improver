import json
import streamlit as st
from pypdf import PdfReader
from groq import Groq


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="CV Improver AI",
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

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">📄 CV Improver AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Analyze your resume against a job description and discover '
    'exactly how to improve your CV'
    '</div>',
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# API KEY
# ---------------------------------------------------------

st.sidebar.title("⚙️ Settings")

api_key = st.sidebar.text_input(
    "Groq API Key",
    type="password",
    help="Enter your Groq API key."
)

if not api_key:
    st.sidebar.info(
        "Enter your Groq API key to analyze your CV."
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

We are looking for a Junior Machine Learning Engineer.

Requirements:
- Strong Python programming skills
- Knowledge of Machine Learning
- Experience with NumPy and Pandas
- Knowledge of Scikit-learn
- Understanding of SQL
- Experience with Git and GitHub
- Understanding of REST APIs
- Bachelor's degree in Computer Science
"""
)


# ---------------------------------------------------------
# EXTRACT TEXT FROM PDF
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

    client = Groq(api_key=api_key)

    prompt = f"""
You are an expert recruiter, ATS specialist, career advisor,
and resume reviewer.

Your task is to compare a candidate's resume with a specific
job description.

IMPORTANT RULES:

1. Do NOT invent skills, experience, education, certifications,
   projects, or achievements.
2. Only consider information actually present in the resume.
3. Clearly identify requirements that are missing.
4. Distinguish between required qualifications and preferred
   qualifications.
5. Give practical recommendations that the candidate can
   realistically act on.
6. Never recommend lying or falsely adding experience.
7. Evaluate the resume based on relevance to THIS specific job.

RESUME:
----------------
{resume_text}
----------------

JOB DESCRIPTION:
----------------
{job_description}
----------------

Calculate a CV match score from 0 to 100.

Use these approximate weights:

Skills: 30%
Relevant Experience: 30%
Job Responsibilities: 20%
Education: 10%
Tools and Keywords: 10%

Return ONLY valid JSON.

Use exactly this structure:

{{
    "match_score": 0,

    "recommendation": "Strong Match / Moderate Match / Weak Match",

    "summary": "Short explanation of the candidate's overall suitability.",

    "matching_skills": [
        "Skills from the resume that match the job"
    ],

    "missing_skills": [
        "Important skills required by the job that are not demonstrated"
    ],

    "matching_experience": [
        "Relevant experience demonstrated in the resume"
    ],

    "missing_experience": [
        "Relevant experience required by the job but not demonstrated"
    ],

    "education_match": "Explain whether the candidate's education matches the requirement.",

    "matching_keywords": [
        "Important job-related keywords already present in the CV"
    ],

    "missing_keywords": [
        "Important job-related keywords missing from the CV"
    ],

    "cv_changes": [
        "Specific changes the candidate should make to their CV"
    ],

    "improvement_plan": [
        "Skills, projects, certifications, or experience the candidate should develop"
    ],

    "ats_tips": [
        "Specific ATS optimization recommendations"
    ]
}}

Be specific.

For example, instead of saying:

"Improve your Python skills."

Say:

"Add specific Python projects to the Projects section and
mention the Python libraries used, such as Pandas or NumPy,
if you have actually used them."

Do not recommend adding a technology unless the candidate
actually has experience with it.
"""


    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        temperature=0.2,

        response_format={
            "type": "json_object"
        },

        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert recruitment, ATS, "
                    "and career analysis assistant."
                )
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
            "Please enter your Groq API key in the sidebar."
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
            "🤖 AI is analyzing your CV..."
        ):

            try:

                resume_text = extract_resume_text(
                    uploaded_file
                )

                if not resume_text.strip():

                    st.error(
                        "Could not extract text from this PDF. "
                        "Please upload a text-based PDF."
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


    # -----------------------------------------------------
    # SCORE
    # -----------------------------------------------------

    score = result.get(
        "match_score",
        0
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


    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    st.subheader("📝 Overall Summary")

    st.write(
        result.get(
            "summary",
            ""
        )
    )


    # -----------------------------------------------------
    # SKILLS
    # -----------------------------------------------------

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

            st.info(
                "No matching skills identified."
            )


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


    # -----------------------------------------------------
    # EXPERIENCE
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # EDUCATION
    # -----------------------------------------------------

    st.divider()

    st.subheader("🎓 Education Match")

    st.write(
        result.get(
            "education_match",
            "No information available."
        )
    )


    # -----------------------------------------------------
    # KEYWORDS
    # -----------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        st.subheader("🔑 Matching Keywords")

        keywords = result.get(
            "matching_keywords",
            []
        )

        for keyword in keywords:

            st.write(
                f"• {keyword}"
            )


    with col2:

        st.subheader("🔎 Missing Keywords")

        keywords = result.get(
            "missing_keywords",
            []
        )

        for keyword in keywords:

            st.write(
                f"• {keyword}"
            )


    # -----------------------------------------------------
    # CV CHANGES
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "✏️ Changes Required in Your CV"
    )

    changes = result.get(
        "cv_changes",
        []
    )

    if changes:

        for i, change in enumerate(
            changes,
            1
        ):

            st.write(
                f"**{i}.** {change}"
            )

    else:

        st.info(
            "No major CV changes identified."
        )


    # -----------------------------------------------------
    # IMPROVEMENT PLAN
    # -----------------------------------------------------

    st.subheader(
        "📚 Skills & Experience to Improve"
    )

    improvements = result.get(
        "improvement_plan",
        []
    )

    if improvements:

        for item in improvements:

            st.info(item)

    else:

        st.info(
            "No additional improvements identified."
        )


    # -----------------------------------------------------
    # ATS TIPS
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # DOWNLOAD REPORT
    # -----------------------------------------------------

    st.divider()

    report = f"""
CV IMPROVER AI REPORT
=====================

Match Score: {score}/100

Recommendation:
{result.get("recommendation", "")}


SUMMARY
-------
{result.get("summary", "")}


MATCHING SKILLS
---------------
{chr(10).join("- " + x for x in result.get("matching_skills", []))}


MISSING SKILLS
--------------
{chr(10).join("- " + x for x in result.get("missing_skills", []))}


RELEVANT EXPERIENCE
-------------------
{chr(10).join("- " + x for x in result.get("matching_experience", []))}


MISSING EXPERIENCE
------------------
{chr(10).join("- " + x for x in result.get("missing_experience", []))}


EDUCATION
---------
{result.get("education_match", "")}


MATCHING KEYWORDS
-----------------
{chr(10).join("- " + x for x in result.get("matching_keywords", []))}


MISSING KEYWORDS
----------------
{chr(10).join("- " + x for x in result.get("missing_keywords", []))}


CV CHANGES
----------
{chr(10).join("- " + x for x in result.get("cv_changes", []))}


IMPROVEMENT PLAN
----------------
{chr(10).join("- " + x for x in result.get("improvement_plan", []))}


ATS TIPS
--------
{chr(10).join("- " + x for x in result.get("ats_tips", []))}
"""


    st.download_button(

        label="📥 Download Analysis Report",

        data=report,

        file_name="cv_improver_report.txt",

        mime="text/plain",

        use_container_width=True
    )
