from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import analyzer

app = FastAPI(
    title="RecruitAI Backend API",
    description="Core Engine cho hệ thống phân tích và xếp hạng CV",
    version="1.0.0"
)

# Cấu hình CORS để Frontend (Streamlit) có thể gọi API mà không bị block
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Trong thực tế doanh nghiệp sẽ set domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Nhúng các router vào app chính
app.include_router(analyzer.router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "RecruitAI Core Engine đang chạy!"}