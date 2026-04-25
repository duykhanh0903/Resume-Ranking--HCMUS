import streamlit as st
import streamlit_shadcn_ui as ui
import pandas as pd
import requests

# ==========================================
# 0. PAGE CONFIG & ROUTER
# ==========================================
st.set_page_config(page_title="RecruitAI", layout="wide", initial_sidebar_state="expanded")

# Khởi tạo state để theo dõi trang hiện tại
if 'current_page' not in st.session_state:
    st.session_state.current_page = "analyzer"

def change_page(page_name):
    st.session_state.current_page = page_name

# Vẫn giữ lại 1 chút CSS cực nhỏ cho avatar/profile text nếu cần
st.markdown("""
<style>
    .profile-name { font-size: 1.2rem; font-weight: bold; margin-bottom: 0;}
    .profile-sub { font-size: 0.9rem; color: #64748b; margin-top: 0;}
    .block-container { padding-top: 4rem; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("### 🧬 RecruitAI")
    st.caption("Enterprise Plan")
    st.markdown("---")
    
    # Điều hướng trang
    if ui.button("Dashboard", variant="ghost" if st.session_state.current_page != "dashboard" else "secondary", key="nav_dash"):
        change_page("dashboard")
        st.rerun()
        
    if ui.button("Resume Analyzer", variant="ghost" if st.session_state.current_page != "analyzer" else "secondary", key="nav_analyzer"):
        change_page("analyzer")
        st.rerun()

    if ui.button("Candidate Ranking", variant="ghost" if st.session_state.current_page != "ranking" else "secondary", key="nav_ranking"):
        change_page("ranking")
        st.rerun()

    if ui.button("Job Search", variant="ghost" if st.session_state.current_page != "job_search" else "secondary", key="nav_jobsearch"):
        change_page("job_search")
        st.rerun()

    if ui.button("Resume Builder", variant="ghost" if st.session_state.current_page != "resume_builder" else "secondary", key="nav_builder"):
        change_page("resume_builder")
        st.rerun()
        
    if ui.button("Analytics & Ethics", variant="ghost" if st.session_state.current_page != "ethics" else "secondary", key="nav_ethics"):
        change_page("ethics")
        st.rerun()
        
    st.markdown("---")
    st.caption("SYSTEM")
    ui.button("Settings", variant="ghost", key="nav_settings")


# ==========================================
# 2. MAIN CONTENT
# ==========================================

# ------------------------------------------
# TRANG 1: RESUME ANALYZER
# ------------------------------------------
if st.session_state.current_page == "analyzer":
    st.caption("RecruitAI > **Resume Analyzer**")

    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.title("Resume Analyzer")
    with header_col2:
        jd_options = ["Senior Product Designer", "Frontend Engineer (React)", "Backend Developer (Python)"]
        selected_jd = st.selectbox("Job Description", jd_options, label_visibility="collapsed")

    st.write("") 
    uploaded_file = st.file_uploader("Drag and drop resume here (PDF, DOCX)", type=["pdf", "docx"])
    st.markdown("---")

    col_left, col_right = st.columns([4, 6], gap="large")

    with col_left:
        st.subheader("Extracted Profile 👤")
        st.markdown("<p class='profile-name'>Alex Rivera</p><p class='profile-sub'>6+ Years Experience • San Francisco, CA</p>", unsafe_allow_html=True)
        st.markdown("**Technical Skills**")
        ui.badges(badge_list=[("UI/UX Design", "secondary"), ("Figma", "secondary"), ("React", "secondary"), ("Tailwind CSS", "secondary")], key="skills_badges")
        st.markdown("<br>**Education**", unsafe_allow_html=True)
        st.markdown("🎓 **B.S. Interaction Design**<br>*University of California, Berkeley*", unsafe_allow_html=True)

    with col_right:
        st.subheader("AI Reasoning 🧠")
        score_col, text_col = st.columns([1, 3])
        with score_col:
            st.metric(label="Match Score", value="85%", delta="High Fit", delta_color="normal")
        with text_col:
            st.write("Highly qualified candidate with strong overlap in visual design and frontend knowledge. Past experience aligns perfectly.")
            st.write("✅ Technical Fit &nbsp;&nbsp; ✅ Experience Level &nbsp;&nbsp; ❌ Domain Gap")

        # Dùng native st.success / st.warning / st.info thay vì HTML custom
        st.success("**✔️ Verified:** Candidate has extensive experience building Design Systems which is a core requirement for this role.")
        st.error("**⚠️ Warning:** Limited experience mentioned regarding User Research methodologies.")
        st.success("**✔️ Verified:** Location match: Based in San Francisco.")

    st.markdown("---")
    st.subheader("Agent Calibration")
    st.write("Help the AI learn by providing feedback on its reasoning.")

    calib_col1, calib_col2 = st.columns([2, 8])
    with calib_col1:
        st.write("Do you agree?")
        vote_col1, vote_col2 = st.columns(2)
        with vote_col1:
            ui.button("👍 Yes", variant="outline", key="vote_yes")
        with vote_col2:
            ui.button("👎 No", variant="outline", key="vote_no")
    with calib_col2:
        feedback_text = st.text_area("Add override notes or feedback on the AI's logic...", label_visibility="collapsed")
        
    col_empty, col_btn = st.columns([8, 2])
    with col_btn:
        if ui.button("Submit Feedback", variant="default", key="submit_fb"):
            st.toast("Feedback saved!")

# ------------------------------------------
# TRANG 2: CANDIDATE RANKING
# ------------------------------------------
elif st.session_state.current_page == "ranking":
    st.caption("RecruitAI > **Candidate Ranking**")
    
    col_header1, col_header2 = st.columns([4, 1])
    with col_header1:
        st.title("Candidate Ranking")
        st.write("Compare and rank applicants based on custom job role requirements")
    with col_header2:
        st.write("") 
        ui.button("🔍 New Ranking", variant="default", key="new_ranking_btn")
    
    st.write("")
    
    # Mock Data
    data = {
        "ID": ["USR-9921", "USR-8842", "USR-7731", "USR-6610", "USR-5509", "USR-4422"],
        "Role": ["Senior Frontend Engineer", "Product Designer", "Backend Developer", "Data Scientist", "DevOps Engineer", "UX Researcher"],
        "Match Score": [94, 88, 82, 79, 75, 72],
        "AI Summary": ["Expertise in React and system design, proven track record...", "Strong portfolio with focus on accessibility...", "Proficient in Go and distributed systems...", "Experience with LLMs and data pipelines...", "Strong Kubernetes and CI/CD background...", "Skilled in qualitative analysis and user interviews..."],
        "Action": ["View Deep-Dive", "View Deep-Dive", "View Deep-Dive", "View Deep-Dive", "View Deep-Dive", "View Deep-Dive"]
    }
    df = pd.DataFrame(data)
    
    # Dùng st.dataframe với column_config để tạo thanh Progress trực tiếp trong bảng
    st.dataframe(
        df,
        column_config={
            "ID": st.column_config.TextColumn("Anonymized ID", width="small"),
            "Role": st.column_config.TextColumn("Role", width="medium"),
            "Match Score": st.column_config.ProgressColumn(
                "Match Score",
                help="AI assigned match score",
                format="%d%%",
                min_value=0,
                max_value=100,
            ),
            "AI Summary": st.column_config.TextColumn("AI Summary", width="large"),
            "Action": st.column_config.TextColumn("Action", width="small")
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.caption("Showing 1 to 6 of 128 results")

# ------------------------------------------
# TRANG 3: ANALYTICS & ETHICS DASHBOARD
# ------------------------------------------
elif st.session_state.current_page == "ethics":
    st.caption("RecruitAI > **Analytics & Ethics**")
    st.title("Ethics Dashboard")
    st.write("")
    
    # -- Row 1: KPI Metrics bằng st.metric --
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(label="Total Scanned", value="12,482", delta="12.5%")
    k2.metric(label="Avg. Match", value="78.5%", delta="3.2%")
    k3.metric(label="Diversity Index", value="92/100", delta="-0.8%", delta_color="inverse")
    k4.metric(label="Bias Score", value="Low (0.02)", delta="Stable", delta_color="off")
    
    st.markdown("---")
    
    # -- Row 2: Transparency & Fairness --
    col_trans_text, col_trans_score = st.columns([2, 1], gap="large")
    
    with col_trans_text:
        st.subheader("Transparency & Fairness")
        st.write("Our AI utilizes advanced debiasing techniques to ensure equitable hiring outcomes. This module monitors for protected class disparities in real-time, providing deep insights into the integrity of your algorithmic selection process.")
        
        st.info("**🛡️ Bias Mitigation Engines:** Algorithms are trained to exclude proxy variables for protected characteristics, focusing strictly on skill-based merit.")
        st.info("**🛡️ Real-time Parity Monitoring:** Continuous calculation of selection rates across different demographic groups to prevent disparate impact.")
        st.info("**🛡️ Audit-Ready Documentation:** Comprehensive logging of AI decision-making factors for full compliance with EEOC and local regulations.")
        
        btn_col1, btn_col2, _ = st.columns([1, 1, 2])
        with btn_col1:
            ui.button("View Full Audit Logs", variant="default", key="btn_audit")
        with btn_col2:
            ui.button("Export Ethics Report", variant="outline", key="btn_export")

    with col_trans_score:
        st.container(border=True)
        st.markdown("<h1 style='text-align: center; font-size: 5rem;'>⚖️</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Integrity Score: 98%</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>High confidence algorithmic neutrality</p>", unsafe_allow_html=True)

    st.markdown("---")

    # -- Row 3: Demographic Parity & Ethics Statement --
    col_parity, col_statement = st.columns(2, gap="large")
    
    with col_parity:
        st.subheader("Demographic Parity")
        
        st.write("Gender Equality: **0.96** (Target: 1.0)")
        st.progress(96)
        
        st.write("Racial Fairness: **0.94** (Target: 1.0)")
        st.progress(94)
        
        st.write("Age Neutrality: **0.99** (Target: 1.0)")
        st.progress(99)

    with col_statement:
        st.success("""
        ### AI Ethics Statement
        
        "Our commitment to ethical AI means we prioritize human oversight in every automated decision. 
        We believe technology should expand opportunities, not restrict them through hidden bias."
        
        📖 [Read our full Privacy & Fairness Policy](#)
        """)

# ------------------------------------------
# TRANG TRỐNG: DASHBOARD (Placeholder)
# ------------------------------------------
elif st.session_state.current_page == "dashboard":
    st.title("Dashboard")
    st.write("Trang tổng quan sẽ hiển thị ở đây...")

# ------------------------------------------
# TRANG 4: JOB SEARCH
# ------------------------------------------
elif st.session_state.current_page == "job_search":
    st.caption("RecruitAI > **Job Search**")
    
    st.title("Smart Job Search")
    st.write("Discover opportunities across global tech platforms with a single click.")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        job_query = st.text_input("Role or Keywords", placeholder="e.g., NLP Engineer, React Developer")
    with col2:
        job_location = st.text_input("Location", placeholder="e.g., Remote, San Francisco, Vietnam")
        
    if ui.button("Search Openings", variant="default", key="btn_search_jobs"):
        if not job_query:
            st.warning("Please enter a job role or keyword to start searching.")
        else:
            with st.spinner("Aggregating job portals..."):
                try:
                    # Đảm bảo FastAPI Backend đang chạy ở cổng 8000
                    api_url = "http://localhost:8000/api/v1/jobsearch/search"
                    params = {"keyword": job_query, "location": job_location if job_location else "Remote"}
                    
                    response = requests.get(api_url, params=params)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if data.get("status") == "success" and data.get("data"):
                        st.markdown("### 🎯 Recommended Portals")
                        st.write("Click on any portal below to view aggregated results directly.")
                        st.write("")
                        
                        # Hiển thị kết quả dạng Grid (2 cột)
                        res_col1, res_col2 = st.columns(2)
                        
                        for idx, portal_data in enumerate(data["data"]):
                            target_col = res_col1 if idx % 2 == 0 else res_col2
                            
                            with target_col:
                                st.markdown(f"""
                                <div style="
                                    background: rgba(255, 255, 255, 0.03); 
                                    border: 1px solid rgba(255, 255, 255, 0.1); 
                                    border-radius: 8px; 
                                    padding: 16px; 
                                    margin-bottom: 16px;">
                                    <h4 style="color: {portal_data['color']}; margin-top: 0;">{portal_data['portal']}</h4>
                                    <p style="color: #888; font-size: 0.9rem;">{portal_data['title']}</p>
                                    <a href="{portal_data['url']}" target="_blank" style="
                                        display: inline-block;
                                        background-color: {portal_data['color']};
                                        color: white;
                                        padding: 8px 16px;
                                        text-decoration: none;
                                        border-radius: 4px;
                                        font-size: 0.9rem;
                                        font-weight: bold;
                                    ">View Postings ↗</a>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.error("No data received from the aggregation engine.")
                        
                except requests.exceptions.ConnectionError:
                    st.error("Error: Could not connect to the Backend API. Please ensure the FastAPI server is running on localhost:8000.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")

# ------------------------------------------
# TRANG 5: RESUME BUILDER
# ------------------------------------------
elif st.session_state.current_page == "resume_builder":
    st.caption("RecruitAI > **Resume Builder**")
    st.title("Professional Resume Builder")
    st.write("Generate a high-quality, ATS-friendly resume in seconds.")

    # Khởi tạo State cho danh sách động nếu chưa có
    if "experiences" not in st.session_state:
        st.session_state.experiences = [{"company": "", "title": "", "date": "", "description": ""}]
    if "educations" not in st.session_state:
        st.session_state.educations = [{"school": "", "degree": "", "date": ""}]

    with st.sidebar:
        st.markdown("### Template Settings")
        selected_template = st.selectbox("Select Layout", ["Modern", "Professional", "Minimal", "Creative"])

    with st.container():
        # 1. Personal Information
        with st.expander("👤 Personal Information", expanded=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Full Name", placeholder="e.g. Alex Rivera")
            title = col2.text_input("Professional Title", placeholder="e.g. NLP Engineer")
            email = col1.text_input("Email Address")
            phone = col2.text_input("Phone Number")
            linkedin = st.text_input("LinkedIn URL")
            summary = st.text_area("Professional Summary", help="A brief overview of your career and goals.")

        # 2. Skills
        with st.expander("🛠️ Technical Skills"):
            skills_raw = st.text_input("Skills", placeholder="e.g. Python, FastAPI, NLP, PyTorch (separate by comma)")

        # 3. Work Experience (Dynamic List)
        with st.expander("💼 Work Experience"):
            for i, exp in enumerate(st.session_state.experiences):
                st.markdown(f"**Experience {i+1}**")
                col_c, col_r = st.columns(2)
                exp["company"] = col_c.text_input("Company Name", value=exp["company"], key=f"comp_{i}")
                exp["title"] = col_r.text_input("Job Role", value=exp["title"], key=f"role_{i}")
                exp["date"] = st.text_input("Duration", value=exp["date"], placeholder="e.g. Jan 2023 - Present", key=f"date_{i}")
                exp["description"] = st.text_area("Key Responsibilities", value=exp["description"], key=f"desc_{i}")
                st.divider()
            
            if st.button("➕ Add Another Experience"):
                st.session_state.experiences.append({"company": "", "title": "", "date": "", "description": ""})
                st.rerun()

        # 4. Education (Dynamic List)
        with st.expander("🎓 Education"):
            for i, edu in enumerate(st.session_state.educations):
                st.markdown(f"**Education {i+1}**")
                edu["school"] = st.text_input("Institution", value=edu["school"], key=f"school_{i}")
                col_d, col_y = st.columns(2)
                edu["degree"] = col_d.text_input("Degree", value=edu["degree"], key=f"deg_{i}")
                edu["date"] = col_y.text_input("Graduation Year", value=edu["date"], key=f"edy_{i}")
                st.divider()
                
            if st.button("➕ Add Another Education"):
                st.session_state.educations.append({"school": "", "degree": "", "date": ""})
                st.rerun()

    # Nút Generate
    if st.button("Generate Resume", type="primary", use_container_width=True):
        if not name or not email:
            st.error("Please fill in at least your Name and Email.")
        else:
            with st.spinner("Crafting your document..."):
                payload = {
                    "template": selected_template,
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "linkedin": linkedin,
                    "title": title,
                    "summary": summary,
                    "experience": [exp for exp in st.session_state.experiences if exp["company"].strip()],
                    "education": [edu for edu in st.session_state.educations if edu["school"].strip()],
                    "skills": [s.strip() for s in skills_raw.split(",") if s.strip()]
                }
                
                try:
                    res = requests.post("http://localhost:8000/api/v1/builder/generate", json=payload)
                    if res.status_code == 200:
                        st.success("Your resume is ready for download!")
                        st.download_button(
                            label="📥 Download DOCX File",
                            data=res.content,
                            file_name=f"Resume_{name.replace(' ', '_')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    else:
                        st.error(f"Server Error: {res.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e} - Đảm bảo FastAPI đang chạy (uvicorn src.api.main:app --reload)")