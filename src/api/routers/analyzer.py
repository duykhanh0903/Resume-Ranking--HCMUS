from fastapi import APIRouter, UploadFile, File, Form
from typing import List

router = APIRouter()

@router.post("/analyze")
async def analyze_candidate_resume(
    job_role: str = Form(...),
    resume_file: UploadFile = File(...)
):
    """
    Endpoint nhận file CV (PDF/DOCX) và Vị trí ứng tuyển.
    Sau này, logic OCR, Regex, Llama 3 và SBERT sẽ được gọi ở đây.
    """
    
    # In ra terminal để debug xem có nhận được file không
    print(f"Đã nhận file: {resume_file.filename} cho vị trí: {job_role}")
    
    # -------------------------------------------------------------------
    # TODO: Tương lai bạn sẽ nhúng các module ở src/engine/ vào đây:
    # 1. raw_text = parser.extract_text(resume_file.file)
    # 2. structured_data = agent.extract_with_llama3(raw_text)
    # 3. match_score = model_wrapper.get_sbert_score(structured_data, job_role)
    # -------------------------------------------------------------------

    # Dữ liệu giả (Mock) trả về cho Streamlit render UI
    return {
        "status": "success",
        "extracted_profile": {
            "name": "Alex Rivera",
            "experience_summary": "6+ Years Experience • San Francisco, CA",
            "skills": ["UI/UX Design", "Figma", "React", "Tailwind CSS"],
            "education": "B.S. Interaction Design, UC Berkeley"
        },
        "analysis": {
            "match_score": 85,
            "reasoning": "Highly qualified candidate with strong overlap in visual design and frontend knowledge.",
            "verified_strengths": [
                "Candidate has extensive experience building Design Systems.",
                "Location match: Based in San Francisco."
            ],
            "warnings": [
                "Limited experience mentioned regarding User Research methodologies."
            ]
        }
    }