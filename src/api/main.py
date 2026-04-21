from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import analyzer
from src.api.routers import jobsearch

app = FastAPI(
    title="RecruitAI Backend API",
    description="Core Engine cho hệ thống phân tích và xếp hạng CV",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyzer.router, prefix="/api/v1/analyzer", tags=["Resume Analysis"])
app.include_router(jobsearch.router, prefix="/api/v1/jobsearch", tags=["Job Search"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "RecruitAI Core Engine đang chạy!"}