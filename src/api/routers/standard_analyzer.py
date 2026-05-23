from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import tempfile, shutil, hashlib
from pathlib import Path

from src.utils.parser import ResumeBlockParser
from src.utils.extractor import ResumeExtractor
from src.utils.resume_analyzer import ResumeScorer
from src.utils.configs.job_role import JOB_ROLES
from src.utils.supabase_client import (
    upsert_candidate,
    upsert_extracted_profile,
    save_resume_analysis,
    save_job_comparison,
)

router = APIRouter()

# Module-level singletons — khởi tạo một lần, dùng lại cho mọi request
_parser    = ResumeBlockParser()
_extractor = ResumeExtractor(model_name='llama3')
_scorer    = ResumeScorer()


# Thêm vào src/api/routers/standard_analyzer.py

from pydantic import BaseModel

class FeedbackInput(BaseModel):
    candidate_id: int
    analysis_id:  Optional[int]
    vote:         str   # "up" | "down" | "neutral"
    notes:        Optional[str]
    ai_score:     Optional[float]
    agreed:       Optional[bool]

@router.post("/feedback")
def submit_feedback(data: FeedbackInput):
    from src.utils.supabase_client import save_feedback_vote
    result = save_feedback_vote(
        candidate_id=data.candidate_id,
        analysis_id=data.analysis_id,
        vote=data.vote,
        notes=data.notes,
        ai_score=data.ai_score,
        agreed=data.agreed,
    )
    if not result:
        raise HTTPException(status_code=500, detail="Không thể lưu feedback")
    return {"status": "success", "id": result["id"]}

@router.post("/analyze")
async def standard_analyze(
    job_category: str  = Form(...),
    job_role:     str  = Form(...),
    resume_file:  UploadFile = File(...),
):
    """
    Nhận CV (PDF/DOCX) + job_category + job_role.
    Trả về ATS scores, suggestions, extracted profile, candidate_id, analysis_id.
    """

    # ── 1. Đọc file vào memory ──────────────────────────────
    file_bytes = await resume_file.read()
    file_hash  = hashlib.md5(file_bytes).hexdigest()

    # ── 2. Ghi ra file tạm để parser đọc ────────────────────
    tmp_dir  = tempfile.mkdtemp()
    tmp_path = Path(tmp_dir) / resume_file.filename

    try:
        tmp_path.write_bytes(file_bytes)

        # ── 3. Parse ─────────────────────────────────────────
        raw_blocks, embedded_links = _parser.parse_file(str(tmp_path))
        clean_text = _parser.restructure_data(raw_blocks)

        if not clean_text or not clean_text.strip():
            raise HTTPException(
                status_code=422,
                detail="Không thể trích xuất văn bản. File có thể là ảnh scan."
            )

        # ── 4. Detect document type ───────────────────────────
        doc_type = _extractor.detect_document_type(clean_text)
        if doc_type != 'resume':
            raise HTTPException(
                status_code=422,
                detail=f"Tài liệu được phân loại là '{doc_type}', không phải resume."
            )

        # ── 5. LLM extraction ─────────────────────────────────
        structured_json = _extractor.extract_structured_data(clean_text, embedded_links)
        if not structured_json:
            raise HTTPException(
                status_code=503,
                detail="LLM extraction thất bại. Đảm bảo Ollama đang chạy."
            )

        # ── 6. Tìm job requirements ───────────────────────────
        job_requirements = None
        for category, roles in _scorer.roles.items():
            if job_role in roles:
                job_requirements = roles[job_role]
                break

        if not job_requirements:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy yêu cầu cho vị trí '{job_role}'."
            )

        # ── 7. ATS Scoring ────────────────────────────────────
        results = _scorer.analyze_resume(
            resume_data=clean_text,
            structured_json=structured_json,
            job_requirements=job_requirements,
        )

        # ── 8. Lưu vào Supabase ───────────────────────────────
        candidate_id = None
        analysis_id  = None

        try:
            contact = structured_json.get("contact", {}) or {}

            candidate = upsert_candidate(
                file_name=resume_file.filename,
                file_content=file_bytes,
                full_name=structured_json.get("full_name"),
                email=contact.get("email"),
                phone=contact.get("phone"),
                total_exp_years=structured_json.get("total_exp_years"),
            )
            candidate_id = candidate["id"] if candidate else None

            if candidate_id:
                upsert_extracted_profile(
                    candidate_id=candidate_id,
                    raw_json=structured_json,
                )

                analysis_record = save_resume_analysis(
                    candidate_id=candidate_id,
                    job_role=job_role,
                    job_category=job_category,
                    section_scores=results["section_scores"],
                    suggestions=results["suggesstion"],
                    clean_text=clean_text,
                )
                analysis_id = analysis_record["id"] if analysis_record else None

                found_skills   = structured_json.get("skills", {}).get("technical", [])
                missing_skills = job_requirements.get("required_skills", [])

                save_job_comparison(
                    candidate_id=candidate_id,
                    job_role=job_role,
                    job_category=job_category,
                    ats_score=results["section_scores"]["ats_score"],
                    sbert_score=None,
                    final_score=results["section_scores"]["ats_score"],
                    found_skills=found_skills,
                    missing_skills=missing_skills,
                )

        except Exception as db_err:
            # Lỗi DB không được làm fail toàn bộ pipeline
            print(f"[DB Warning] {db_err}")

        # ── 9. Build response ─────────────────────────────────
        return {
            "status":        "success",
            "candidate_id":  candidate_id,
            "analysis_id":   analysis_id,
            "doc_type":      doc_type,
            "embedded_links": embedded_links,
            "structured_profile": structured_json,
            "section_scores":     results["section_scores"],
            "suggestions":        results["suggesstion"],
        }

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@router.get("/job-roles")
def get_job_roles():
    """Trả về toàn bộ danh mục và vị trí để Streamlit populate dropdown."""
    return {
        "status": "success",
        "data": {
            category: list(roles.keys())
            for category, roles in JOB_ROLES.items()
        }
    }