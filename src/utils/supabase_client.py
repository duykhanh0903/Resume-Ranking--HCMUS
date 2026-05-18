"""
src/utils/supabase_client.py
────────────────────────────
Supabase client singleton + helper methods cho toàn bộ RecruitAI.
Tất cả các router và module chỉ cần import từ file này.
"""

import os
import hashlib
import json
from typing import Optional, Dict, Any, List

from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
# 1. KHỞI TẠO CLIENT (Singleton)
# ──────────────────────────────────────────────

_supabase: Optional[Client] = None

def get_supabase() -> Client:
    """Trả về Supabase client duy nhất (lazy init)."""
    global _supabase
    if _supabase is None:
        url  = os.getenv("SUPABASE_URL")
        key  = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not url or not key:
            raise EnvironmentError(
                "Thiếu SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY trong file .env"
            )
        _supabase = create_client(url, key)
    return _supabase


# ──────────────────────────────────────────────
# 2. HELPERS DÙNG CHUNG
# ──────────────────────────────────────────────

def compute_md5(content: bytes) -> str:
    """Tính MD5 hash của nội dung file để detect duplicate."""
    return hashlib.md5(content).hexdigest()


def _serialize(obj: Any) -> Any:
    """Chuyển dict/list thành JSON string nếu cần (Supabase nhận JSONB)."""
    if isinstance(obj, (dict, list)):
        return obj          # supabase-py tự handle JSONB
    return obj


# ──────────────────────────────────────────────
# 3. CANDIDATES
# ──────────────────────────────────────────────

def upsert_candidate(
    file_name: str,
    file_content: bytes,
    full_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    total_exp_years: Optional[float] = None,
) -> Optional[Dict]:
    """
    Tạo hoặc cập nhật candidate dựa theo file_hash_md5.
    Trả về dict candidate (bao gồm id).
    Nếu MD5 đã tồn tại → trả về bản ghi cũ (không tạo trùng).
    """
    db = get_supabase()
    file_hash = compute_md5(file_content)

    # Kiểm tra duplicate
    existing = db.table("candidates")\
        .select("*")\
        .eq("file_hash_md5", file_hash)\
        .execute()

    if existing.data:
        print(f"[Supabase] Candidate đã tồn tại: {existing.data[0]['id']}")
        return existing.data[0]

    payload = {
        "file_name":       file_name,
        "file_hash_md5":   file_hash,
        "full_name":       full_name,
        "email":           email,
        "phone":           phone,
        "total_exp_years": total_exp_years,
    }
    result = db.table("candidates").insert(payload).execute()
    return result.data[0] if result.data else None


def get_candidate_by_id(candidate_id: int) -> Optional[Dict]:
    db = get_supabase()
    result = db.table("candidates").select("*").eq("id", candidate_id).execute()
    return result.data[0] if result.data else None


# ──────────────────────────────────────────────
# 4. EXTRACTED PROFILES
# ──────────────────────────────────────────────

def upsert_extracted_profile(
    candidate_id: int,
    raw_json: Dict,
) -> Optional[Dict]:
    """
    Lưu hoặc cập nhật extracted profile.
    Tự tách các trường từ raw_json của LLM.
    """
    db = get_supabase()

    contact    = raw_json.get("contact", {}) or {}
    skills     = raw_json.get("skills", {}) or {}
    education  = raw_json.get("education", [])
    experience = raw_json.get("experience", [])

    payload = {
        "candidate_id": candidate_id,
        "raw_json":     raw_json,
        "summary":      raw_json.get("summary"),
        "skills_tech":  skills.get("technical", []),
        "skills_soft":  skills.get("soft", []),
        "education":    education,
        "experience":   experience,
        "links":        contact.get("links", []),
    }

    # Upsert dựa trên candidate_id (UNIQUE constraint)
    result = db.table("extracted_profiles")\
        .upsert(payload, on_conflict="candidate_id")\
        .execute()
    return result.data[0] if result.data else None


def get_profile_by_candidate(candidate_id: int) -> Optional[Dict]:
    db = get_supabase()
    result = db.table("extracted_profiles")\
        .select("*")\
        .eq("candidate_id", candidate_id)\
        .execute()
    return result.data[0] if result.data else None


# ──────────────────────────────────────────────
# 5. RESUME ANALYSES (ATS Scoring)
# ──────────────────────────────────────────────

