from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from src.utils.resume_template import ResumeBuilder

router = APIRouter()
builder = ResumeBuilder()

class ResumeInput(BaseModel):
    template: str
    name: str
    email: str
    phone: str
    linkedin: Optional[str] = ""
    title: str
    summary: str
    experience: List[Dict]
    education: List[Dict]
    skills: List[str]

@router.post("/generate")
async def generate_resume_endpoint(data: ResumeInput):
    try:
        # Tách chuỗi ngày tháng (VD: "Jan 2011 - 2013" -> "Jan 2011" và "2013")
        def parse_date(date_str):
            if "-" in date_str:
                parts = date_str.split("-", 1)
                return parts[0].strip(), parts[1].strip()
            return date_str.strip(), ""

        # Format lại Kinh nghiệm làm việc
        formatted_experience = []
        for exp in data.experience:
            start, end = parse_date(exp.get("date", ""))
            formatted_experience.append({
                "company": exp.get("company", ""),
                "position": exp.get("title", ""), # Map 'title' từ UI thành 'position' của Reference Template
                "start_date": start,
                "end_date": end,
                # Tách description thành các gạch đầu dòng
                "responsibilities": [line.strip() for line in exp.get("description", "").split('\n') if line.strip()],
                "description": "" 
            })

        # Format lại Học vấn
        formatted_education = []
        for edu in data.education:
            # Tách degree (VD: "PhD in AI" -> deg="PhD", field="in AI") để khớp template
            degree_raw = edu.get("degree", "")
            parts = degree_raw.split(" ", 1)
            deg = parts[0] if len(parts) > 0 else ""
            field = parts[1] if len(parts) > 1 else ""

            formatted_education.append({
                "school": edu.get("school", ""),
                "degree": deg,
                "field": field,
                "graduation_date": edu.get("date", ""),
                "gpa": ""
            })

        # Gộp tất cả thành cấu trúc mà Reference Template làm sẵn
        engine_data = {
            "template": data.template,
            "personal_info": {
                "full_name": data.name,
                "title": data.title,
                "email": data.email,
                "phone": data.phone,
                "location": "", # UI không có cái này nên để trống
                "linkedin": data.linkedin,
                "portfolio": ""
            },
            "summary": data.summary,
            "experience": formatted_experience,
            "education": formatted_education,
            "skills": {
                "technical": data.skills, # Đưa list skill phẳng vào danh mục technical
                "soft": [],
                "languages": [],
                "tools": []
            }
        }
        
        doc_stream = builder.generate_resume(engine_data)
        
        return StreamingResponse(
            doc_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=Resume_{data.name.replace(' ', '_')}.docx"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")