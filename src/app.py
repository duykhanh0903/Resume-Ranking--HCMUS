import streamlit as st
import streamlit_shadcn_ui as ui
import pandas as pd

# Thiết lập trang rộng (giống dashboard)
st.set_page_config(page_title="AI Screener", layout="wide", initial_sidebar_state="expanded")

# Thêm chút CSS custom nhẹ cho các hộp thông báo (do Streamlit không có sẵn màu nền nhạt)
st.markdown("""
<style>
    .reasoning-box-green { background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 15px; border-radius: 8px; color: #166534; margin-bottom: 10px; }
    .reasoning-box-red { background-color: #fef2f2; border: 1px solid #fecaca; padding: 15px; border-radius: 8px; color: #991b1b; margin-bottom: 10px; }
    .profile-name { font-size: 1.2rem; font-weight: bold; margin-bottom: 0;}
    .profile-sub { font-size: 0.9rem; color: #64748b; margin-top: 0;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. SIDEBAR (Tương đương Menu Trái)
# ==========================================
with st.sidebar:
    st.markdown("### ✨ AI Screener")
    st.markdown("---")
    
    # Dùng phím tắt menu
    ui.button("Dashboard", variant="ghost", key="nav_dash")
    ui.button("Resume Analyzer", variant="default", key="nav_analyzer") # Nút đang active
    ui.button("Job Board", variant="ghost", key="nav_job")
    ui.button("Talent Pool", variant="ghost", key="nav_talent")
    
    st.markdown("---")
    st.caption("SYSTEM")
    ui.button("Settings", variant="ghost", key="nav_settings")
    
    st.success("🟢 AI Engine Online")

# ==========================================
# 2. MAIN HEADER (Tương đương Top Navbar)
# ==========================================
st.caption("Dashboard > **Resume Analyzer**")

header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("Resume Analyzer")
with header_col2:
    # Dropdown chọn JD
    jd_options = ["Senior Product Designer", "Frontend Engineer (React)", "Backend Developer (Python)"]
    selected_jd = st.selectbox("Job Description", jd_options, label_visibility="collapsed")

st.write("") # Tạo khoảng trắng

# ==========================================
# 3. UPLOAD AREA (Core Area)
# ==========================================
uploaded_file = st.file_uploader("Drag and drop resume here (PDF, DOCX)", type=["pdf", "docx"])

st.markdown("---")

# ==========================================
# 4. ANALYSIS VIEW (40/60 Split)
# ==========================================
col_left, col_right = st.columns([4, 6], gap="large")

# --- CỘT TRÁI: EXTRACTED PROFILE ---
with col_left:
    st.subheader("Extracted Profile 👤")
    
    # Mock data hiển thị
    st.markdown("<p class='profile-name'>Alex Rivera</p><p class='profile-sub'>6+ Years Experience • San Francisco, CA</p>", unsafe_allow_html=True)
    
    st.markdown("**Technical Skills**")
    # Sử dụng badges của Shadcn UI
    ui.badges(badge_list=[("UI/UX Design", "secondary"), ("Figma", "secondary"), ("React", "secondary"), ("Tailwind CSS", "secondary")], key="skills_badges")
    
    st.markdown("<br>**Education**", unsafe_allow_html=True)
    st.markdown("🎓 **B.S. Interaction Design**<br>*University of California, Berkeley*", unsafe_allow_html=True)

# --- CỘT PHẢI: AI REASONING ---
with col_right:
    st.subheader("AI Reasoning 🧠")
    
    score_col, text_col = st.columns([1, 3])
    with score_col:
        # Streamlit dùng st.metric cho các con số nổi bật
        st.metric(label="Match Score", value="85%", delta="High Fit", delta_color="normal")
    with text_col:
        st.write("Highly qualified candidate with strong overlap in visual design and frontend knowledge. Past experience at Adobe aligns perfectly with our enterprise focus.")
        st.write("✅ Technical Fit &nbsp;&nbsp; ✅ Experience Level &nbsp;&nbsp; ❌ Domain Gap")

    # Các hộp lý luận chi tiết (Dùng HTML/CSS đã khai báo ở trên để giống màu thiết kế của bạn)
    st.markdown("""
        <div class="reasoning-box-green">
            <b>✔️ Verified:</b> Candidate has extensive experience building Design Systems which is a core requirement for this role.
        </div>
        <div class="reasoning-box-red">
            <b>⚠️ Warning:</b> Limited experience mentioned regarding User Research methodologies.
        </div>
        <div class="reasoning-box-green">
            <b>✔️ Verified:</b> Location match: Based in San Francisco.
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 5. FOOTER: AGENT CALIBRATION
# ==========================================
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