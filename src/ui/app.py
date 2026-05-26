import streamlit as st
import streamlit_shadcn_ui as ui
import pandas as pd
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# ==========================================
# 0. PAGE CONFIG & ROUTER
# ==========================================
st.set_page_config(page_title="RecruitAI", layout="wide", initial_sidebar_state="expanded")

if "auth_user"  not in st.session_state: st.session_state["auth_user"]  = None
if "auth_token" not in st.session_state: st.session_state["auth_token"] = None
if "auth_role"  not in st.session_state: st.session_state["auth_role"]  = None

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

    pages = {
        "dashboard":         "Dashboard",
        "analyzer":          "Resume Analyzer",
        "standard_analyzer": "Standard Analyzer",
        "ranking":           "Candidate Ranking",
        "job_search":        "Job Search",
        "resume_builder":    "Resume Builder",
        "ethics":            "Analytics & Ethics",
    }

    for page_key, page_label in pages.items():
        is_active = st.session_state.current_page == page_key

        # SỬA Ở ĐÂY: Dùng st.button native để tránh lỗi Phantom Click
        if st.button(
            label=page_label,
            type="primary" if is_active else "secondary",
            use_container_width=True,
            key=f"nav_{page_key}"
        ):
            if not is_active:
                st.session_state.current_page = page_key
                st.rerun()

    st.markdown("---")
    st.caption("SYSTEM")
    st.button("Settings", use_container_width=True, key="nav_settings")


# ==========================================
# 2. MAIN CONTENT
# ==========================================

# Clear standard analyzer results when navigating away
if st.session_state.current_page != "standard_analyzer":
    if "std_analysis" in st.session_state:
        del st.session_state["std_analysis"]
    if "std_file" in st.session_state:
        del st.session_state["std_file"]

# ------------------------------------------
# TRANG 1: RESUME ANALYZER
# ------------------------------------------
if st.session_state.current_page == "analyzer":
    import requests
    
    st.caption("RecruitAI > **Resume Analyzer**")

    # Khởi tạo session state để lưu trữ kết quả phân tích
    if "ai_analysis_result" not in st.session_state:
        st.session_state.ai_analysis_result = None

    st.title("Resume Analyzer")
    st.write("AI Agent evaluation with SBERT semantic matching.")
    st.markdown("---")

    # ── Job roles từ API ────────────────────────────────────
    @st.cache_data(ttl=3600)
    def fetch_job_roles_for_ai():
        # Gọi chung endpoint lấy danh sách Job Roles với Standard Analyzer
        res = requests.get(f"{API_BASE_URL}/api/v1/standard-analyzer/job-roles", timeout=10)
        res.raise_for_status()
        return res.json()["data"]

    try:
        job_roles_map = fetch_job_roles_for_ai()
    except Exception:
        st.error("Không kết nối được Backend. Chạy: uvicorn src.api.main:app --reload")
        st.stop()

    all_categories = list(job_roles_map.keys())

    # ── Giao diện 3 cột: Upload | Category | Role ─────────────
    col_file, col_cat, col_role = st.columns([3, 2, 2])

    with col_file:
        uploaded_file = st.file_uploader(
            "Upload resume", type=["pdf", "docx"],
            label_visibility="collapsed",
            key="ai_uploaded_file" # Đổi key để không bị trùng với Standard Analyzer
        )

    with col_cat:
        selected_cat = st.selectbox("Category", all_categories, key="ai_cat")

    with col_role:
        role_options  = job_roles_map[selected_cat]
        selected_role = st.selectbox("Job Role", role_options, key="ai_role")

    run_ai_btn = st.button(
        "🚀 Run AI Analysis", type="primary", use_container_width=True,
        disabled=(uploaded_file is None) # Nút chỉ sáng lên khi đã có file
    )
    st.markdown("---")

    # =========================================================
    # XỬ LÝ LOGIC GỌI API 
    # =========================================================
    if run_ai_btn and uploaded_file:
        with st.spinner("🕵️ Agent is thinking, parsing resume, and running SBERT matching..."):
            file_bytes = uploaded_file.getvalue()
            files = {"resume_file": (uploaded_file.name, file_bytes, uploaded_file.type)}
            
            data = {
                "job_category": selected_cat, 
                "job_role": selected_role
            }
            
            try:
                res = requests.post(f"{API_BASE_URL}/api/v1/analyzer/analyze_ai", data=data, files=files)
                if res.status_code == 200:
                    st.session_state.ai_analysis_result = res.json()
                else:
                    st.error(f"❌ Backend Error: {res.text}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Could not connect to the Backend API. Ensure FastAPI is running.")

    # =========================================================
    # RENDER GIAO DIỆN PHÂN TÍCH DỰA TRÊN STATE
    # =========================================================
    col_left, col_right = st.columns([4, 6], gap="large")
    result_data = st.session_state.ai_analysis_result

    if result_data:
        st.session_state["last_candidate_id"] = result_data.get("candidate_id")
        st.session_state["last_analysis_id"] = result_data.get("analysis_id")

    # --- CỘT TRÁI: HIỂN THỊ PROFILE ---
    with col_left:
        st.subheader("Extracted Profile 👤")
        
        if not result_data:
            st.info("No profile extracted yet. Please run the analysis.")
        else:
            profile = result_data.get("extracted_profile", {})
            
            full_name = profile.get("full_name") or "Unknown Candidate"
            exp_years = profile.get("total_exp_years") or 0
            location = profile.get("contact", {}).get("address") or "Location N/A"
            
            st.markdown(f"<p class='profile-name'>{full_name}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='profile-sub'>{exp_years} Years Experience • {location}</p>", unsafe_allow_html=True)
            
            tech_skills = profile.get("skills", {}).get("technical", [])
            if tech_skills:
                st.markdown("**Technical Skills**")
                ui.badges(badge_list=[(s, "secondary") for s in tech_skills[:10]], key="ai_skills_badges")
            
            education_list = profile.get("education", [])
            if education_list:
                st.markdown("<br>**Education**", unsafe_allow_html=True)
                for edu in education_list[:2]:
                    degree = edu.get("degree") or ""
                    field = edu.get("field") or ""
                    school = edu.get("institution") or "Unknown Institution"
                    year = edu.get("graduation_year") or ""
                    
                    deg_str = f"{degree} {field}".strip() or "Academic Degree"
                    st.markdown(f"🎓 **{deg_str}**<br>*{school} ({year})*", unsafe_allow_html=True)

    # --- CỘT PHẢI: HIỂN THỊ AGENT REASONING ---
    with col_right:
        st.subheader("AI Agent Reasoning 🧠")
        
        if not result_data:
            st.info("👈 Upload a resume and click 'Run AI Analysis' to let the Agent evaluate the candidate.")
        else:
            data_ai = result_data.get("analysis", {})
            
            score_col, text_col = st.columns([1, 3])
            with score_col:
                score_val = data_ai.get('match_score', 0)
                
                # Phân loại nhãn và màu sắc tự động dựa trên dải điểm hiệu chuẩn
                if score_val >= 75.0:
                    fit_label = "Good Fit"
                    d_color = "normal"   # Màu Xanh lá
                elif score_val >= 50.0:
                    fit_label = "Potential Fit"
                    d_color = "off"      # Màu Xám trung tính
                else:
                    fit_label = "No Fit"
                    d_color = "inverse"  # Màu Đỏ cảnh báo
                
                st.metric(
                    label="Match Score", 
                    value=f"{score_val}%", 
                    delta=fit_label, 
                    delta_color=d_color,
                    help="Calculated by fine-tuned SBERT model" # Thêm chú thích nhỏ khi di chuột vào
                )
            
            with text_col:
                st.write(data_ai.get("reasoning", "No analysis reasoning provided."))
                
            st.markdown("#### Agent Verification Report")
            for strength in data_ai.get("verified_strengths", []):
                st.success(f"**{strength}**")
                
            for warning in data_ai.get("warnings", []):
                st.warning(f"**{warning}**")
                
            suggestions = data_ai.get("interview_suggestions", [])
            if suggestions:
                with st.expander("💬 Interview Suggestions from AI", expanded=True):
                    for idx, q in enumerate(suggestions):
                        st.markdown(f"{idx + 1}. {q}")

    # =========================================================
    # PHẦN CALIBRATION (AGENT FEEDBACK)
    # =========================================================
    st.markdown("---")
    st.subheader("Agent Calibration")
    st.write("Help the AI learn by providing feedback on its reasoning.")

    candidate_id = st.session_state.get("last_candidate_id")
    analysis_id  = st.session_state.get("last_analysis_id")

    ai_score_val = 0
    if result_data and "analysis" in result_data:
        ai_score_val = result_data["analysis"].get("match_score", 0)

    calib_col1, calib_col2 = st.columns([2, 8])
    with calib_col1:
        st.write("Do you agree?")
        vote_col1, vote_col2 = st.columns(2)
        with vote_col1:
            # Lưu trạng thái "up" khi bấm Yes
            if ui.button("👍 Yes", variant="outline", key="ai_vote_yes"):
                st.session_state["_ai_vote"] = "up"
                st.toast("👍 Vote recorded!")
        with vote_col2:
            # Lưu trạng thái "down" khi bấm No
            if ui.button("👎 No", variant="outline", key="ai_vote_no"):
                st.session_state["_ai_vote"] = "down"
                st.toast("👎 Vote recorded!")
    with calib_col2:
        feedback_text = st.text_area(
            "Add override notes or feedback on the AI's logic...", 
            label_visibility="collapsed",
            key="ai_feedback_input"
        )

    col_empty, col_btn = st.columns([8, 2])
    with col_btn:
        if ui.button("Submit Feedback", variant="default", key="ai_submit_fb"):
            if not candidate_id:
                st.warning("⚠️ No candidate in session. Run analysis first.")
            else:
                try:
                    import requests
                    fb_response = requests.post(
                        f"{API_BASE_URL}/api/v1/standard-analyzer/feedback",
                        json={
                            "candidate_id": candidate_id,
                            "analysis_id":  analysis_id,
                            "vote":         st.session_state.get("_ai_vote", "neutral"),
                            "notes":        feedback_text.strip() or None,
                            "ai_score":     float(ai_score_val),
                            "agreed":       st.session_state.get("_ai_vote") == "up",
                        },
                        timeout=10,
                    )
                    
                    if fb_response.status_code == 200:
                        st.toast("✅ Feedback saved to Database!")
                        st.session_state.pop("_ai_vote", None) 
                    else:
                        st.error(f"Feedback error: {fb_response.text}")
                except Exception as fb_err:
                    st.error(f"Could not save feedback: {fb_err}")