def save_resume_analysis(
    candidate_id: int,
    job_role: str,
    job_category: Optional[str],
    section_scores: Dict,
    suggestions: Dict,
    clean_text: Optional[str] = None,
) -> Optional[Dict]:
    """
    Lưu kết quả phân tích ATS vào resume_analyses.

    section_scores = {
        'ats_score': 78,
        'contact': 100, 'summary': 67, 'skills': 60,
        'experience': 75, 'education': 100, 'format': 85
    }
    suggestions = {
        'contact_suggestions': [...],
        'summary_suggestions': [...],
        ...
    }
    """
    db = get_supabase()
    payload = {
        "candidate_id":          candidate_id,
        "job_role":               job_role,
        "job_category":           job_category,
        "ats_score":              section_scores.get("ats_score"),
        "score_contact":          section_scores.get("contact"),
        "score_summary":          section_scores.get("summary"),
        "score_skills":           section_scores.get("skills"),
        "score_experience":       section_scores.get("experience"),
        "score_education":        section_scores.get("education"),
        "score_format":           section_scores.get("format"),
        "suggestions_contact":    suggestions.get("contact_suggestions", []),
        "suggestions_summary":    suggestions.get("summary_suggestions", []),
        "suggestions_skills":     suggestions.get("skills_suggestions", []),
        "suggestions_experience": suggestions.get("experience_suggestions", []),
        "suggestions_education":  suggestions.get("education_suggestions", []),
        "suggestions_format":     suggestions.get("format_suggestions", []),
        "clean_text":             clean_text,
    }
    result = db.table("resume_analyses")\
        .upsert(payload, on_conflict="candidate_id,job_role")\
        .execute()
    return result.data[0] if result.data else None


def get_analyses_by_role(job_role: str, limit: int = 50) -> List[Dict]:
    """Lấy danh sách phân tích theo vị trí, sắp xếp theo ATS score."""
    db = get_supabase()
    result = db.table("resume_analyses")\
        .select("*, candidates(full_name, email, total_exp_years)")\
        .eq("job_role", job_role)\
        .order("ats_score", desc=True)\
        .limit(limit)\
        .execute()
    return result.data or []


# ──────────────────────────────────────────────
# 6. JOB COMPARISONS (Ranking)
# ──────────────────────────────────────────────

def save_job_comparison(
    candidate_id: int,
    job_role: str,
    job_category: Optional[str],
    ats_score: Optional[float],
    sbert_score: Optional[float],
    final_score: Optional[float],
    found_skills: Optional[List] = None,
    missing_skills: Optional[List] = None,
) -> Optional[Dict]:
    """Lưu kết quả so sánh CV với JD (ATS + SBERT combined)."""
    db = get_supabase()
    payload = {
        "candidate_id":  candidate_id,
        "job_role":       job_role,
        "job_category":   job_category,
        "ats_score":      ats_score,
        "sbert_score":    sbert_score,
        "final_score":    final_score,
        "found_skills":   found_skills or [],
        "missing_skills": missing_skills or [],
        "status":         "pending",
    }
    result = db.table("job_comparisons")\
        .upsert(payload, on_conflict="candidate_id,job_role")\
        .execute()
    return result.data[0] if result.data else None


def get_ranking_by_role(job_role: str, limit: int = 100) -> List[Dict]:
    """Lấy bảng xếp hạng ứng viên theo vị trí, join thông tin candidates."""
    db = get_supabase()
    result = db.table("job_comparisons")\
        .select("*, candidates(full_name, email, total_exp_years)")\
        .eq("job_role", job_role)\
        .order("final_score", desc=True)\
        .limit(limit)\
        .execute()
    return result.data or []


def update_comparison_status(comparison_id: int, status: str) -> Optional[Dict]:
    """Cập nhật trạng thái xét duyệt: pending/shortlisted/rejected/hired."""
    db = get_supabase()
    result = db.table("job_comparisons")\
        .update({"status": status})\
        .eq("id", comparison_id)\
        .execute()
    return result.data[0] if result.data else None


# ──────────────────────────────────────────────
# 7. FEEDBACK VOTES (Agent Calibration)
# ──────────────────────────────────────────────

def save_feedback_vote(
    candidate_id: int,
    vote: str,                          # 'up' | 'down' | 'neutral'
    analysis_id: Optional[int] = None,
    notes: Optional[str] = None,
    recruiter_tag: Optional[str] = None,
    ai_score: Optional[float] = None,
    agreed: Optional[bool] = None,
) -> Optional[Dict]:
    """Lưu phản hồi của HR về kết quả phân tích AI."""
    db = get_supabase()
    assert vote in ("up", "down", "neutral"), "vote phải là 'up', 'down', hoặc 'neutral'"
    payload = {
        "candidate_id":  candidate_id,
        "analysis_id":   analysis_id,
        "vote":           vote,
        "notes":          notes,
        "recruiter_tag":  recruiter_tag,
        "ai_score":       ai_score,
        "agreed":         agreed,
    }
    result = db.table("feedback_votes").insert(payload).execute()
    return result.data[0] if result.data else None


