import os
from fastapi import APIRouter, Body, HTTPException
from src.engine.agent.recruiter_agent import RecruitAIAgent
from dotenv import load_dotenv

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
    jd_json: dict = Body(..., description="JSON chứa thông tin Job Description"),
    resume_json: dict = Body(..., description="JSON chứa thông tin Resume"),
    raw_text: str = Body("", description="Văn bản thô của CV để quét chuyên sâu")
):
    if not recruiter_agent:
        raise HTTPException(status_code=500, detail="Thiếu GROQ_API_KEY trong môi trường.")
        
    try:
        result = await recruiter_agent.run_analysis(jd_json, resume_json, raw_text)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        return {
            "status": "success",
            "analysis": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))