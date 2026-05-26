import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import tempfile, shutil
from pathlib import Path

from src.engine.agent.recruiter_agent import RecruitAIAgent
from src.engine.tools.sbert_tools import calculate_overall_match
from src.utils.parser import ResumeBlockParser
from src.utils.extractor import ResumeExtractor
from src.utils.configs.job_role import JOB_ROLES
from src.utils.configs.job_descriptions import JOB_DESCRIPTIONS

import gc
from src.engine.tools.sbert_tools import get_embeddings, calibrate_sbert_score
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from dotenv import load_dotenv

from src.utils.supabase_client import (
    upsert_candidate,
    upsert_extracted_profile,
    save_job_comparison
)

_parser = ResumeBlockParser()
_extractor = ResumeExtractor()

load_dotenv()

router = APIRouter()

# Hàm lấy danh sách Key an toàn
def get_all_groq_keys():
    return [os.getenv(f"GROQ_API_KEY_{i}") for i in range(1, 6) if os.getenv(f"GROQ_API_KEY_{i}")]

keys = get_all_groq_keys()
if not keys:
    raise RuntimeError("GROQ_API_KEY_X missing in .env file")

# Khởi tạo Agent với key
agents_pool = [RecruitAIAgent(api_key=k) for k in keys]

@router.post("/analyze_ai")
async def analyze_with_ai(
    job_category: str = Form(...),
    job_role: str = Form(...),
    resume_file: UploadFile = File(...)
):
    # 1. Lấy JD từ config
    jd_text = ""
    if job_category in JOB_DESCRIPTIONS and job_role in JOB_DESCRIPTIONS[job_category]:
        jd_text = JOB_DESCRIPTIONS[job_category][job_role]
        
    if not jd_text:
        raise HTTPException(status_code=400, detail="Không tìm thấy văn bản mô tả JD cho vị trí này.")

    # 2. Đọc và xử lý file CV tải lên
    file_bytes = await resume_file.read()
    tmp_dir = tempfile.mkdtemp()
    tmp_path = Path(tmp_dir) / resume_file.filename
    
    try:
        tmp_path.write_bytes(file_bytes)
        raw_blocks, embedded_links = _parser.parse_file(str(tmp_path))
        clean_text = _parser.restructure_data(raw_blocks)

        if not clean_text or len(clean_text.strip()) < 10:
            raise HTTPException(
                status_code=422, 
                detail="Không thể trích xuất văn bản. File có thể là ảnh scan."
            )
        
        doc_type = _extractor.detect_document_type(clean_text)
        if doc_type != 'resume':
            raise HTTPException(
                status_code=400, 
                detail=f"Tài liệu tải lên dường như không phải CV (Phát hiện: {doc_type.upper()}). Vui lòng tải lên CV hợp lệ."
            )
        
        # ── THỰC HIỆN ĐỒNG THỜI 2 KIỂU TRÍCH XUẤT ──
        # Kiểu 1: Trích xuất JSON có cấu trúc để hiển thị thông tin ứng viên lên giao diện (UI)
        resume_json = _extractor.extract_structured_data(clean_text, embedded_links)
        
        # Kiểu 2: Trích xuất dạng khối văn bản liên tục phục vụ cho mô hình SBERT fine-tuned
        resume_narrative = _extractor.extract_narrative_text(clean_text)

        if not resume_json:
            raise HTTPException(status_code=500, detail="Lỗi trích xuất cấu hình JSON.")

        # 3. Tính điểm bằng mô hình SBERT Fine-tuned chuẩn xác (Đoạn văn vs Đoạn văn)
        # Mã hóa chuỗi văn bản dài theo đúng cấu trúc lúc train
        jd_embedding = get_embeddings([jd_text])
        resume_embedding = get_embeddings([resume_narrative])
        
        # Tính toán độ tương đồng Cosine
        similarity = cosine_similarity(jd_embedding, resume_embedding)[0][0]
        raw_score = float(similarity)
        real_sbert_score = calibrate_sbert_score(raw_score)

        # 4. Truyền toàn bộ ngữ cảnh thực tế cho LangGraph Agent
        # Lấy mảng kỹ năng từ job_role cũ gửi cho Agent để nó dùng làm danh sách kiểm tra (Checklist)
        jd_skills = JOB_ROLES[job_category][job_role].get("required_skills", [])
        jd_dict = {"required_skills": jd_skills, "full_description": jd_text}
        
        result = {}
        # 🌟 CƠ CHẾ XOAY VÒNG KEY (FALLBACK)
        for i, agent in enumerate(agents_pool):
            try:
                result = await agent.run_analysis(
                    jd=jd_dict, 
                    resume=resume_json, 
                    raw_text=clean_text,
                    calculated_score=real_sbert_score
                )
                
                # Kiểm tra xem Groq có trả về chuỗi JSON chứa lỗi (ví dụ: HTTP 429 Rate Limit) không
                if isinstance(result, dict) and "error" in result:
                    print(f"⚠️ [Cảnh báo] Key số {i+1} gặp lỗi: {result['error'][:50]}... Đang tự động chuyển sang Key tiếp theo!")
                    continue # Bỏ qua, chạy vòng lặp với Agent tiếp theo
                
                # Nếu chạy mượt, không có chữ "error", lập tức thoát vòng lặp
                break
                
            except Exception as e:
                # Bắt luôn cả những lỗi mạng bất ngờ khiến thư viện crash
                print(f"⚠️ [Cảnh báo] Key số {i+1} văng lỗi exception: {e}. Đang chuyển sang Key tiếp theo!")
                continue

        # In Debug để theo dõi
        print("====== DEBUG AGENT RESULT ======")
        if isinstance(result, dict) and "error" not in result and result:
            print(f"✅ Phân tích thành công!")
        else:
            print("❌ Tất cả 5 Keys đều đã cạn kiệt Token hoặc bị lỗi hệ thống!")
            # Trả về một block an toàn để UI không bị sập (hiện 0%)
            result = {
                "match_score": real_sbert_score,
                "reasoning": "Hệ thống AI hiện đang quá tải do vượt giới hạn API. Điểm số phía trên được tính toán hoàn toàn bằng SBERT Model. Vui lòng quay lại tính năng này sau 10-15 phút.",
                "verified_strengths": [],
                "warnings": ["Tất cả API keys dự phòng đều đã chạm ngưỡng giới hạn."],
                "interview_suggestions": []
            }
        print("================================")

        candidate_id = None
        try:
            contact = resume_json.get("contact", {}) or {}
            
            # 5.1 Lưu/Cập nhật Candidate
            candidate = upsert_candidate(
                file_name=resume_file.filename,
                file_content=file_bytes,
                full_name=resume_json.get("full_name"),
                email=contact.get("email"),
                phone=contact.get("phone"),
                total_exp_years=resume_json.get("total_exp_years"),
            )
            
            if candidate and "id" in candidate:
                candidate_id = candidate["id"]
                
                # 5.2 Lưu Extracted Profile (JSON của Ollama)
                upsert_extracted_profile(
                    candidate_id=candidate_id,
                    raw_json=resume_json
                )

                # 5.3 LƯU ĐIỂM SBERT VÀO BẢNG JOB_COMPARISONS
                found_skills = resume_json.get("skills", {}).get("technical", [])
                
                save_job_comparison(
                    candidate_id=candidate_id,
                    job_role=job_role,
                    job_category=job_category,
                    ats_score=None, # Luồng này là luồng AI, ATS Score để null
                    sbert_score=real_sbert_score, # <--- ĐÃ LƯU ĐIỂM SBERT
                    final_score=real_sbert_score, # Lấy điểm SBERT làm điểm Final để rank
                    found_skills=found_skills,
                    missing_skills=result.get("warnings", []) # Lấy những kỹ năng thiếu từ Agent
                )
        except Exception as db_err:
            print(f"⚠️ [DB Warning] Không thể lưu vào DB: {db_err}")
        
        return {
            "status": "success",
            "candidate_id": candidate_id,
            "analysis_id": None,
            "extracted_profile": resume_json, 
            "analysis": result
        }
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)