def get_feedback_stats() -> Dict:
    """Thống kê tỉ lệ đồng ý / không đồng ý với AI."""
    db = get_supabase()
    result = db.table("feedback_votes").select("vote, agreed").execute()
    data   = result.data or []
    total  = len(data)
    up     = sum(1 for r in data if r["vote"] == "up")
    down   = sum(1 for r in data if r["vote"] == "down")
    agreed = sum(1 for r in data if r.get("agreed") is True)
    return {
        "total":        total,
        "up":           up,
        "down":         down,
        "neutral":      total - up - down,
        "agreed_count": agreed,
        "agree_rate":   round(agreed / total * 100, 1) if total else 0,
    }


# ──────────────────────────────────────────────
# 8. JOB SEARCH HISTORY
# ──────────────────────────────────────────────

def save_job_search(
    keyword: str,
    location: Optional[str],
    portals_result: List[Dict],
) -> Optional[Dict]:
    """Lưu một lần tìm kiếm job vào lịch sử."""
    db = get_supabase()
    payload = {
        "keyword":        keyword,
        "location":       location,
        "portals_result": portals_result,
    }
    result = db.table("job_search_history").insert(payload).execute()
    return result.data[0] if result.data else None


def get_recent_job_searches(limit: int = 20) -> List[Dict]:
    """Lấy lịch sử tìm kiếm gần nhất."""
    db = get_supabase()
    result = db.table("job_search_history")\
        .select("*")\
        .order("created_at", desc=True)\
        .limit(limit)\
        .execute()
    return result.data or []


def get_trending_keywords(limit: int = 10) -> List[Dict]:
    """Top từ khóa được tìm nhiều nhất (dùng cho Analytics)."""
    db = get_supabase()
    # Supabase không có GROUP BY trực tiếp qua SDK → dùng RPC hoặc xử lý Python
    result = db.table("job_search_history").select("keyword").execute()
    data   = result.data or []
    from collections import Counter
    counts = Counter(r["keyword"] for r in data)
    return [{"keyword": k, "count": v} for k, v in counts.most_common(limit)]


# ──────────────────────────────────────────────
# 9. RESUME BUILDS
# ──────────────────────────────────────────────

def save_resume_build(
    candidate_name: str,
    template: str,
    engine_data: Dict,              # Toàn bộ data dict đã format từ builder.py
) -> Optional[Dict]:
    """Lưu thông tin resume vừa được build."""
    db = get_supabase()
    personal = engine_data.get("personal_info", {})
    payload = {
        "candidate_name": candidate_name,
        "template":       template,
        "personal_info":  personal,
        "summary":        engine_data.get("summary"),
        "skills":         engine_data.get("skills"),
        "experience":     engine_data.get("experience"),
        "education":      engine_data.get("education"),
        "file_name":      f"Resume_{candidate_name.replace(' ', '_')}.docx",
    }
    result = db.table("resume_builds").insert(payload).execute()
    return result.data[0] if result.data else None


def get_recent_builds(limit: int = 20) -> List[Dict]:
    db = get_supabase()
    result = db.table("resume_builds")\
        .select("id, created_at, candidate_name, template, file_name")\
        .order("created_at", desc=True)\
        .limit(limit)\
        .execute()
    return result.data or []


# ──────────────────────────────────────────────
# 10. DASHBOARD ANALYTICS
# ──────────────────────────────────────────────

def get_dashboard_stats() -> Dict:
    """
    Lấy các chỉ số tổng hợp cho trang Dashboard.
    Trả về dict với các key: total_candidates, avg_ats, total_analyses,
    total_searches, total_builds, feedback_stats.
    """
    db = get_supabase()

    # Tổng số candidates
    cands = db.table("candidates").select("id", count="exact").execute()
    total_candidates = cands.count or 0

    # Trung bình ATS score
    analyses = db.table("resume_analyses").select("ats_score").execute()
    scores   = [r["ats_score"] for r in (analyses.data or []) if r["ats_score"] is not None]
    avg_ats  = round(sum(scores) / len(scores), 1) if scores else 0

    # Tổng số lần phân tích
    total_analyses = len(analyses.data or [])

    # Tổng job searches
    searches = db.table("job_search_history").select("id", count="exact").execute()
    total_searches = searches.count or 0

    # Tổng resume builds
    builds = db.table("resume_builds").select("id", count="exact").execute()
    total_builds = builds.count or 0

    # Feedback stats
    feedback = get_feedback_stats()

    return {
        "total_candidates": total_candidates,
        "avg_ats_score":    avg_ats,
        "total_analyses":   total_analyses,
        "total_searches":   total_searches,
        "total_builds":     total_builds,
        "feedback":         feedback,
    }
