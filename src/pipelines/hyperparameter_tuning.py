import os
import json
import optuna
from sentence_transformers import SentenceTransformer, InputExample
from sentence_transformers.sentence_transformer import losses, evaluation
from torch.utils.data import DataLoader
from src.utils.load_data import load_data_for_sbert

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

# ================= CHUẨN BỊ DỮ LIỆU & EVALUATOR =================
train_samples, _ = load_data_for_sbert("train_data.json")
_, val_raw = load_data_for_sbert("val_data.json")

val_sentences1 = [item['jd'] for item in val_raw]
val_sentences2 = [item['cv'] for item in val_raw]
val_labels = [item['score'] for item in val_raw]

evaluator = evaluation.EmbeddingSimilarityEvaluator(val_sentences1, val_sentences2, val_labels, name='resume-val')

# ================= LUỒNG TỐI ƯU HÓA =================
def objective(trial):
    print(f"\n--- ĐANG CHẠY THỬ NGHIỆM THỨ {trial.number + 1} ---")
    learning_rate = trial.suggest_float("learning_rate", 1e-5, 5e-5, log=True)
    batch_size = trial.suggest_categorical("batch_size", [16, 32])
    epochs = trial.suggest_int("epochs", 3, 5)

    model = SentenceTransformer('all-MiniLM-L6-v2')
    model.max_seq_length = 512
    train_dataloader = DataLoader(train_samples, shuffle=True, batch_size=batch_size)
    train_loss = losses.CoSENTLoss(model=model)

    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        evaluator=evaluator,
        epochs=epochs,
        evaluation_steps=0, 
        warmup_steps=100,
        optimizer_params={'lr': learning_rate},
        output_path=None 
    )

    score = evaluator(model)
    final_score = score.get('resume-val_spearman_cosine', 0.0) if isinstance(score, dict) else score
    
    print(f"-> Thử nghiệm {trial.number + 1} hoàn tất | Điểm Spearman: {final_score:.4f}")
    return final_score

if __name__ == "__main__":
    print("\n🚀 Bắt đầu quá trình Tinh chỉnh Siêu tham số (Optuna)...")
    study = optuna.create_study(direction="maximize", study_name="SBERT_Tuning")
    study.optimize(objective, n_trials=8)

    print("\n🎉 BỘ THAM SỐ XỊN NHẤT ĐƯỢC TÌM THẤY LÀ:")
    best_trial = study.best_trial
    print(f" - Điểm cao nhất: {best_trial.value:.4f}")
    for key, value in best_trial.params.items():
        print(f"    * {key}: {value}")