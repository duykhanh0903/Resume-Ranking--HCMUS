import os
import json
from sentence_transformers import SentenceTransformer, InputExample
from sentence_transformers.sentence_transformer import losses, evaluation
from torch.utils.data import DataLoader
from src.utils.load_data import load_data_for_sbert

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
MODEL_SAVE_PATH = os.path.join(BASE_DIR, "models", "sbert_resume_ranking")

if __name__ == "__main__":
    print("Đang nạp dữ liệu...")
    train_samples, _ = load_data_for_sbert("train_data.json")
    _, val_raw = load_data_for_sbert("val_data.json")

    val_sentences1 = [item['jd'] for item in val_raw]
    val_sentences2 = [item['cv'] for item in val_raw]
    val_labels = [item['score'] for item in val_raw]
    
    evaluator = evaluation.EmbeddingSimilarityEvaluator(val_sentences1, val_sentences2, val_labels, name='resume-val')

    model = SentenceTransformer('all-MiniLM-L6-v2')
    model.max_seq_length = 512
    
    # SỬ DỤNG BỘ THAM SỐ TỐT NHẤT TỪ OPTUNA
    BEST_BATCH_SIZE = 32
    BEST_LR = 3.472885132845913e-05
    BEST_EPOCHS = 5
    
    train_dataloader = DataLoader(train_samples, shuffle=True, batch_size=BEST_BATCH_SIZE)
    train_loss = losses.CoSENTLoss(model=model)

    print(f"Đang bắt đầu Fine-tuning với LR={BEST_LR}, Batch={BEST_BATCH_SIZE}...")
    
    os.makedirs(os.path.join(BASE_DIR, "models"), exist_ok=True)
    
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        evaluator=evaluator,
        epochs=BEST_EPOCHS,
        evaluation_steps=50,
        warmup_steps=100,
        optimizer_params={'lr': BEST_LR},
        output_path=MODEL_SAVE_PATH 
    )

    print(f"Hoàn tất! Model đã được lưu tại: {MODEL_SAVE_PATH}")