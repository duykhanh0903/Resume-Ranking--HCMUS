from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import analyzer
from src.api.routers import jobsearch
from src.api.routers import builder
from src.api.routers import standard_analyzer 
from src.api.routers import ranking

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

app.include_router(ranking.router, prefix="/api/v1/ranking", tags=["Ranking"])
app.include_router(analyzer.router, prefix="/api/v1/analyzer", tags=["Resume Analysis"])
app.include_router(jobsearch.router, prefix="/api/v1/jobsearch", tags=["Job Search"])
app.include_router(builder.router, prefix="/api/v1/builder", tags=["Resume Builder"])
app.include_router(standard_analyzer.router,  prefix="/api/v1/standard-analyzer", tags=["Standard Analysis"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "RecruitAI Core Engine đang chạy!"}