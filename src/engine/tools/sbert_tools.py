import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

load_dotenv()

HF_API_URL = os.getenv("HF_API_URL")
HF_TOKEN = os.getenv("HF_TOKEN")

def get_embeddings(texts: list) -> list:
    if not texts: return []
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        response = requests.post(HF_API_URL, headers=headers, json={"inputs": texts, "options": {"wait_for_model": True}})
        if response.status_code == 200:
            return response.json()
        print(f"⚠️ Lỗi API Hugging Face: {response.text}")
        return np.zeros((len(texts), 384)).tolist()
    except Exception as e:
        print(f"⚠️ Lỗi mạng HF: {e}")
        return np.zeros((len(texts), 384)).tolist()

def calculate_overall_match(jd_skills: list, resume_skills: list) -> float:
    """
    Tính điểm khớp tổng thể dựa trên Cosine Similarity của SBERT.
    Đảm bảo điểm số được tính toán bằng toán học thay vì LLM tự sinh.
    """
    if not jd_skills or not resume_skills:
        return 0.0
        
    total_score = 0.0
    
    # Mã hóa toàn bộ skill của ứng viên 1 lần duy nhất để tiết kiệm chi phí tính toán
    resume_embs = get_embeddings(resume_skills)
    
    for req_skill in jd_skills:
        req_emb = get_embeddings([req_skill])
        similarities = cosine_similarity(req_emb, resume_embs)[0]
        best_match_score = float(np.max(similarities))
        
        # Đặt ngưỡng (threshold), ví dụ > 0.6 mới tính là có điểm (cùng nhóm ngữ nghĩa)
        if best_match_score > 0.6:
            total_score += best_match_score
            
    # Tính trung bình điểm trên thang 100
    avg_score = (total_score / len(jd_skills)) * 100
    
    # Đảm bảo điểm số không vượt quá 100 và làm tròn 1 chữ số thập phân
    return round(min(avg_score, 100.0), 1)

def calibrate_sbert_score(raw_similarity: float) -> float:
    """
    Hiệu chuẩn điểm Cosine Similarity gốc của SBERT để phù hợp với hiển thị UI.
    Dựa trên thống kê tập test (Fit: ~0.73, Potential: ~0.66, No Fit: ~0.58).
    """
    
    # 1. Bảo vệ biên
    if raw_similarity <= 0.0:
        return 0.0
    if raw_similarity >= 1.0:
        return 100.0

    # 2. Các điểm neo (Anchors): (X_raw, Y_target)
    # X_raw: Điểm SBERT gốc. Y_target: Điểm hiển thị trên UI (0-100)
    anchors = [
        (0.00, 0.0),   
        (0.50, 20.0),  # Dưới 0.50 là rất tệ, đè điểm xuống < 20
        (0.65, 49.0),  # Mốc giao điểm No Fit / Potential Fit chạm mốc 49đ (Đỏ)
        (0.71, 74.0),  # Mốc giao điểm Potential / Good Fit chạm mốc 74đ (Vàng)
        (0.76, 85.0),  # Mức 75% của Good Fit đạt điểm cao (85đ)
        (0.85, 95.0),  # Mức cực tốt
        (1.00, 100.0)
    ]

    # 3. Nội suy tuyến tính
    for i in range(len(anchors) - 1):
        x0, y0 = anchors[i]
        x1, y1 = anchors[i + 1]
        
        if x0 <= raw_similarity <= x1:
            # Nếu mẫu bằng chính điểm neo, tránh chia cho 0
            if x0 == x1: 
                return round(y0, 1)
                
            # Tính toán tỷ lệ
            ratio = (raw_similarity - x0) / (x1 - x0)
            calibrated = y0 + (ratio * (y1 - y0))
            return round(calibrated, 1)

    return 100.0

@tool
def verify_semantic_similarity(query: str, context_list: list) -> dict:
    """
    Sử dụng công cụ này khi không tìm thấy kỹ năng khớp chính xác. 
    So sánh một yêu cầu (query) với danh sách kỹ năng trong CV (context_list).
    Trả về dictionary chứa điểm tương đồng ('score') và kỹ năng khớp nhất ('best_match').
    """
    if not context_list:
        return {"score": 0.0, "best_match": ""}
    
    query_emb = get_embeddings([query])
    context_embs = get_embeddings(context_list)
    similarities = cosine_similarity(query_emb, context_embs)[0]
    
    idx = np.argmax(similarities)
    return {
        "score": float(similarities[idx]),
        "best_match": str(context_list[idx])
    }

@tool
def deep_scan_raw_text(skill_name: str, raw_text: str) -> str:
    """
    Sử dụng công cụ này khi kỹ năng không có trong JSON của ứng viên. 
    Quét trực tiếp trong văn bản thô (raw_text) để tìm dấu vết của kỹ năng.
    """
    if not raw_text:
        return "Not found"
        
    # Tách văn bản thành các câu dài có ý nghĩa
    sentences = [s.strip() for s in raw_text.split('.') if len(s.strip()) > 15]
    if not sentences: 
        return "Not found"
    
    query_emb = get_embeddings([skill_name])
    context_embs = get_embeddings(sentences)
    similarities = cosine_similarity(query_emb, context_embs)[0]
    
    idx = np.argmax(similarities)
    best_score = similarities[idx]
    
    if best_score > 0.6: # Ngưỡng tin cậy
        return f"Found evidence in text: '...{sentences[idx]}...'"
    
    return "Not found"