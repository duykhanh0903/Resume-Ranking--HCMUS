from langchain_core.tools import tool
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load mô hình SBERT đã fine-tune (chỉ load 1 lần khi app start)
try:
    sbert_model = SentenceTransformer("models/sbert_resume_ranking")
    print("✅ Đã load SBERT fine-tuned thành công.")
except Exception as e:
    print(f"⚠️ Không tìm thấy model fine-tune, dùng base model: {e}")
    sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

@tool
def verify_semantic_similarity(query: str, context_list: list) -> dict:
    """
    Sử dụng công cụ này khi không tìm thấy kỹ năng khớp chính xác. 
    So sánh một yêu cầu (query) với danh sách kỹ năng trong CV (context_list).
    Trả về dictionary chứa điểm tương đồng ('score') và kỹ năng khớp nhất ('best_match').
    """
    if not context_list:
        return {"score": 0.0, "best_match": ""}
    
    query_emb = sbert_model.encode([query])
    context_embs = sbert_model.encode(context_list)
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
    
    query_emb = sbert_model.encode([skill_name])
    context_embs = sbert_model.encode(sentences)
    similarities = cosine_similarity(query_emb, context_embs)[0]
    
    idx = np.argmax(similarities)
    best_score = similarities[idx]
    
    if best_score > 0.6: # Ngưỡng tin cậy
        return f"Found evidence in text: '...{sentences[idx]}...'"
    
    return "Not found"