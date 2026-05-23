from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import urllib.parse

from src.utils.resume_template import ResumeBuilder
from src.utils.supabase_client import save_resume_build

router  = APIRouter()
builder = ResumeBuilder()


class ResumeInput(BaseModel):
    template: str
    name:     str
    email:    str
    phone:    str
    linkedin: Optional[str] = ""
    title:    str
    summary:  str
    experience: List[Dict]
    education:  List[Dict]
    skills:     List[str]


@router.post("/generate")
async def generate_resume_endpoint(data: ResumeInput):
    try:
        def parse_date(date_str):
            if "-" in date_str:
                parts = date_str.split("-", 1)
                return parts[0].strip(), parts[1].strip()
            return date_str.strip(), ""

        formatted_experience = []
        for exp in data.experience:
            start, end = parse_date(exp.get("date", ""))
            formatted_experience.append({
                "company":          exp.get("company", ""),
                "position":         exp.get("title", ""),
                "start_date":       start,
                "end_date":         end,
                "responsibilities": [
                    line.strip()
                    for line in exp.get("description", "").split('\n')
                    if line.strip()
                ],
                "description": ""
            })

        formatted_education = []
        for edu in data.education:
            degree_raw = edu.get("degree", "")
            parts      = degree_raw.split(" ", 1)
            formatted_education.append({
                "school":          edu.get("school", ""),
                "degree":          parts[0] if parts else "",
                "field":           parts[1] if len(parts) > 1 else "",
                "graduation_date": edu.get("date", ""),
                "gpa":             ""
            })

        engine_data = {
            "template": data.template,
            "personal_info": {
                "full_name": data.name,
                "title":     data.title,
                "email":     data.email,
                "phone":     data.phone,
                "location":  "",
                "linkedin":  data.linkedin,
                "portfolio": ""
            },
            "summary":    data.summary,
            "experience": formatted_experience,
            "education":  formatted_education,
            "skills": {
                "technical": data.skills,
                "soft":      [],
                "languages": [],
                "tools":     []
            }
        }

        doc_stream = builder.generate_resume(engine_data)

        # ✅ Fix encoding: dùng RFC 5987 cho tên file Unicode
        safe_name = urllib.parse.quote(data.name.replace(' ', '_'))

        return StreamingResponse(
            doc_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": (
                    f"attachment; "
                    f"filename=\"Resume.docx\"; "
                    f"filename*=UTF-8''{safe_name}.docx"
                )
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")