# ------------------------------------------
# TRANG 2: CANDIDATE RANKING
# ------------------------------------------
elif st.session_state.current_page == "ranking":
    import sys, os

    _root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if _root not in sys.path:
        sys.path.insert(0, _root)

    from src.utils.auth import login, logout, is_logged_in, is_admin

    st.markdown("---")
    if is_logged_in():
        u = st.session_state["auth_user"]
        st.caption(f"👤 {u['username']}")
        st.caption(f"Role: `{st.session_state.get('auth_role','viewer')}`")
        if st.button("Đăng xuất", use_container_width=True, key="logout_btn"):
            logout()
            st.rerun()
    else:
        st.caption("Chưa đăng nhập")

    st.caption("RecruitAI > **Candidate Ranking**")
    st.title("Candidate Ranking")

    # ── GATE: chưa đăng nhập ──────────────────────────────────────
    if not is_logged_in():
        st.warning("🔒 Trang này yêu cầu đăng nhập với quyền **Admin**.")
        st.markdown("---")

        col = st.columns([1, 2, 1])[1]
        with col:
            st.markdown("##### Đăng nhập")
            with st.form("login_form"):
                username  = st.text_input("Tên đăng nhập", placeholder="admin")
                password  = st.text_input("Mật khẩu", type="password", placeholder="••••••••")
                submitted = st.form_submit_button(
                    "Đăng nhập", use_container_width=True, type="primary"
                )

            if submitted:
                if not username or not password:
                    st.warning("Vui lòng nhập đầy đủ.")
                else:
                    with st.spinner("Đang xác thực..."):
                        ok, msg = login(username, password)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # ── GATE: đã login nhưng không phải admin ────────────────────
    elif not is_admin():
        st.error("🔒 Bạn không có quyền truy cập. Chỉ **Admin** mới xem được trang này.")
        u = st.session_state["auth_user"]
        st.info(f"Tài khoản: `{u['username']}` — Role: `{st.session_state.get('auth_role','viewer')}`")
        if st.button("Đăng xuất và thử lại", key="relogin_btn"):
            logout()
            st.rerun()

    # ── NỘI DUNG RANKING (chỉ admin vào được) ────────────────────
    else:
        API = f"{API_BASE_URL}/api/v1/ranking"

        st.write("Compare and rank applicants based on ATS + AI scores.")
        st.markdown("---")

        # Sidebar weight controls
        with st.sidebar:
            st.markdown("---")
            st.markdown("### ⚖️ Score Weights")
            p1, p2, p3 = st.columns(3)
            if p1.button("50/50", key="rk_5050"): st.session_state["rk_wats"] = 50
            if p2.button("60/40", key="rk_6040"): st.session_state["rk_wats"] = 60
            if p3.button("70/30", key="rk_7030"): st.session_state["rk_wats"] = 70
            if "rk_wats" not in st.session_state: st.session_state["rk_wats"] = 50
            w_ats = st.slider("ATS Weight (%)", 0, 100, step=5, key="rk_wats")
            w_ai  = 100 - w_ats
            st.markdown(f"**Final = ATS×{w_ats}% + AI×{w_ai}%**")

        # Lấy danh sách roles
        try:
            roles_resp = requests.get(f"{API}/roles", timeout=5).json()
            role_options = ["— All —"] + roles_resp.get("data", [])
        except Exception:
            role_options = ["— All —"]

        # Filters
        f1, f2, f3, f4 = st.columns([3, 2, 2, 2])
        search     = f1.text_input("Search name / email", placeholder="Tìm kiếm...", key="rk_search")
        role_sel   = f2.selectbox("Job Role",  role_options, key="rk_role")
        status_sel = f3.selectbox("Status",
                        ["— All —", "pending", "shortlisted", "rejected", "hired"],
                        key="rk_status")
        sort_sel   = f4.selectbox("Sort by",
                        ["Final score", "ATS score", "AI score", "Name"],
                        key="rk_sort")

        sort_map = {
            "Final score": "final_score",
            "ATS score":   "ats_score",
            "AI score":    "sbert_score",
            "Name":        "name",
        }

        params = {"w_ats": w_ats, "sort_by": sort_map[sort_sel], "limit": 200}
        if role_sel   != "— All —": params["job_role"] = role_sel
        if status_sel != "— All —": params["status"]   = status_sel
        if search.strip():          params["search"]   = search.strip()

        try:
            resp = requests.get(f"{API}/candidates", params=params, timeout=10)
            resp.raise_for_status()
            data  = resp.json()
            rows  = data.get("data", [])
            total = data.get("total", 0)
        except Exception as e:
            st.error(f"Không kết nối được Backend: {e}")
            rows, total = [], 0

        # Stats
        all_ats = [float(r.get("ats_score") or 0) for r in rows]
        avg_ats = round(sum(all_ats) / len(all_ats), 1) if all_ats else 0
        n_short = sum(1 for r in rows if r.get("status") == "shortlisted")
        n_hired = sum(1 for r in rows if r.get("status") == "hired")

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("👤 Candidates", total)
        k2.metric("🔵 Avg ATS",    f"{avg_ats}%")
        k3.metric("✅ Shortlisted", n_short)
        k4.metric("🎉 Hired",       n_hired)
        st.markdown("---")

        if not rows:
            st.info("Chưa có dữ liệu. Upload và phân tích CV trước.")
        else:
            STATUS_ICON = {
                "pending":     "⏳",
                "shortlisted": "✅",
                "rejected":    "❌",
                "hired":       "🎉",
            }

            table_rows = []
            for i, r in enumerate(rows):
                cand   = r.get("candidates") or {}
                ai_raw = r.get("sbert_score")
                ai_pct = round(float(ai_raw), 1) if ai_raw is not None else None
                final_raw = r.get("_final")
                final = round(float(final_raw) / 100, 1) if final_raw is not None else round(float(r.get("ats_score") or 0), 1)
                table_rows.append({
                    "#":           i + 1,
                    "Name":        cand.get("full_name") or "—",
                    "Email":       cand.get("email")     or "—",
                    "Role":        r.get("job_role", ""),
                    "🔵 ATS":      int(r.get("ats_score") or 0),
                    "🟣 AI Score": int(ai_pct) if ai_pct is not None else None,
                    "🏅 Final":    final,
                    "Status":      STATUS_ICON.get(r.get("status", "pending"), "⏳")
                                   + " " + (r.get("status", "pending")).capitalize(),
                    "Exp (yr)":    cand.get("total_exp_years"),
                    "_cmp_id":     r.get("id"),
                })

            import pandas as pd
            df = pd.DataFrame(table_rows)

            st.dataframe(
                df.drop(columns=["_cmp_id"]),
                column_config={
                    "#":           st.column_config.NumberColumn(width="small"),
                    "🔵 ATS":      st.column_config.ProgressColumn(
                                       "🔵 ATS",    format="%d%%",   min_value=0, max_value=100),
                    "🟣 AI Score": st.column_config.ProgressColumn(
                                       "🟣 AI",     format="%d%%",   min_value=0, max_value=100),
                    "🏅 Final":    st.column_config.ProgressColumn(
                                       "🏅 Final",  format="%.1f%%", min_value=0, max_value=100),
                },
                hide_index=True,
                use_container_width=True,
                height=min(500, 60 + len(table_rows) * 38),
            )
            st.caption(
                f"Showing {len(rows)}/{total} candidates  |  "
                f"Final = ATS×{w_ats}% + AI×{w_ai}%"
            )

            # Update status
            st.markdown("---")
            with st.expander("✏️ Cập nhật trạng thái ứng viên"):
                id_map = {
                    f"#{r['#']} — {r['Name']} ({r['Role']})": r["_cmp_id"]
                    for r in table_rows
                }
                u1, u2, u3 = st.columns([3, 2, 1])
                sel_lbl    = u1.selectbox("Chọn ứng viên", list(id_map.keys()), key="rk_upd_cand")
                new_status = u2.selectbox(
                    "Trạng thái mới",
                    ["pending", "shortlisted", "rejected", "hired"],
                    key="rk_upd_status"
                )
                u3.write("")
                u3.write("")
                if u3.button("💾 Lưu", key="rk_upd_btn"):
                    cmp_id = id_map[sel_lbl]
                    try:
                        res = requests.put(
                            f"{API}/{cmp_id}/status",
                            json={"status": new_status},
                            timeout=5,
                        )
                        if res.status_code == 200:
                            st.success(f"Đã cập nhật → **{new_status}**")
                            st.rerun()
                        else:
                            st.error(f"Lỗi: {res.text}")
                    except Exception as e:
                        st.error(str(e))



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
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from collections import Counter

    import sys, os, tempfile, shutil, json, hashlib
    from pathlib import Path

    _root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if _root not in sys.path:
        sys.path.insert(0, _root)

    from src.utils.supabase_client import get_supabase

    st.caption("RecruitAI > **Dashboard**")
    st.title("📊 Dashboard")
    st.markdown("Overview of the real-time recruitment system.")
    st.markdown("---")

    # ── Load dữ liệu ─────────────────────────────────────────
    @st.cache_data(ttl=30)
    def load_dashboard_data():
        db = get_supabase()
        candidates  = db.table("candidates").select("*").execute().data or []
        analyses    = db.table("resume_analyses").select("*").execute().data or []
        comparisons = db.table("job_comparisons").select(
                          "*, candidates(full_name, email, total_exp_years)"
                      ).execute().data or []
        feedbacks   = db.table("feedback_votes").select("*").execute().data or []
        searches    = db.table("job_search_history").select("*").execute().data or []
        builds      = db.table("resume_builds").select("*").execute().data or []
        return candidates, analyses, comparisons, feedbacks, searches, builds

    try:
        with st.spinner("Loading data..."):
            candidates, analyses, comparisons, feedbacks, searches, builds = load_dashboard_data()
    except Exception as e:
        st.error(f"❌ Unable to connect to Supabase: {e}")
        st.stop()

    # ── Refresh button ────────────────────────────────────────
    _, col_ref = st.columns([10, 1])
    with col_ref:
        if st.button("🔄", help="Refresh data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # ══════════════════════════════════════════════════════════
    # SIDEBAR PANEL: WEIGHT CONTROLS
    # ══════════════════════════════════════════════════════════
    with st.sidebar:
        st.markdown("---")
        st.markdown("### ⚖️ Score Weights")
        st.caption("Adjust the weights for calculating the Final Score")

        # Preset buttons
        preset_col1, preset_col2, preset_col3 = st.columns(3)
        with preset_col1:
            if st.button("50/50", use_container_width=True, key="preset_5050"):
                st.session_state["w_ats"] = 50
        with preset_col2:
            if st.button("60/40", use_container_width=True, key="preset_6040"):
                st.session_state["w_ats"] = 60
        with preset_col3:
            if st.button("70/30", use_container_width=True, key="preset_7030"):
                st.session_state["w_ats"] = 70

        # Khởi tạo mặc định
        if "w_ats" not in st.session_state:
            st.session_state["w_ats"] = 50

        w_ats = st.slider(
            "ATS Score Weight (%)",
            min_value=0, max_value=100,
            value=st.session_state["w_ats"],
            step=5,
            key="w_ats",
            help="Weight for ATS rule-based score"
        )
        w_ai = 100 - w_ats

        # Hiển thị công thức trực quan
        st.markdown(
            f"""
            <div style="
                background: rgba(99,102,241,0.1);
                border: 1px solid rgba(99,102,241,0.3);
                border-radius: 8px;
                padding: 10px 14px;
                margin-top: 8px;
                font-size: 0.82rem;
                line-height: 1.8;
            ">
            <b>Formula:</b><br>
            Final = ATS × <b>{w_ats}%</b> + AI × <b>{w_ai}%</b>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption("⚠️ AI Score = None nếu SBERT chưa chạy → Final = ATS Score")
        st.markdown("---")

    # ── Hàm tính Final Score ──────────────────────────────────
    def compute_final(ats, sbert, w_ats_pct):
        """
        ats     : 0–100
        sbert   : 0–1  (cosine similarity từ SBERT) hoặc None
        w_ats   : 0–100 (%)
        → Final : 0–100
        """
        w_ai_pct = 100 - w_ats_pct
        ats_val  = float(ats or 0)

        if sbert is None:
            # Chưa có AI score → dùng ATS làm đại diện
            return round(ats_val, 1)

        ai_val = float(sbert) * 100   # convert 0-1 → 0-100
        return round(ats_val * (w_ats_pct / 100) + ai_val * (w_ai_pct / 100), 1)

    # Tính Final Score cho toàn bộ comparisons theo trọng số hiện tại
    for c in comparisons:
        c["_final_computed"] = compute_final(
            c.get("ats_score"),
            c.get("sbert_score"),
            w_ats
        )
        # Convert sbert 0-1 → 0-100 để hiển thị
        c["_ai_score_100"] = round(float(c["sbert_score"]) * 100, 1) \
                             if c.get("sbert_score") is not None else None

    # ══════════════════════════════════════════════════════════
    # ROW 1: KPI METRICS
    # ══════════════════════════════════════════════════════════
    total_candidates = len(candidates)
    total_analyses   = len(analyses)
    ats_scores       = [a["ats_score"] for a in analyses if a.get("ats_score") is not None]
    avg_ats          = round(sum(ats_scores) / len(ats_scores), 1) if ats_scores else 0

    ai_scores_raw    = [c["sbert_score"] for c in comparisons if c.get("sbert_score") is not None]
    avg_ai           = round(sum(ai_scores_raw) / len(ai_scores_raw) * 100, 1) if ai_scores_raw else None

    finals           = [c["_final_computed"] for c in comparisons]
    avg_final        = round(sum(finals) / len(finals), 1) if finals else 0

    has_ai           = len(ai_scores_raw) > 0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("👤 Candidate",      f"{total_candidates:,}")
    k2.metric("📋 Analysis",     f"{total_analyses:,}")
    k3.metric("🔵 Avg ATS",       f"{avg_ats}%")
    k4.metric("🟣 Avg AI Score",  f"{avg_ai}%" if avg_ai else "—",
              help="AI Analyzer don't have data" if not avg_ai else None)
    k5.metric("🏅 Avg Final",     f"{avg_final}%",
              help=f"ATS×{w_ats}% + AI×{w_ai}%")
    k6.metric("🔍 Searches",      f"{len(searches):,}")

    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    # ROW 2: SCORE COMPARISON CHART + RADAR
    # ══════════════════════════════════════════════════════════
    col_scatter, col_radar = st.columns([3, 2], gap="large")

    with col_scatter:
        st.subheader("🔵🟣 ATS vs AI Score")
        if comparisons and has_ai:
            plot_data = []
            for c in comparisons:
                if c.get("sbert_score") is not None:
                    cand = c.get("candidates") or {}
                    plot_data.append({
                        "Tên":        cand.get("full_name", "N/A"),
                        "Job Role":   c.get("job_role", ""),
                        "ATS Score":  float(c.get("ats_score") or 0),
                        "AI Score":   c["_ai_score_100"],
                        "Final Score": c["_final_computed"],
                        "Status":     c.get("status", "pending"),
                    })

            if plot_data:
                df_scatter = pd.DataFrame(plot_data)
                fig_sc = px.scatter(
                    df_scatter,
                    x="ATS Score", y="AI Score",
                    size="Final Score",
                    color="Job Role",
                    hover_data=["Tên", "Final Score", "Status"],
                    size_max=20,
                    opacity=0.8,
                )
                fig_sc.update_layout(
                    height=300,
                    margin=dict(t=10, b=10, l=10, r=10),
                    xaxis=dict(range=[0, 100], title="ATS Score (rule-based)"),
                    yaxis=dict(range=[0, 100], title="AI Score (SBERT ×100)"),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#94a3b8"),
                    legend=dict(orientation="h", yanchor="top", y=-0.2),
                )
                # Đường diagonal = ATS == AI
                fig_sc.add_shape(
                    type="line", x0=0, y0=0, x1=100, y1=100,
                    line=dict(dash="dot", color="rgba(148,163,184,0.3)", width=1)
                )
                st.plotly_chart(fig_sc, use_container_width=True)
                st.caption("Points lying on the diagonal line indicate that AI is rated higher than ATS, and vice versa.")
            else:
                st.info("No AI Scores available.")
        elif not has_ai:
            # Hiển thị chỉ ATS distribution nếu chưa có SBERT
            st.caption("⚠️ No AI Scores available")
            if ats_scores:
                fig_hist = px.histogram(
                    x=ats_scores, nbins=10,
                    labels={"x": "ATS Score", "y": "Số CV"},
                    color_discrete_sequence=["#6366f1"],
                )
                fig_hist.update_layout(
                    height=280, margin=dict(t=5, b=5, l=5, r=5),
                    xaxis=dict(range=[0, 100]),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#94a3b8"),
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.info("No data available.")
        else:
            st.info("No data available.")

    with col_radar:
        st.subheader("📐 Avg ATS Breakdown")
        if analyses:
            section_keys = {
                "Contact":    "score_contact",
                "Summary":    "score_summary",
                "Skills":     "score_skills",
                "Experience": "score_experience",
                "Education":  "score_education",
                "Format":     "score_format",
            }
            avg_sec = {}
            for label, key in section_keys.items():
                vals = [a[key] for a in analyses if a.get(key) is not None]
                avg_sec[label] = round(sum(vals) / len(vals), 1) if vals else 0

            cats   = list(avg_sec.keys()) + [list(avg_sec.keys())[0]]
            vals_r = list(avg_sec.values()) + [list(avg_sec.values())[0]]

            fig_r = go.Figure(go.Scatterpolar(
                r=vals_r, theta=cats,
                fill="toself",
                fillcolor="rgba(99,102,241,0.15)",
                line=dict(color="#6366f1", width=2),
                marker=dict(size=5, color="#6366f1"),
            ))
            fig_r.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100],
                                    gridcolor="rgba(148,163,184,0.15)",
                                    tickfont=dict(size=9, color="#94a3b8")),
                    angularaxis=dict(gridcolor="rgba(148,163,184,0.15)",
                                     tickfont=dict(size=10, color="#e2e8f0")),
                    bgcolor="rgba(0,0,0,0)",
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=20, b=20, l=40, r=40),
                height=280,
            )
            st.plotly_chart(fig_r, use_container_width=True)
        else:
            st.info("No analysis data available.")

    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    # ROW 3: SCORE DISTRIBUTION
    # ══════════════════════════════════════════════════════════
    st.subheader("📊 Score Distribution")

    ats_list   = [int(c.get("ats_score") or 0) for c in comparisons]
    ai_list    = [int(c["_ai_score_100"]) for c in comparisons if c["_ai_score_100"] is not None]
    final_list = [c["_final_computed"] for c in comparisons]

    tab1, tab2, tab3 = st.tabs(["🔵 ATS Score", "🟣 AI Score", "🏅 Final Score"])

    def make_hist(data, color, title):
        if not data:
            return None
        fig = px.histogram(
            x=data, nbins=10,
            labels={"x": title, "y": "Số CV"},
            color_discrete_sequence=[color],
        )
        # Phân vùng màu nền
        for x0, x1, clr in [(0,50,"rgba(239,68,68,0.05)"),
                             (50,75,"rgba(245,158,11,0.05)"),
                             (75,100,"rgba(34,197,94,0.05)")]:
            fig.add_vrect(x0=x0, x1=x1, fillcolor=clr, line_width=0, layer="below")
        fig.add_vline(x=sum(data)/len(data), line_dash="dash",
                      line_color="rgba(255,255,255,0.4)",
                      annotation_text=f"Avg: {sum(data)/len(data):.1f}",
                      annotation_position="top right",
                      annotation_font_color="#94a3b8")
        fig.update_layout(
            height=250, margin=dict(t=10, b=10, l=10, r=10),
            xaxis=dict(range=[0, 100]),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            bargap=0.08,
        )
        return fig

    with tab1:
        fig = make_hist(ats_list, "#6366f1", "ATS Score")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            low = sum(1 for s in ats_list if s < 50)
            mid = sum(1 for s in ats_list if 50 <= s < 75)
            hi  = sum(1 for s in ats_list if s >= 75)
            c1, c2, c3 = st.columns(3)
            c1.metric("🔴 Thấp (<50)",    low)
            c2.metric("🟡 Trung (50–74)", mid)
            c3.metric("🟢 Cao (≥75)",     hi)
        else:
            st.info("Not have ATS available.")

    with tab2:
        if ai_list:
            fig = make_hist(ai_list, "#a855f7", "AI Score")
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                low = sum(1 for s in ai_list if s < 50)
                mid = sum(1 for s in ai_list if 50 <= s < 75)
                hi  = sum(1 for s in ai_list if s >= 75)
                c1, c2, c3 = st.columns(3)
                c1.metric("🔴 Thấp (<50)",    low)
                c2.metric("🟡 Trung (50–74)", mid)
                c3.metric("🟢 Cao (≥75)",     hi)
        else:
            st.info("⚠️ No AI Scores available")

    with tab3:
        fig = make_hist(final_list, "#0ea5e9", "Final Score")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            low = sum(1 for s in final_list if s < 50)
            mid = sum(1 for s in final_list if 50 <= s < 75)
            hi  = sum(1 for s in final_list if s >= 75)
            c1, c2, c3 = st.columns(3)
            c1.metric("🔴 Thấp (<50)",    low)
            c2.metric("🟡 Trung (50–74)", mid)
            c3.metric("🟢 Cao (≥75)",     hi)
        else:
            st.info("No data available.")

    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    # ROW 5: FEEDBACK + JOB SEARCH + BUILDS
    # ══════════════════════════════════════════════════════════
    col_fb, col_search, col_build = st.columns(3, gap="large")

    with col_fb:
        st.subheader("💬 Feedback Stats")
        if feedbacks:
            up      = sum(1 for f in feedbacks if f.get("vote") == "up")
            down    = sum(1 for f in feedbacks if f.get("vote") == "down")
            neutral = sum(1 for f in feedbacks if f.get("vote") == "neutral")
            agreed  = sum(1 for f in feedbacks if f.get("agreed") is True)
            total_f = len(feedbacks)
            agree_rate = round(agreed / total_f * 100, 1) if total_f else 0

            m1, m2 = st.columns(2)
            m1.metric("Tổng", total_f)
            m2.metric("Đồng ý AI", f"{agree_rate}%")

            fig_pie = px.pie(
                values=[up, down, neutral],
                names=["👍 Đồng ý", "👎 Không đồng ý", "😐 Trung lập"],
                color_discrete_sequence=["#22c55e", "#ef4444", "#94a3b8"],
                hole=0.5,
            )
            fig_pie.update_layout(
                height=200, margin=dict(t=5, b=30, l=5, r=5),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.5, font=dict(size=10)),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"),
            )
            fig_pie.update_traces(textinfo="percent+value")
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No feedback available.\nUse 👍/👎 in the Standard Analyzer.")

    with col_search:
        st.subheader("🔍 Trending Keywords")
        if searches:
            kw_counts  = Counter(s["keyword"] for s in searches if s.get("keyword"))
            top_kw     = kw_counts.most_common(6)
            df_kw      = pd.DataFrame(top_kw, columns=["Từ khóa", "Lần tìm"])
            fig_kw     = px.bar(
                df_kw, x="Lần tìm", y="Từ khóa",
                orientation="h",
                color_discrete_sequence=["#0ea5e9"],
            )
            fig_kw.update_layout(
                height=230, margin=dict(t=5, b=5, l=5, r=5),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"),
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig_kw, use_container_width=True)
            st.metric("Tổng lần tìm", len(searches))
        else:
            st.info("No search history available.")

    with col_build:
        st.subheader("📄 Resume Templates")
        if builds:
            tmpl_counts = Counter(b.get("template", "Unknown") for b in builds)
            fig_tmpl    = px.pie(
                values=list(tmpl_counts.values()),
                names=list(tmpl_counts.keys()),
                color_discrete_sequence=["#f59e0b", "#10b981", "#6366f1", "#ec4899"],
                hole=0.4,
            )
            fig_tmpl.update_layout(
                height=230, margin=dict(t=5, b=30, l=5, r=5),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.5, font=dict(size=10)),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"),
            )
            fig_tmpl.update_traces(textinfo="percent+label")
            st.plotly_chart(fig_tmpl, use_container_width=True)
            st.metric("Tổng resume đã tạo", len(builds))
        else:
            st.info("No resume templates available.")

    st.markdown("---")

# # ------------------------------------------
# # TRANG 4: JOB SEARCH
# # ------------------------------------------
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
                    api_url = f"{API_BASE_URL}/api/v1/jobsearch/search"
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

# ──────────────────────────────────────────
# RESUME BUILDER 
# ──────────────────────────────────────────
elif st.session_state.current_page == "resume_builder":
    import sys, os
    from io import BytesIO

    _root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if _root not in sys.path:
        sys.path.insert(0, _root)

    from src.utils.resume_template import ResumeBuilder
    from src.utils.supabase_client import save_resume_build

    @st.cache_resource
    def get_resume_builder():
        return ResumeBuilder()

    st.caption("RecruitAI > **Resume Builder**")
    st.title("Professional Resume Builder")
    st.markdown("---")

    # ── Session state init ────────────────────────────────────
    if "experiences" not in st.session_state:
        st.session_state.experiences = [{"company":"","title":"","date":"","description":""}]
    if "educations" not in st.session_state:
        st.session_state.educations = [{"school":"","degree":"","date":""}]
    if "rb_generated" not in st.session_state:
        st.session_state.rb_generated = None
    if "rb_template" not in st.session_state:
        st.session_state.rb_template = "Modern"

    # ── Template selector ─────────
    st.markdown("#### 🎨 Choose Template")
    tmpl_cols = st.columns(4)
    TEMPLATES = {
        "Modern":       ("🔵", "#2980b9"),
        "Professional": ("⚫", "#1a1a1a"),
        "Minimal":      ("⬜", "#212121"),
        "Creative":     ("🟣", "#9b59b6"),
    }

    for i, (tmpl_name, (icon, color)) in enumerate(TEMPLATES.items()):
        with tmpl_cols[i]:
            is_selected = st.session_state.rb_template == tmpl_name

            border    = f"3px solid {color}" if is_selected else "1px solid rgba(150,150,150,0.3)"
            bg        = f"{color}22"         if is_selected else "rgba(255,255,255,0.03)"
            weight    = "700"                if is_selected else "400"
            txt_color = "white"              if is_selected else "#94a3b8"
            badge     = f'<div style="font-size:10px;color:{color};margin-top:2px">✓ Selected</div>' if is_selected else ""

            html_card = f'<div style="border:{border};background:{bg};border-radius:8px;padding:12px 8px;text-align:center;margin-bottom:4px;min-height:80px"><div style="font-size:22px">{icon}</div><div style="font-size:13px;font-weight:{weight};color:{txt_color};margin-top:4px">{tmpl_name}</div>{badge}</div>'
            st.markdown(html_card, unsafe_allow_html=True)

            # ── Dùng on_change callback thay vì if-button + st.rerun() ──
            def _select_tmpl(name):
                st.session_state.rb_template = name
                st.session_state.rb_generated = None

            # Sử dụng callback on_click để giữ nguyên state của form
            st.button("Select", key=f"tmpl_{tmpl_name}",
                      use_container_width=True,
                      type="primary" if is_selected else "secondary",
                      on_click=_select_tmpl,
                      args=(tmpl_name,))


    selected_template = st.session_state.rb_template
    st.markdown("---")

    # ── Lưu active tab để rerun không reset về tab 0 ──
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = 0

    # ══════════════════════════════════════════════════════════
    # 3 TABS
    # ══════════════════════════════════════════════════════════
    tab_form, tab_preview, tab_download = st.tabs(["📝 Form", "👁️ Preview", "📥 Download"])

    # ──────────────────────────────────────────────────────────
    # TAB 1: FORM
    # ──────────────────────────────────────────────────────────
    with tab_form:
        with st.expander("👤 Personal Information", expanded=True):
            c1, c2      = st.columns(2)
            rb_name     = c1.text_input("Full Name",           placeholder="e.g. Alex Rivera",      key="rb_name")
            rb_title    = c2.text_input("Professional Title",  placeholder="e.g. NLP Engineer",     key="rb_title")
            rb_email    = c1.text_input("Email Address",                                              key="rb_email")
            rb_phone    = c2.text_input("Phone Number",                                               key="rb_phone")
            rb_linkedin = st.text_input("LinkedIn URL",                                               key="rb_linkedin")
            rb_location = st.text_input("Location",            placeholder="e.g. Ho Chi Minh City", key="rb_location")
            rb_summary  = st.text_area("Professional Summary",
                                        placeholder="A brief overview of your career and goals.",
                                        key="rb_summary", height=100)

        with st.expander("🛠️ Technical Skills"):
            rb_skills = st.text_input("Skills",
                                       placeholder="Python, FastAPI, NLP, PyTorch (comma-separated)",
                                       key="rb_skills")

        with st.expander("💼 Work Experience"):
            for i, exp in enumerate(st.session_state.experiences):
                st.markdown(f"**Experience {i+1}**")
                cc, cr = st.columns(2)
                exp["company"]     = cc.text_input("Company",            value=exp["company"],      key=f"comp_{i}")
                exp["title"]       = cr.text_input("Job Role",           value=exp["title"],        key=f"role_{i}")
                exp["date"]        = st.text_input("Duration",           value=exp["date"],         key=f"date_{i}",
                                                    placeholder="Jan 2023 - Present")
                exp["description"] = st.text_area("Key Responsibilities", value=exp["description"], key=f"desc_{i}",
                                                    height=80)
                if len(st.session_state.experiences) > 1:
                    if st.button("🗑️ Remove", key=f"del_exp_{i}"):
                        st.session_state.experiences.pop(i)
                        st.rerun()
                st.divider()
            if st.button("➕ Add Experience", key="add_exp"):
                st.session_state.experiences.append({"company":"","title":"","date":"","description":""})
                st.rerun()

        with st.expander("🎓 Education"):
            for i, edu in enumerate(st.session_state.educations):
                st.markdown(f"**Education {i+1}**")
                edu["school"] = st.text_input("Institution", value=edu["school"], key=f"school_{i}")
                cd, cy = st.columns(2)
                edu["degree"] = cd.text_input("Degree",          value=edu["degree"], key=f"deg_{i}",
                                               placeholder="e.g. B.S. Computer Science")
                edu["date"]   = cy.text_input("Graduation Year", value=edu["date"],   key=f"edy_{i}",
                                               placeholder="e.g. 2023")
                if len(st.session_state.educations) > 1:
                    if st.button("🗑️ Remove", key=f"del_edu_{i}"):
                        st.session_state.educations.pop(i)
                        st.rerun()
                st.divider()
            if st.button("➕ Add Education", key="add_edu"):
                st.session_state.educations.append({"school":"","degree":"","date":""})
                st.rerun()

        st.info("💡 Chuyển sang tab **👁️ Preview** để xem trước resume theo thời gian thực.")

    # ──────────────────────────────────────────────────────────
    # TAB 2: PREVIEW
    # ──────────────────────────────────────────────────────────
    with tab_preview:
        selected_template = st.session_state.rb_template  # đọc sau khi có thể đã đổi

        name_v      = st.session_state.get("rb_name", "")
        title_v     = st.session_state.get("rb_title", "")
        email_v     = st.session_state.get("rb_email", "")
        phone_v     = st.session_state.get("rb_phone", "")
        linkedin_v  = st.session_state.get("rb_linkedin", "")
        location_v  = st.session_state.get("rb_location", "")
        summary_v   = st.session_state.get("rb_summary", "")
        skills_v    = st.session_state.get("rb_skills", "")
        skills_list = [s.strip() for s in skills_v.split(",") if s.strip()]

        TEMPLATE_STYLES = {
            "Modern": {
                "accent": "#2980b9", "bg": "#ffffff", "text": "#2c3e50",
                "header_bg": "#f0f7ff", "font": "'Georgia', serif",
                "name_size": "28px", "border": "2px solid #2980b9",
            },
            "Professional": {
                "accent": "#0078d7", "bg": "#ffffff", "text": "#1a1a1a",
                "header_bg": "#ffffff", "font": "'Segoe UI', sans-serif",
                "name_size": "26px", "border": "1px solid #0078d7",
            },
            "Minimal": {
                "accent": "#212121", "bg": "#ffffff", "text": "#212121",
                "header_bg": "#ffffff", "font": "'Helvetica Neue', sans-serif",
                "name_size": "32px", "border": "1px solid #212121",
            },
            "Creative": {
                "accent": "#9b59b6", "bg": "#fdf8ff", "text": "#34495e",
                "header_bg": "#f5eeff", "font": "'Arial', sans-serif",
                "name_size": "28px", "border": "2px solid #9b59b6",
            },
        }
        s = TEMPLATE_STYLES[selected_template]

        def sec(title):
            return f"""<div style="margin-top:18px;margin-bottom:8px;
                font-size:12px;font-weight:700;letter-spacing:1.8px;
                text-transform:uppercase;color:{s['accent']};
                padding-bottom:4px;border-bottom:{s['border']}">{title}</div>"""

        def badges(skills):
            return "".join([
                f'<span style="display:inline-block;background:{s["accent"]}18;'
                f'color:{s["accent"]};border:1px solid {s["accent"]}40;'
                f'border-radius:4px;padding:2px 10px;margin:3px 3px 0 0;font-size:12px">{sk}</span>'
                for sk in skills
            ])

        exp_html = ""
        for exp in st.session_state.experiences:
            if not exp.get("company","").strip(): continue
            lines = [f"<li style='margin:2px 0;font-size:12.5px'>{l.strip()}</li>"
                     for l in exp.get("description","").split("\n") if l.strip()]
            exp_html += f"""
            <div style="margin-bottom:12px">
                <div style="display:flex;justify-content:space-between">
                    <b style="font-size:14px">{exp.get('title','')}</b>
                    <span style="font-size:12px;color:#888">{exp.get('date','')}</span>
                </div>
                <div style="color:{s['accent']};font-size:13px;font-style:italic">{exp.get('company','')}</div>
                {"<ul style='margin:4px 0 0 16px;padding:0'>" + "".join(lines) + "</ul>" if lines else ""}
            </div>"""

        edu_html = ""
        for edu in st.session_state.educations:
            if not edu.get("school","").strip(): continue
            edu_html += f"""
            <div style="margin-bottom:10px">
                <div style="display:flex;justify-content:space-between">
                    <b style="font-size:14px">{edu.get('degree','')}</b>
                    <span style="font-size:12px;color:#888">{edu.get('date','')}</span>
                </div>
                <div style="color:{s['accent']};font-size:13px">{edu.get('school','')}</div>
            </div>"""

        contacts = " &nbsp;|&nbsp; ".join(filter(None, [
            f"✉ {email_v}" if email_v else "",
            f"📞 {phone_v}" if phone_v else "",
            f"📍 {location_v}" if location_v else "",
            f"🔗 {linkedin_v}" if linkedin_v else "",
        ]))

        html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
        <style>
            *{{box-sizing:border-box;margin:0;padding:0}}
            body{{font-family:{s['font']};background:{s['bg']};color:{s['text']};
                 padding:28px 32px;font-size:13px;line-height:1.55;max-width:800px;margin:0 auto}}
        </style></head><body>
        <div style="background:{s['header_bg']};padding:20px 24px;border-radius:6px;text-align:center;margin-bottom:2px">
            <div style="font-size:{s['name_size']};font-weight:800;letter-spacing:1px;
                        color:{s['accent']};margin-bottom:4px">
                {name_v.upper() if name_v else "YOUR NAME"}
            </div>
            {"<div style='font-size:14px;color:#666;margin-bottom:6px'>" + title_v + "</div>" if title_v else ""}
            {"<div style='font-size:12px;color:#888'>" + contacts + "</div>" if contacts else ""}
        </div>
        {sec("Professional Summary") + f"<p style='font-size:13px;margin-top:4px'>{summary_v}</p>" if summary_v else ""}
        {sec("Experience") + exp_html if exp_html else ""}
        {sec("Education") + edu_html if edu_html else ""}
        {sec("Skills") + "<div style='margin-top:6px'>" + badges(skills_list) + "</div>" if skills_list else ""}
        </body></html>"""

        if not name_v.strip():
            st.info("💡 Điền thông tin ở tab **📝 Form** để xem preview ở đây.")
        else:
            st.caption(f"🎨 Template: **{selected_template}** — cập nhật realtime")
            st.components.v1.html(html, height=720, scrolling=True)

    # ──────────────────────────────────────────────────────────
    # TAB 3: DOWNLOAD
    # ──────────────────────────────────────────────────────────

    with tab_download:
        name_dl   = st.session_state.get("rb_name",  "").strip()
        email_dl  = st.session_state.get("rb_email", "").strip()

        if not name_dl:
            st.warning("⚠️ Điền tên ở tab **📝 Form** trước.")
        else:
            st.markdown(f"### Generate cho **{name_dl}**")
            st.markdown(f"🎨 Template: **{selected_template}**")
            st.markdown("---")

            exp_count = sum(1 for e in st.session_state.experiences if e.get("company","").strip())
            edu_count = sum(1 for e in st.session_state.educations  if e.get("school","").strip())
            skl_count = len([s for s in st.session_state.get("rb_skills","").split(",") if s.strip()])

            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"""
| Mục | |
|---|---|
| 💼 Work Experience | {exp_count} mục |
| 🎓 Education | {edu_count} mục |
| 🛠️ Skills | {skl_count} kỹ năng |
| 📧 Email | {"✅ " + email_dl if email_dl else "❌ Chưa điền"} |
                """)
            with c2:
                st.write("")
                gen_btn = st.button(
                    "⚡ Generate", type="primary",
                    use_container_width=True, key="gen_resume",
                    disabled=(not email_dl)
                )

            if not email_dl:
                st.error("❌ Cần có Email để generate. Điền ở tab Form.")

            if gen_btn and email_dl:
                with st.spinner(f"Generating {selected_template} resume..."):
                    try:
                        # ── Build payload giống hệt code cũ ───────────────
                        skills_raw = st.session_state.get("rb_skills", "")

                        payload = {
                            "template": selected_template,
                            "name":     name_dl,
                            "email":    email_dl,
                            "phone":    st.session_state.get("rb_phone",    "").strip(),
                            "linkedin": st.session_state.get("rb_linkedin", "").strip(),
                            "title":    st.session_state.get("rb_title",    "").strip(),
                            "summary":  st.session_state.get("rb_summary",  "").strip(),
                            "experience": [
                                exp for exp in st.session_state.experiences
                                if exp.get("company", "").strip()
                            ],
                            "education": [
                                edu for edu in st.session_state.educations
                                if edu.get("school", "").strip()
                            ],
                            "skills": [
                                s.strip() for s in skills_raw.split(",")
                                if s.strip()
                            ],
                        }

                        # ── Gọi đúng endpoint hiện có ─────────────────────
                        res = requests.post(
                            f"{API_BASE_URL}/api/v1/builder/generate",
                            json=payload,
                            timeout=30,
                        )

                        if res.status_code == 200:
                            st.session_state.rb_generated = {
                                "bytes":     res.content,
                                "file_name": f"Resume_{name_dl.replace(' ', '_')}.docx"
                            }
                            st.success("✅ Resume generated successfully!")
                        else:
                            st.error(f"❌ Server Error {res.status_code}: {res.text}")

                    except requests.exceptions.ConnectionError:
                        st.error("❌ Không kết nối được Backend. Chạy: uvicorn src.api.main:app --reload")
                    except requests.exceptions.Timeout:
                        st.error("❌ Request timeout.")
                    except Exception as e:
                        st.error(f"❌ Lỗi: {e}")
                        st.exception(e)

            # ── Download button ────────────────────────────────
            if st.session_state.rb_generated:
                g = st.session_state.rb_generated
                st.download_button(
                    "📥 Download DOCX",
                    data=g["bytes"],
                    file_name=g["file_name"],
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="dl_resume",
                    use_container_width=True,
                )
                st.caption(f"`{g['file_name']}`")

# ------------------------------------------
# TRANG 6: STANDARD ANALYZER
# ------------------------------------------
elif st.session_state.current_page == "standard_analyzer":
    import requests
    import hashlib

    API_BASE = f"{API_BASE_URL}/api/v1/standard-analyzer"

    st.caption("RecruitAI > **Standard Analyzer**")
    st.title("Standard Analyzer")
    st.write("Rule-based ATS scoring.")
    st.markdown("---")

    # ── Job roles từ API ────────────────────────────────────
    @st.cache_data(ttl=3600)
    def fetch_job_roles():
        res = requests.get(f"{API_BASE}/job-roles", timeout=10)
        res.raise_for_status()
        return res.json()["data"]

    try:
        job_roles_map = fetch_job_roles()
    except Exception:
        st.error("Không kết nối được Backend. Chạy: uvicorn src.api.main:app --reload")
        st.stop()

    all_categories = list(job_roles_map.keys())

    col_file, col_cat, col_role = st.columns([3, 2, 2])

    with col_file:
        uploaded_file = st.file_uploader(
            "Upload resume", type=["pdf", "docx"],
            label_visibility="collapsed",
            key="std_uploaded_file"
        )

    with col_cat:
        selected_cat = st.selectbox("Category", all_categories, key="std_cat")

    with col_role:
        role_options  = job_roles_map[selected_cat]
        selected_role = st.selectbox("Job Role", role_options, key="std_role")

    run_btn = st.button(
        "Run Standard Analysis", type="primary",
        disabled=(uploaded_file is None)
    )

    # ── Gọi API phân tích ───────────────────────────────────
    if run_btn and uploaded_file:

        # Tính cache key từ file + role (khác role → phân tích lại)
        file_bytes = uploaded_file.getvalue()
        file_hash  = hashlib.md5(file_bytes).hexdigest()
        cache_key  = f"std_result_{file_hash}_{selected_role}"

        # Nếu đã có kết quả cho đúng file + đúng role → dùng lại
        if cache_key in st.session_state:
            st.session_state["std_analysis"] = st.session_state[cache_key]
            st.toast("Dùng kết quả đã phân tích (cache)")

        else:
            with st.spinner("Đang phân tích..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/analyze",
                        data={
                            "job_category": selected_cat,
                            "job_role":     selected_role,
                        },
                        files={
                            "resume_file": (
                                uploaded_file.name,
                                file_bytes,
                                uploaded_file.type,
                            )
                        },
                        timeout=120,
                    )

                    if response.status_code == 200:
                        data = response.json()
                        analysis = {
                            "structured":     data["structured_profile"],
                            "scores":         data["section_scores"],
                            "suggestions":    data["suggestions"],
                            "role":           selected_role,
                            "embedded_links": data.get("embedded_links", []),
                            "candidate_id":   data.get("candidate_id"),
                            "analysis_id":    data.get("analysis_id"),
                        }
                        st.session_state["std_analysis"] = analysis
                        # Lưu cache để lần sau không gọi lại
                        st.session_state[cache_key] = analysis

                    else:
                        detail = response.json().get("detail", response.text)
                        st.error(f"Lỗi {response.status_code}: {detail}")

                except requests.exceptions.ConnectionError:
                    st.error("Không kết nối được Backend API.")
                except requests.exceptions.Timeout:
                    st.error("Request timeout (>120s). Ollama có thể đang bận.")

    # ── Render kết quả ──────────────────────────────────────
    result = st.session_state.get("std_analysis")
    if result:
        # ✅ Chỉ một block if result — lưu session rồi render luôn
        st.session_state["last_candidate_id"] = result.get("candidate_id")
        st.session_state["last_analysis_id"]  = result.get("analysis_id")

        structured     = result["structured"]
        scores         = result["scores"]
        suggestions    = result["suggestions"]
        role           = result["role"]
        embedded_links = result.get("embedded_links", [])

        st.markdown(f"### Results — **{role}**")
        st.markdown("---")

        col_left, col_right = st.columns([4, 6], gap="large")

        with col_left:
            st.subheader("Extracted Profile 👤")

            st.markdown(f"**{structured.get('full_name', 'Unknown')}**")
            exp_years = structured.get("total_exp_years")
            if exp_years:
                st.caption(f"{exp_years} years experience")

            summary = structured.get("summary", "") or ""
            if summary:
                st.info(summary[:200] + ("…" if len(summary) > 200 else ""))

            contact   = structured.get("contact", {}) or {}
            llm_links = contact.get("links", []) or []
            all_links = list(set(llm_links + embedded_links))

            if contact.get("email") or contact.get("phone") or all_links:
                st.markdown("**Contact**")
                if contact.get("email"):
                    st.markdown(f"✉️ {contact['email']}")
                if contact.get("phone"):
                    st.markdown(f"📞 {contact['phone']}")
                for link in all_links:
                    if "linkedin" in link.lower():
                        st.markdown(f"🔗 [LinkedIn]({link})")
                    elif "github" in link.lower():
                        st.markdown(f"🐙 [GitHub]({link})")
                    elif "behance" in link.lower():
                        st.markdown(f"🎨 [Behance]({link})")
                    else:
                        st.markdown(f"🌐 [{link}]({link})")

            tech = structured.get("skills", {}).get("technical", []) or []
            soft = structured.get("skills", {}).get("soft", [])     or []
            if tech:
                st.markdown("**Technical Skills**")
                ui.badges([(s, "secondary") for s in tech[:10]], key="sa_tech")
            if soft:
                st.markdown("**Soft Skills**")
                ui.badges([(s, "outline") for s in soft[:6]], key="sa_soft")

            education = structured.get("education", []) or []
            if education:
                st.markdown("**Education**")
                for edu in education:
                    st.markdown(
                        f"🎓 **{edu.get('degree','') or ''} {edu.get('field','') or ''}**"
                        f" — {edu.get('institution','') or ''} {edu.get('graduation_year','') or ''}"
                    )

            experience = structured.get("experience", []) or []
            if experience:
                st.markdown("**Experience**")
                for exp in experience[:3]:
                    st.markdown(
                        f"💼 **{exp.get('role','') or ''}** @ {exp.get('company','') or ''}  \n"
                        f"_{exp.get('period','') or ''}_"
                    )

        with col_right:
            st.subheader("ATS Score Breakdown 📊")

            ats = scores.get("ats_score", 0)
            st.metric("Overall ATS Score", f"{ats} / 100")
            st.progress(ats / 100)
            st.markdown("")

            s1, s2, s3 = st.columns(3)
            s1.metric("Skills",     int(scores.get("skills",     0)))
            s2.metric("Experience", int(scores.get("experience", 0)))
            s3.metric("Format",     int(scores.get("format",     0)))
            s1.metric("Contact",    int(scores.get("contact",    0)))
            s2.metric("Education",  int(scores.get("education",  0)))
            s3.metric("Summary",    int(scores.get("summary",    0)))

            st.markdown("---")
            st.subheader("Suggestions ✏️")

            labels = {
                "contact_suggestions":    "📇 Contact",
                "summary_suggestions":    "📝 Summary",
                "skills_suggestions":     "🛠️ Skills",
                "experience_suggestions": "💼 Experience",
                "education_suggestions":  "🎓 Education",
                "format_suggestions":     "📐 Formatting",
            }
            any_msg = False
            for key, label in labels.items():
                msgs = suggestions.get(key, [])
                if msgs:
                    any_msg = True
                    with st.expander(f"{label} ({len(msgs)})", expanded=True):
                        for msg in msgs:
                            st.warning(msg)

            if not any_msg:
                st.success("✅ Resume is well-optimized for this role!")

            with st.expander("🔍 Raw extracted JSON"):
                st.json(structured)

        # ── Agent Calibration ───────────────────────────────
        st.markdown("---")
        st.subheader("Agent Calibration")
        st.write("Help the AI learn by providing feedback on its reasoning.")

        candidate_id = st.session_state.get("last_candidate_id")
        analysis_id  = st.session_state.get("last_analysis_id")

        calib_col1, calib_col2 = st.columns([2, 8])

        with calib_col1:
            st.write("Do you agree?")
            vote_col1, vote_col2 = st.columns(2)
            with vote_col1:
                if ui.button("👍 Yes", variant="outline", key="vote_yes"):
                    st.session_state["_vote"] = "up"
                    st.toast("👍 Vote recorded!")
            with vote_col2:
                if ui.button("👎 No", variant="outline", key="vote_no"):
                    st.session_state["_vote"] = "down"
                    st.toast("👎 Vote recorded!")

        with calib_col2:
            feedback_text = st.text_area(
                "Add override notes or feedback on the AI's logic…",
                label_visibility="collapsed",
                key="std_feedback_text"
            )

        col_empty, col_btn = st.columns([8, 2])
        with col_btn:
            if ui.button("Submit Feedback", variant="default", key="submit_fb"):
                if not candidate_id:
                    st.warning("⚠️ No candidate in session. Run analysis first.")
                else:
                    # ✅ Gọi API thay vì import Supabase trực tiếp
                    try:
                        fb_response = requests.post(
                            f"{API_BASE}/feedback",
                            json={
                                "candidate_id": candidate_id,
                                "analysis_id":  analysis_id,
                                "vote":         st.session_state.get("_vote", "neutral"),
                                "notes":        feedback_text.strip() or None,
                                "ai_score":     float(scores.get("ats_score") or 0),
                                "agreed":       st.session_state.get("_vote") == "up",
                            },
                            timeout=10,
                        )
                        if fb_response.status_code == 200:
                            st.toast("✅ Feedback saved!")
                            st.session_state.pop("_vote", None)
                        else:
                            st.error(f"Feedback error: {fb_response.text}")
                    except Exception as fb_err:
                        st.error(f"Could not save feedback: {fb_err}")