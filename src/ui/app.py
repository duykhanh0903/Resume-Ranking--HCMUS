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
        if ui.button(
            page_label,
            variant="secondary" if is_active else "ghost",
            key=f"nav_{page_key}"
        ):
            if not is_active:
                st.session_state.current_page = page_key
                st.rerun()

    st.markdown("---")
    st.caption("SYSTEM")
    ui.button("Settings", variant="ghost", key="nav_settings")


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
    # ROW 3: CANDIDATE RANKING TABLE (3 cột điểm + filter)
    # ══════════════════════════════════════════════════════════
    st.subheader("🏆 Candidate Ranking")
    st.caption(f"Final Score = ATS × **{w_ats}%** + AI × **{w_ai}%**")
 
    if comparisons:
        all_roles = sorted(set(c["job_role"] for c in comparisons if c.get("job_role")))
 
        f1, f2, f3 = st.columns([2, 2, 6])
        with f1:
            role_filter = st.selectbox(
                "Job Role", ["— Tất cả —"] + all_roles, key="dash_role_f"
            )
        with f2:
            status_filter = st.selectbox(
                "Trạng thái",
                ["— Tất cả —", "pending", "shortlisted", "rejected", "hired"],
                key="dash_status_f"
            )
 
        filtered = comparisons
        if role_filter != "— Tất cả —":
            filtered = [c for c in filtered if c.get("job_role") == role_filter]
        if status_filter != "— Tất cả —":
            filtered = [c for c in filtered if c.get("status") == status_filter]
 
        # Sắp xếp theo Final Score tính lại
        filtered = sorted(filtered, key=lambda x: x["_final_computed"], reverse=True)
 
        STATUS_ICON = {
            "pending":     "⏳ Pending",
            "shortlisted": "✅ Shortlisted",
            "rejected":    "❌ Rejected",
            "hired":       "🎉 Hired",
        }
 
        rows = []
        for i, c in enumerate(filtered[:50]):
            cand = c.get("candidates") or {}
            ai_display = c["_ai_score_100"]
            rows.append({
                "#":             i + 1,
                "Tên":           cand.get("full_name") or "N/A",
                "Job Role":      c.get("job_role", ""),
                "🔵 ATS":        int(c.get("ats_score") or 0),
                "🟣 AI Score":   int(ai_display) if ai_display is not None else None,
                "🏅 Final":      c["_final_computed"],
                "Trạng thái":    STATUS_ICON.get(c.get("status", "pending"), "⏳ Pending"),
                "_id":           c.get("id"),
            })
 
        df_rank = pd.DataFrame(rows)
 
        st.dataframe(
            df_rank.drop(columns=["_id"]),
            column_config={
                "#": st.column_config.NumberColumn(width="small"),
                "🔵 ATS": st.column_config.ProgressColumn(
                    "🔵 ATS", format="%d%%", min_value=0, max_value=100
                ),
                "🟣 AI Score": st.column_config.ProgressColumn(
                    "🟣 AI Score", format="%d%%", min_value=0, max_value=100
                ),
                "🏅 Final": st.column_config.ProgressColumn(
                    "🏅 Final", format="%.1f%%", min_value=0, max_value=100
                ),
            },
            hide_index=True,
            use_container_width=True,
            height=min(450, 55 + len(rows) * 35),
        )
 
        st.caption(
            f"Displaying {len(rows)}/{len(filtered)} candidates  |  "
            f"{'⚠️ AI Score column is empty = SBERT not run for this CV' if any(r['🟣 AI Score'] is None for r in rows) else '✅ All 3 scores available'}"
        )
 
        # ── Cập nhật status ───────────────────────────────────
        with st.expander("✏️ Cập nhật trạng thái ứng viên"):
            u1, u2, u3 = st.columns([3, 2, 1])
            with u1:
                id_map = {
                    f"#{r['#']} — {r['Tên']} ({r['Job Role']})": r["_id"]
                    for r in rows
                }
                sel_label = st.selectbox("Chọn ứng viên", list(id_map.keys()), key="upd_cand")
            with u2:
                new_status = st.selectbox(
                    "Trạng thái mới",
                    ["pending", "shortlisted", "rejected", "hired"],
                    key="upd_status"
                )
            with u3:
                st.write("")
                st.write("")
                if st.button("💾 Lưu", use_container_width=True, key="upd_btn"):
                    try:
                        db = get_supabase()
                        db.table("job_comparisons")\
                          .update({"status": new_status})\
                          .eq("id", id_map[sel_label])\
                          .execute()
                        st.success(f"✅ Đã cập nhật '{new_status}'")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
    else:
        st.info("Chưa có dữ liệu ranking.")
 
    st.markdown("---")
 
    # ══════════════════════════════════════════════════════════
    # ROW 4: SCORE DISTRIBUTION (3 loại điểm song song)
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
            st.info("⚠️ No AI Scores available — SBERT pipeline not run or sbert_score is None in DB.")
 
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
 
    # ══════════════════════════════════════════════════════════
    # ROW 6: RECENT CANDIDATES
    # ══════════════════════════════════════════════════════════
    st.subheader("👤 Ứng Viên Mới Nhất")
    if candidates:
        recent = sorted(candidates, key=lambda x: x["created_at"], reverse=True)[:10]
        st.dataframe(
            pd.DataFrame([{
                "Thời gian":   c["created_at"][:16].replace("T", " "),
                "Tên":         c.get("full_name") or "N/A",
                "Email":       c.get("email") or "—",
                "Phone":       c.get("phone") or "—",
                "Kinh nghiệm": f"{c.get('total_exp_years') or '?'} yr",
                "File":        c.get("file_name", ""),
            } for c in recent]),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No candidates available in the system.")
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


# ------------------------------------------
# TRANG 6: STANDARD ANALYZER
# ------------------------------------------
elif st.session_state.current_page == "standard_analyzer":
    import sys, os, tempfile, shutil, json, hashlib
    from pathlib import Path

    _root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if _root not in sys.path:
        sys.path.insert(0, _root)

    from src.utils.parser import ResumeBlockParser
    from src.utils.extractor import ResumeExtractor
    from src.utils.resume_analyzer import ResumeScorer
    from src.utils.configs.job_role import JOB_ROLES

    # ── Supabase helpers ────────────────────────────────────────
    from src.utils.supabase_client import (
        upsert_candidate,
        upsert_extracted_profile,
        save_resume_analysis,
        save_job_comparison,
        save_feedback_vote,
        get_supabase,
    )

    # ── Cached instances (load once, reuse across reruns) ──────
    @st.cache_resource
    def get_parser():
        return ResumeBlockParser()

    @st.cache_resource
    def get_extractor():
        return ResumeExtractor(model_name='llama3')

    @st.cache_resource
    def get_scorer():
        return ResumeScorer()

    st.caption("RecruitAI > **Standard Analyzer**")
    st.title("Standard Analyzer")
    st.write("Rule-based ATS scoring.")
    st.markdown("---")

    roles_by_cat   = {cat: list(roles.keys()) for cat, roles in JOB_ROLES.items()}
    all_categories = list(roles_by_cat.keys())

    col_file, col_cat, col_role = st.columns([3, 2, 2])

    with col_file:
        uploaded_file = st.file_uploader(
            "Upload resume", type=["pdf", "docx"],
            label_visibility="collapsed",
            key="std_uploaded_file"
        )
        if uploaded_file is not None:
            st.session_state["std_file"] = uploaded_file
        elif "std_file" in st.session_state:
            uploaded_file = st.session_state["std_file"]

    with col_cat:
        selected_cat = st.selectbox(
            "Category", all_categories,
            key="std_selected_cat",
            index=all_categories.index(
                st.session_state.get("std_cat", all_categories[0])
            )
        )
        st.session_state["std_cat"] = selected_cat

    with col_role:
        role_options  = roles_by_cat[selected_cat]
        saved_role    = st.session_state.get("std_role", role_options[0])
        role_index    = role_options.index(saved_role) if saved_role in role_options else 0
        selected_role = st.selectbox(
            "Job Role", role_options,
            key="std_selected_role",
            index=role_index
        )
        st.session_state["std_role"] = selected_role

    run_btn = st.button(
        "Run Standard Analysis", type="primary",
        disabled=(uploaded_file is None)
    )

    # ── Pipeline ───────────────────────────────────────────────
    if run_btn and uploaded_file:

        tmp_dir  = tempfile.mkdtemp()
        tmp_path = Path(tmp_dir) / uploaded_file.name
        tmp_path.write_bytes(uploaded_file.getvalue())

        file_bytes = uploaded_file.getvalue()
        file_hash  = hashlib.md5(file_bytes).hexdigest()
        cache_key  = f"extraction_{file_hash}"

        try:
            with st.status("Running pipeline…", expanded=True) as status:

                # ── Step 1: Parse ──────────────────────────────
                st.write("📄 Parsing file…")
                parser               = get_parser()
                raw_blocks, embedded_links = parser.parse_file(str(tmp_path))
                clean_text           = parser.restructure_data(raw_blocks)

                if not clean_text or not clean_text.strip():
                    st.error("Could not extract text. Is the PDF image-only / scanned?")
                    st.stop()
                st.write(
                    f"✅ Extracted {len(clean_text)} characters"
                    + (f", {len(embedded_links)} embedded links" if embedded_links else "")
                )

                # ── Step 2: Detect doc type ────────────────────
                st.write("🔍 Detecting document type…")
                extractor = get_extractor()
                doc_type  = extractor.detect_document_type(clean_text)
                if doc_type != 'resume':
                    st.error(f"Document classified as '{doc_type}', not a resume.")
                    st.stop()
                st.write(f"✅ Document type: {doc_type}")

                # Step 3 — LLM extraction (cached per file)
                if cache_key in st.session_state:
                    structured_json = st.session_state[cache_key]
                    st.write("✅ Structured data (from cache — instant)")
                else:
                    st.write("🤖 Extracting structured data with Ollama…")
                    st.caption("Takes 15–30s on first run. Cached on repeat.")
                    structured_json = extractor.extract_structured_data(
                        clean_text, embedded_links
                    )
                    if not structured_json:
                        st.error("LLM extraction failed. Is Ollama running? → ollama serve")
                        st.stop()
                    st.session_state[cache_key] = structured_json
                    st.write("✅ Structured data extracted")

                # Step 4 — Find job requirements
                st.write(f"📋 Loading requirements for '{selected_role}'…")
                scorer           = get_scorer()
                job_requirements = None
                for category, roles in scorer.roles.items():
                    if selected_role in roles:
                        job_requirements = roles[selected_role]
                        break

                if not job_requirements:
                    st.error(f"No requirements found for '{selected_role}'")
                    st.stop()
                st.write("✅ Job requirements loaded")

                # ── Step 5: ATS Scoring ────────────────────────
                st.write("📊 Scoring…")
                results = scorer.analyze_resume(
                    resume_data=clean_text,
                    structured_json=structured_json,
                    job_requirements=job_requirements
                )

                # ── Step 6: Lưu vào Supabase ──────────────────
                st.write("💾 Saving to database…")
                try:
                    contact = structured_json.get("contact", {}) or {}

                    # 6a. Upsert candidate
                    candidate = upsert_candidate(
                        file_name=uploaded_file.name,
                        file_content=file_bytes,
                        full_name=structured_json.get("full_name"),
                        email=contact.get("email"),
                        phone=contact.get("phone"),
                        total_exp_years=structured_json.get("total_exp_years"),
                    )
                    candidate_id = candidate["id"] if candidate else None

                    if candidate_id:
                        # 6b. Upsert extracted profile
                        upsert_extracted_profile(
                            candidate_id=candidate_id,
                            raw_json=structured_json,
                        )

                        # 6c. Save ATS analysis
                        analysis_record = save_resume_analysis(
                            candidate_id=candidate_id,
                            job_role=selected_role,
                            job_category=selected_cat,
                            section_scores=results["section_scores"],
                            suggestions=results["suggesstion"],
                            clean_text=clean_text,
                        )
                        analysis_id = analysis_record["id"] if analysis_record else None

                        # 6d. Save job comparison (ATS-only, SBERT = None cho đến khi AI chạy)
                        keyword_result = results["suggesstion"].get("skills_suggestions", [])
                        found_skills   = structured_json.get("skills", {}).get("technical", [])
                        missing_skills = job_requirements.get("required_skills", [])

                        save_job_comparison(
                            candidate_id=candidate_id,
                            job_role=selected_role,
                            job_category=selected_cat,
                            ats_score=results["section_scores"]["ats_score"],
                            sbert_score=None,
                            final_score=results["section_scores"]["ats_score"],
                            found_skills=found_skills,
                            missing_skills=missing_skills,
                        )

                        # Lưu IDs vào session để dùng cho feedback
                        st.session_state["last_candidate_id"] = candidate_id
                        st.session_state["last_analysis_id"]  = analysis_id

                        st.write(f"✅ Saved! Candidate ID: {candidate_id}")
                    else:
                        st.write("⚠️ Skipped DB save (candidate upsert failed)")

                except Exception as db_err:
                    # Không để lỗi DB làm fail toàn bộ pipeline
                    st.write(f"⚠️ DB warning (analysis still shown): {db_err}")

                status.update(label="Analysis complete!", state="complete")

            st.session_state["std_analysis"] = {
                "structured":     structured_json,
                "scores":         results["section_scores"],
                "suggestions":    results["suggesstion"],
                "role":           selected_role,
                "clean_text":     clean_text,
                "embedded_links": embedded_links,
            }

        except Exception as e:
            st.error(f"Pipeline error: {e}")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    # ── Render results ─────────────────────────────────────────
    result = st.session_state.get("std_analysis")
    if result:
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

        # ── Agent Calibration (Feedback) ───────────────────────
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
                vote_value = st.session_state.get("_vote", "neutral")
                ats_score  = scores.get("ats_score")

                if not candidate_id:
                    st.warning("⚠️ No candidate in session. Run analysis first.")
                else:
                    try:
                        save_feedback_vote(
                            candidate_id=candidate_id,
                            analysis_id=analysis_id,
                            vote=vote_value,
                            notes=feedback_text if feedback_text.strip() else None,
                            ai_score=float(ats_score) if ats_score else None,
                            agreed=(vote_value == "up"),
                        )
                        st.toast("✅ Feedback saved to database!")

                        # Reset vote sau khi submit
                        st.session_state.pop("_vote", None)

                    except Exception as fb_err:
                        st.error(f"Could not save feedback: {fb_err}")


