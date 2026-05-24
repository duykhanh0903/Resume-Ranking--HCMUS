import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import tempfile, shutil
from pathlib import Path

from src.engine.agent.recruiter_agent import RecruitAIAgent
from src.engine.tools.sbert_tools import calculate_overall_match
from src.utils.parser import ResumeBlockParser
from src.utils.extractor import ResumeExtractor
from src.utils.configs.job_role import JOB_ROLES
from dotenv import load_dotenv

_parser = ResumeBlockParser()
_extractor = ResumeExtractor(model_name='llama3')

load_dotenv()

router = APIRouter()

# Hàm lấy danh sách Key an toàn
def get_all_groq_keys():
    return [os.getenv(f"GROQ_API_KEY_{i}") for i in range(1, 6) if os.getenv(f"GROQ_API_KEY_{i}")]

keys = get_all_groq_keys()
if not keys:
    raise RuntimeError("GROQ_API_KEY_X missing in .env file")

# Khởi tạo Agent với key đầu tiên (hoặc có thể viết logic xoay vòng key tại đây)
recruiter_agent = RecruitAIAgent(api_key=keys[0])

@router.post("/analyze_ai")
async def analyze_with_ai(
    job_category: str = Form(...),
    job_role: str = Form(...),
    resume_file: UploadFile = File(...)
):
    # 1. Lấy JD từ config
    jd_skills = []
    if job_category in JOB_ROLES and job_role in JOB_ROLES[job_category]:
        jd_skills = JOB_ROLES[job_category][job_role].get("required_skills", [])
    
    if not jd_skills:
        raise HTTPException(status_code=400, detail="Không tìm thấy JD cho vị trí này.")

    # 2. Xử lý File CV thật
    file_bytes = await resume_file.read()
    tmp_dir = tempfile.mkdtemp()
    tmp_path = Path(tmp_dir) / resume_file.filename
    
    try:
        tmp_path.write_bytes(file_bytes)
        
        # Parse & Extract
        raw_blocks, embedded_links = _parser.parse_file(str(tmp_path))
        clean_text = _parser.restructure_data(raw_blocks)
        resume_json = _extractor.extract_structured_data(clean_text, embedded_links)
        
        if not resume_json:
            raise HTTPException(status_code=500, detail="Lỗi trích xuất dữ liệu từ CV.")

        # 3. Tính điểm SBERT thật
        resume_skills = resume_json.get("skills", {}).get("technical", [])
        real_sbert_score = calculate_overall_match(jd_skills, resume_skills)

        # 4. Truyền dữ liệu thật cho Agent
        jd_dict = {"required_skills": jd_skills}
        
        # Ép Agent sử dụng điểm thực tế thay vì tự tính
        result = await recruiter_agent.run_analysis(
            jd=jd_dict, 
            resume=resume_json, 
            raw_text=clean_text,
            calculated_score=real_sbert_score # Thêm tham số này vào hàm run_analysis của Agent
        )
        
        return {
            "status": "success",
            "extracted_profile": resume_json, # Trả về để UI hiển thị thông tin ứng viên
            "analysis": result
        }
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)