import pandas as pd
import json
import asyncio
import os
from groq import AsyncGroq
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv

load_dotenv()

# ================= CẤU HÌNH ĐƯỜNG DẪN TƯƠNG ĐỐI =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INPUT_CSV_PATH = os.path.join(BASE_DIR, "data", "raw", "resume_jd_fit.csv")
CLEANED_JSON_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned_data.json")

# ================= CẤU HÌNH API =================
API_KEYS = [
    os.getenv("GROQ_API_KEY_1"),
    os.getenv("GROQ_API_KEY_2"),
    os.getenv("GROQ_API_KEY_3"),
    os.getenv("GROQ_API_KEY_4"),
    os.getenv("GROQ_API_KEY_5")
]
clients = [AsyncGroq(api_key=key) for key in API_KEYS]
MODEL_NAME = 'llama-3.1-8b-instant'

# ================= CÁC HÀM TIỆN ÍCH =================
def smart_truncate(text, head_words=500, tail_words=300):
    words = str(text).split()
    if len(words) <= (head_words + tail_words):
        return " ".join(words)
    return " ".join(words[:head_words]) + " ... " + " ".join(words[-tail_words:])

def flatten_dict_to_string(data_dict):
    if "error" in data_dict:
        return "N/A"
    parts = []
    for key, val in data_dict.items():
        if isinstance(val, list) and len(val) > 0:
            clean_key = key.replace('_', ' ').title()
            clean_val = ", ".join(val)
            parts.append(f"{clean_key}: {clean_val}")
    return " | ".join(parts) if parts else "No Keywords Extracted"

# ================= HÀM GỌI API & XỬ LÝ LÔ =================
async def extract_keywords_async(text, doc_type, client, max_retries=5):
    if doc_type == "resume":
        system_msg = "You are an expert IT Recruiter. You must output your response in valid JSON format."
        user_msg = f"""
        Extract key IT information from the following Candidate Resume.
        STRICT RULES:
        1. Extract ONLY maximum 15 HARD SKILLS (technical skills, tools, frameworks). Ignore soft skills.
        2. Extract maximum 3 most relevant Job Titles.
        3. Return EXACTLY in this JSON format: {{"skills": ["s1"], "job_titles": ["t1"]}}

        Resume text: {text}
        """
    else:
        system_msg = "You are an expert IT Recruiter. You must output your response in valid JSON format."
        user_msg = f"""
        Extract key IT requirements from the Job Description.
        STRICT RULES:
        1. Extract ONLY maximum 15 HARD SKILLS (technical skills, tools, frameworks). Ignore soft skills.
        2. Extract maximum 3 required Roles/Titles.
        3. Return EXACTLY in this JSON format: {{"required_skills": ["s1"], "required_roles": ["r1"]}}

        Job Description text: {text}
        """

    delay = 3
    for attempt in range(max_retries):
        try:
            chat_completion = await client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                model=MODEL_NAME,
                temperature=0,
                max_tokens=512,
                response_format={"type": "json_object"}
            )

            response_text = chat_completion.choices[0].message.content
            return json.loads(response_text)

        except Exception as e:
            error_msg = str(e).lower()

            if "400" in error_msg and "json_validate_failed" in error_msg:
                print(f"⚠️ Phát hiện văn bản rác/quá dài gây lỗi 400. Ra lệnh SKIP...")
                return {"error": "skip"}

            if "429" in error_msg or "rate limit" in error_msg:
                print(f"[-] Groq Rate Limit. Đang chờ {delay}s... (Lần {attempt + 1}/{max_retries})")
                await asyncio.sleep(delay) 
                delay *= 2
            elif "401" in error_msg or "api key" in error_msg:
                print(f"[!] LỖI API KEY: {error_msg}")
                raise RuntimeError("\n[!] LỖI NGHIÊM TRỌNG: Groq API Key không hợp lệ hoặc bị từ chối.")
            else:
                print(f"[-] Lỗi mạng/Server Groq: {error_msg}. Đang thử lại...")
                await asyncio.sleep(delay)
                delay *= 2

    return {"error": "skip"} 

async def process_single_row(row, client_resume, client_jd, sem):
    # Semaphore đảm bảo không bắn quá nhiều request cùng lúc làm sập API
    async with sem:
        orig_id = int(row['index'])
        label = str(row['label'])
        raw_resume = smart_truncate(row['resume_text'], head_words=500, tail_words=300)
        raw_jd = smart_truncate(row['job_description_text'], head_words=500, tail_words=300)

        resume_task = extract_keywords_async(raw_resume, "resume", client_resume)
        jd_task = extract_keywords_async(raw_jd, "jd", client_jd)

        resume_dict, jd_dict = await asyncio.gather(resume_task, jd_task)

        if "error" in resume_dict or "error" in jd_dict:
            print(f"⏩ Đã bỏ qua ID {orig_id} do lỗi văn bản.")
            return None

        cleaned_resume = flatten_dict_to_string(resume_dict)
        cleaned_jd = flatten_dict_to_string(jd_dict)

        return {
            "id": orig_id,
            "label": label,
            "resume_text": cleaned_resume,
            "job_description_text": cleaned_jd
        }

