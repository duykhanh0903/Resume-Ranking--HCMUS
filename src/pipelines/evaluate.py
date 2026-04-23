import os
from sentence_transformers import SentenceTransformer
from sentence_transformers.sentence_transformer import evaluation
from sklearn.metrics.pairwise import cosine_similarity
from src.utils.load_data import load_data_for_sbert

# ================= CẤU HÌNH ĐƯỜNG DẪN =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MODEL_SAVE_PATH = os.path.join(BASE_DIR, "models", "sbert_resume_ranking") 
BASE_MODEL_NAME = 'all-MiniLM-L6-v2'

if __name__ == "__main__":
    print("Đang nạp tập dữ liệu Test...")
    _, test_raw = load_data_for_sbert("test_data.json")

    label_map = {"No Fit": 0.0, "Potential Fit": 0.5, "Good Fit": 1.0}
    reverse_label_map = {v: k for k, v in label_map.items()}

    # ================= LOAD MÔ HÌNH =================
    print(f"Đang load mô hình đã Fine-tune từ: {MODEL_SAVE_PATH}...")
    model_tuned = SentenceTransformer(MODEL_SAVE_PATH)

    print(f"Đang load mô hình Zero-shot (Pre-trained gốc): {BASE_MODEL_NAME}...")
    model_base = SentenceTransformer(BASE_MODEL_NAME)

    # ================= SO SÁNH TRỰC QUAN (10 MẪU) =================
    print("\n--- SO SÁNH NHÃN THỰC TẾ VÀ DỰ ĐOÁN (10 MẪU TEST ĐẦU TIÊN) ---")
    for i, item in enumerate(test_raw[:10]):
        jd = item['jd']
        resume = item['cv']
        true_score = item['score']
        true_label_text = reverse_label_map.get(true_score, "Unknown")

        # Mã hóa vector cho cả 2 mô hình
        emb1_base = model_base.encode([jd])
        emb2_base = model_base.encode([resume])

        emb1_tuned = model_tuned.encode([jd])
        emb2_tuned = model_tuned.encode([resume])

        # Tính Cosine Similarity
        score_base = cosine_similarity(emb1_base, emb2_base)[0][0]
        score_tuned = cosine_similarity(emb1_tuned, emb2_tuned)[0][0]

        print(f"Mẫu {i+1}:")
        print(f"  - Nhãn gốc (True)  : {true_label_text} ({true_score:.1f})")
        print(f"  - Điểm Zero-shot   : {score_base:.4f}")
        print(f"  - Điểm Fine-tuned  : {score_tuned:.4f}")

        # Tính chênh lệch
        diff = score_tuned - score_base
        trend = "Tăng" if diff > 0 else "Giảm"
        print(f"  => Biến động       : {trend} {abs(diff):.4f}")
        print("-" * 50)

    # ================= ĐÁNH GIÁ TỔNG THỂ =================
    print("\nĐang tính toán các chỉ số đánh giá trên toàn bộ tập Test...")
    test_sentences1 = [item['jd'] for item in test_raw]
    test_sentences2 = [item['cv'] for item in test_raw]
    test_labels = [item['score'] for item in test_raw]

    evaluator = evaluation.EmbeddingSimilarityEvaluator(
        test_sentences1, test_sentences2, test_labels, name="resume-test"
    )

    results_base = evaluator(model_base)
    results_tuned = evaluator(model_tuned)

    print(f"\n================ ĐIỂM CHUYÊN MÔN TỔNG THỂ ({len(test_raw)} MẪU) ================")

    print("\n[A] MÔ HÌNH ZERO-SHOT (GỐC):")
    for metric, score in results_base.items():
        if isinstance(score, float):
            print(f"   - {metric}: {score:.4f}")

    print("\n[B] MÔ HÌNH ĐÃ FINE-TUNE:")
    for metric, score in results_tuned.items():
        if isinstance(score, float):
            print(f"   - {metric}: {score:.4f}")

    spearman_base = results_base.get('resume-test_spearman_cosine', results_base.get('spearman_cosine', 0))
    spearman_tuned = results_tuned.get('resume-test_spearman_cosine', results_tuned.get('spearman_cosine', 0))
    
    uplift = ((spearman_tuned - spearman_base) / spearman_base) * 100 if spearman_base != 0 else 0

    print("\n[KẾT LUẬN]")
    print(f"=> Chỉ số xếp hạng (Spearman Cosine) đã thay đổi: {uplift:+.2f}%")