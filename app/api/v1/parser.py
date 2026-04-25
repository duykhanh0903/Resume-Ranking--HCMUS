from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Annotated
import tempfile
import shutil
import os
from pathlib import Path

from app.services.ocr import OCRService
from app.services.llm import LLMService
from app.schemas.resume import ResumeSchema
from app.core.config import settings

router = APIRouter(prefix="/v1", tags=["parser"])

@router.post("/parse", response_model=ResumeSchema)
async def parse_resume(file: Annotated[UploadFile, File(description="PDF or DOCX resume")]):
    if not file.filename or not file.filename.lower().endswith(('.pdf', '.docx')):
        raise HTTPException(400, "Only PDF/DOCX supported")

    temp_dir = None
    try:
        bytes_data = await file.read()
        if len(bytes_data) == 0:
            raise HTTPException(400, "Empty file")

        _, ext = os.path.splitext(file.filename.lower())
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir) / file.filename
        temp_path.write_bytes(bytes_data)

        text = OCRService.extract(bytes_data, ext)
        if not text or "Error" in text:
            raise HTTPException(500, "Text extraction failed")

        parsed = LLMService.parse_resume(text)
        return parsed
    finally:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)