async def process_balanced_dataset_async(input_csv_path, output_json_path, total_samples=6000):
    print(f"Đang đọc dữ liệu từ: {input_csv_path}")
    df = pd.read_csv(input_csv_path)

    df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=False)

    results = []
    processed_ids = set()
    success_counts = {"Good Fit": 0, "Potential Fit": 0, "No Fit": 0}

    if os.path.exists(output_json_path):
        try:
            with open(output_json_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
            for r in results:
                success_counts[r['label']] += 1
                processed_ids.add(r['id'])
            print(f"📂 Đã tải Checkpoint! Hiện có: {success_counts}")
        except json.JSONDecodeError:
            print("⚠️ File JSON cũ bị lỗi, bắt đầu lại từ đầu.")

    def save_checkpoint(data):
        temp_path = output_json_path + ".tmp"
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        os.replace(temp_path, output_json_path)

    print("🚀 Bắt đầu quét dữ liệu bất đồng bộ...")
    sem = asyncio.Semaphore(3)
    tasks = []
    key_index = 0
    total_clients = len(clients)

    target_per_label = total_samples // 3
    dispatched_counts = success_counts.copy()
    print(f"🎯 Chỉ tiêu mỗi nhãn: {target_per_label} mẫu")
    estimated_batch_tokens = 0
    MAX_TOKENS_PER_MINUTE = 100000
    # ------------------------------------------

    for _, row in df_shuffled.iterrows():
        orig_id = int(row['index'])
        label = str(row['label'])

        if orig_id in processed_ids:
            continue

        if dispatched_counts.get(label, 0) >= target_per_label:
            continue

        resume_words = len(str(row['resume_text']).split())
        jd_words = len(str(row['job_description_text']).split())

        estimated_resume_tokens = min(resume_words, 800) * 1.3
        estimated_jd_tokens = min(jd_words, 800) * 1.3
        tokens_this_row = estimated_resume_tokens + estimated_jd_tokens

        if estimated_batch_tokens + tokens_this_row > MAX_TOKENS_PER_MINUTE:
            print(f"🛑 Đã nạp ~{int(estimated_batch_tokens)} tokens. Chủ động nghỉ 60s để nạp lại Rate Limit...")
            await asyncio.sleep(60)
            estimated_batch_tokens = 0

        estimated_batch_tokens += tokens_this_row

        dispatched_counts[label] = dispatched_counts.get(label, 0) + 1

        client_resume = clients[key_index % total_clients]
        client_jd = clients[(key_index + 1) % total_clients]
        key_index += 2

        task = asyncio.create_task(process_single_row(row, client_resume, client_jd, sem))
        tasks.append(task)
        await asyncio.sleep(0.5)

        if len(tasks) == 50:
            print(f"⏳ Đang xử lý lô 50 mẫu... (Đã lên lịch: {dispatched_counts})")
            batch_results = await asyncio.gather(*tasks)

            for res in batch_results:
                if res is not None:
                    results.append(res)
                    success_counts[res['label']] += 1
                    processed_ids.add(res['id'])

            save_checkpoint(results)
            print(f"💾 Thực tế thành công: {success_counts}")

            # --- ĐỒNG BỘ LẠI TRẠNG THÁI ---
            # Nếu có API nào bị lỗi (res is None), success_counts sẽ thấp hơn dispatched_counts.
            # Việc copy lại giúp "nhả" những slot bị lỗi ra để vòng lặp tiếp tục bốc mẫu bù vào.
            dispatched_counts = success_counts.copy()
            tasks = []

            if sum(success_counts.values()) >= total_samples:
                print("🎯 Đã đạt chỉ tiêu tổng số mẫu!")
                break

    if tasks and sum(success_counts.values()) < total_samples:
        print(f"⏳ Đang xử lý lô cuối cùng...")
        batch_results = await asyncio.gather(*tasks)
        for res in batch_results:
            if res is not None:
                results.append(res)
                success_counts[res['label']] += 1
                processed_ids.add(res['id'])
        save_checkpoint(results)

    print(f"🎉 HOÀN TẤT! Dữ liệu cuối cùng: {success_counts}")

# ================= TÁCH DỮ LIỆU (TRAIN / VAL / TEST) =================
def split_and_save_dataset(input_json_path, output_dir):
    print(f"\n--- Đang tách dữ liệu từ {input_json_path} ---")
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    train_df, temp_df = train_test_split(df, test_size=0.2, stratify=df['label'], random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, stratify=temp_df['label'], random_state=42)

    train_df.to_json(os.path.join(output_dir, "train_data.json"), orient='records', lines=True, force_ascii=False)
    val_df.to_json(os.path.join(output_dir, "val_data.json"), orient='records', lines=True, force_ascii=False)
    test_df.to_json(os.path.join(output_dir, "test_data.json"), orient='records', lines=True, force_ascii=False)

    print(f"Hoàn tất! Train: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")

# ================= MAIN =================
if __name__ == "__main__":
    os.makedirs(os.path.join(BASE_DIR, "data", "processed"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "data", "raw"), exist_ok=True)

    asyncio.run(process_balanced_dataset_async(INPUT_CSV_PATH, CLEANED_JSON_PATH, total_samples=5087))

    split_and_save_dataset(
        input_json_path=CLEANED_JSON_PATH,
        output_dir=os.path.join(BASE_DIR, "data", "processed")
    )