from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List

from src.utils.supabase_client import get_supabase

router = APIRouter()


# ── helpers ──────────────────────────────────────────────────────────
def _compute_final(ats: Optional[float], sbert: Optional[float], w_ats: int) -> float:
    """
    ats    : 0-100
    sbert  : 0-1  (None if not run)
    w_ats  : 0-100 percent
    → final: 0-100
    """
    ats_val = float(ats or 0)
    if sbert is None:
        return round(ats_val, 1)
    ai_val = float(sbert) * 100
    w_ai = 100 - w_ats
    return round(ats_val * (w_ats / 100) + ai_val * (w_ai / 100), 1)


# ── schemas ───────────────────────────────────────────────────────────
class StatusUpdate(BaseModel):
    status: str   # pending | shortlisted | rejected | hired


# ── endpoints ─────────────────────────────────────────────────────────

@router.get("/roles")
def list_roles():
    """Distinct job roles that exist in job_comparisons."""
    db = get_supabase()
    rows = db.table("job_comparisons").select("job_role").execute().data or []
    roles = sorted(set(r["job_role"] for r in rows if r.get("job_role")))
    return {"status": "success", "data": roles}


@router.get("/candidates")
def list_candidates(
    job_role:   Optional[str] = Query(None),
    status:     Optional[str] = Query(None),
    search:     Optional[str] = Query(None),
    sort_by:    str            = Query("final_score"),   # ats_score | sbert_score | final_score | name
    sort_dir:   str            = Query("desc"),           # asc | desc
    w_ats:      int            = Query(50, ge=0, le=100),
    limit:      int            = Query(100, ge=1, le=500),
    offset:     int            = Query(0, ge=0),
):
    """
    Returns ranked candidates, computing final score on the fly.
    """
    db = get_supabase()

    q = db.table("job_comparisons").select(
        "id, job_role, job_category, ats_score, sbert_score, final_score,"
        "found_skills, missing_skills, status, created_at,"
        "candidates(id, full_name, email, phone, total_exp_years, file_name)"
    )

    if job_role:
        q = q.eq("job_role", job_role)
    if status:
        q = q.eq("status", status)

    rows = q.execute().data or []

    # Enrich with computed final score
    for r in rows:
        r["_final"] = _compute_final(r.get("ats_score"), r.get("sbert_score"), w_ats)
        r["_ai_pct"] = round(float(r["sbert_score"]) * 100, 1) if r.get("sbert_score") is not None else None

    # Search filter (name / email)
    if search:
        s = search.lower()
        rows = [
            r for r in rows
            if s in (r.get("candidates") or {}).get("full_name", "").lower()
            or s in (r.get("candidates") or {}).get("email", "").lower()
        ]

    # Sort
    reverse = sort_dir == "desc"
    if sort_by == "ats_score":
        rows.sort(key=lambda r: float(r.get("ats_score") or 0), reverse=reverse)
    elif sort_by == "sbert_score":
        rows.sort(key=lambda r: float(r.get("sbert_score") or 0) * 100, reverse=reverse)
    elif sort_by == "name":
        rows.sort(key=lambda r: (r.get("candidates") or {}).get("full_name", "").lower(), reverse=reverse)
    else:
        rows.sort(key=lambda r: r["_final"], reverse=reverse)

    total = len(rows)
    rows  = rows[offset: offset + limit]

    return {
        "status": "success",
        "total":  total,
        "data":   rows,
    }


@router.put("/{comparison_id}/status")
def update_status(comparison_id: int, body: StatusUpdate):
    allowed = {"pending", "shortlisted", "rejected", "hired"}
    if body.status not in allowed:
        raise HTTPException(status_code=400, detail=f"status must be one of {allowed}")

    db = get_supabase()
    result = db.table("job_comparisons")\
        .update({"status": body.status})\
        .eq("id", comparison_id)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Comparison not found")

    return {"status": "success", "updated": result.data[0]}


@router.get("/stats")
def role_stats():
    """Per-role aggregate stats for the summary cards."""
    db = get_supabase()
    rows = db.table("job_comparisons").select(
        "job_role, ats_score, sbert_score, status"
    ).execute().data or []

    from collections import defaultdict
    buckets: dict = defaultdict(list)
    for r in rows:
        buckets[r["job_role"]].append(r)

    out = []
    for role, items in buckets.items():
        ats_vals = [float(i["ats_score"]) for i in items if i.get("ats_score") is not None]
        avg_ats  = round(sum(ats_vals) / len(ats_vals), 1) if ats_vals else 0
        status_counts = {"pending": 0, "shortlisted": 0, "rejected": 0, "hired": 0}
        for i in items:
            status_counts[i.get("status", "pending")] = status_counts.get(i.get("status", "pending"), 0) + 1

        out.append({
            "job_role":   role,
            "total":      len(items),
            "avg_ats":    avg_ats,
            "shortlisted": status_counts["shortlisted"],
            "hired":       status_counts["hired"],
        })

    out.sort(key=lambda x: x["total"], reverse=True)
    return {"status": "success", "data": out}