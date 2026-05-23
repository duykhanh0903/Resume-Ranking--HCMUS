"""
src/api/routers/analyzer.py  ← PHIÊN BẢN MỚI CÓ SUPABASE
────────────────────────────
Nhận CV upload → parse → extract → score ATS → lưu Supabase.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import hashlib

from src.utils.supabase_client import (
    upsert_candidate,
    upsert_extracted_profile,
    save_resume_analysis,
    save_job_comparison,
)

router = APIRouter()


@router.post("/analyze")
async def analyze_candidate_resume(
    job_role: str = Form(...),
    job_category: Optional[str] = Form(None),
    resume_file: UploadFile = File(...)
):
    """
    Endpoint nhận CV (PDF/DOCX) + vị trí ứng tuyển.
    Luồng: Upload → upsert_candidate → upsert_profile → save_analysis → response
    """
    # ── Đọc nội dung file ──
    file_content = await resume_file.read()

    # ── BƯỚC 1: Lưu candidate (tránh duplicate bằng MD5) ──
    candidate = upsert_candidate(
        file_name=resume_file.filename,
        file_content=file_content,
        # Các trường dưới đây sẽ được điền sau khi parse thực tế
        # Hiện tại để None, sẽ update sau khi extractor chạy
    )
    if not candidate:
        raise HTTPException(status_code=500, detail="Không thể lưu candidate vào database")

    candidate_id = candidate["id"]

    # ────────────────────────────────────────────────────────────
    # TODO: Thay mock data bên dưới bằng các module thực tế:
    #
    # from src.parser import ResumeBlockParser
    # from src.extractor import ResumeExtractor
    # from src.resume_analyzer import ResumeScorer
    #
    # parser = ResumeBlockParser()
    # raw_blocks = parser.parse_file_from_bytes(file_content, resume_file.filename)
    # clean_text = parser.restructure_data(raw_blocks)
    #
    # extractor = ResumeExtractor()
    # structured_json = extractor.extract_structured_data(clean_text)
    #
    # scorer = ResumeScorer()
    # job_requirements = scorer.roles[job_category][job_role]
    # analysis_result = scorer.analyze_resume(clean_text, structured_json, job_requirements)
    # ────────────────────────────────────────────────────────────

    # ── MOCK DATA (xóa khi tích hợp module thật) ──
    structured_json = {
        "full_name": "Alex Rivera",
        "contact": {
            "email": "alex@example.com",
            "phone": "0912345678",
            "links": ["linkedin.com/in/alexrivera"]
        },
        "summary": "6+ years experience in UI/UX and frontend development.",
        "total_exp_years": 6.0,
        "skills": {
            "technical": ["React", "Figma", "Tailwind CSS", "TypeScript"],
            "soft": ["Problem Solving", "Communication"]
        },
        "education": [{"degree": "B.S.", "field": "Interaction Design", "institution": "UC Berkeley", "graduation_year": "2018"}],
        "experience": [{"company": "Acme Corp", "role": "Senior UI Engineer", "period": "2020-01 to 2024-01", "description": "Led design system."}]
    }

    analysis_result = {
        "section_scores": {
            "ats_score": 85,
            "contact": 100, "summary": 67, "skills": 80,
            "experience": 75, "education": 100, "format": 85
        },
        "suggesstion": {
            "contact_suggestions": [],
            "summary_suggestions": ["Expand your professional summary"],
            "skills_suggestions": ["Missing: User Research"],
            "experience_suggestions": [],
            "education_suggestions": [],
            "format_suggestions": []
        }
    }
    clean_text = "Mock clean text content"
    # ── Kết thúc MOCK DATA ──

    # ── BƯỚC 2: Upsert extracted profile ──
    upsert_extracted_profile(
        candidate_id=candidate_id,
        raw_json=structured_json,
    )

    # ── BƯỚC 3: Cập nhật thông tin cơ bản vào candidates ──
    from src.utils.supabase_client import get_supabase
    db = get_supabase()
    db.table("candidates").update({
        "full_name":       structured_json.get("full_name"),
        "email":           structured_json.get("contact", {}).get("email"),
        "phone":           structured_json.get("contact", {}).get("phone"),
        "total_exp_years": structured_json.get("total_exp_years"),
    }).eq("id", candidate_id).execute()

    # ── BƯỚC 4: Lưu kết quả phân tích ATS ──
    analysis_record = save_resume_analysis(
        candidate_id=candidate_id,
        job_role=job_role,
        job_category=job_category,
        section_scores=analysis_result["section_scores"],
        suggestions=analysis_result["suggesstion"],
        clean_text=clean_text,
    )

    # ── BƯỚC 5: Lưu job comparison (để dùng cho ranking) ──
    skills_result = analysis_result["suggesstion"]
    save_job_comparison(
        candidate_id=candidate_id,
        job_role=job_role,
        job_category=job_category,
        ats_score=analysis_result["section_scores"]["ats_score"],
        sbert_score=None,       # Sẽ điền khi SBERT pipeline chạy
        final_score=analysis_result["section_scores"]["ats_score"],
        found_skills=structured_json.get("skills", {}).get("technical", []),
        missing_skills=[],
    )

    # ── Trả về response cho Streamlit ──
    return {
        "status": "success",
        "candidate_id": candidate_id,
        "analysis_id":  analysis_record["id"] if analysis_record else None,
        "extracted_profile": {
            "name":               structured_json.get("full_name"),
            "experience_summary": f"{structured_json.get('total_exp_years', 0)}+ Years Experience",
            "skills":             structured_json.get("skills", {}).get("technical", []),
            "education":          structured_json.get("education", [{}])[0].get("institution", "")
        },
        "analysis": {
            "match_score": analysis_result["section_scores"]["ats_score"],
            "reasoning":   "Analysis completed and saved to database.",
            "verified_strengths": [],
            "warnings": analysis_result["suggesstion"].get("skills_suggestions", []),
        }
    }
