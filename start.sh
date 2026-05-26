#!/bin/bash

git init

echo "📥 Đang tải SBERT model từ DagsHub thông qua DVC..."
# Cấu hình xác thực DVC với DagsHub bằng biến môi trường
dvc remote modify origin --local auth basic
dvc remote modify origin --local user $DAGSHUB_REPO_OWNER
dvc remote modify origin --local password $DAGSHUB_USER_TOKEN
dvc remote modify storage --local access_key_id $AWS_ACCESS_KEY_ID
dvc remote modify storage --local secret_access_key $AWS_SECRET_ACCESS_KEY

# Kéo model về (chỉ kéo những file có trong .dvc)
dvc pull

echo "🚀 Đang khởi động Backend FastAPI ở cổng 8000..."
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 &

echo "⏳ Chờ 3 giây cho Backend ổn định..."
sleep 30

echo "🎨 Đang khởi động Frontend Streamlit..."
streamlit run src/ui/app.py --server.port ${PORT:-8501} --server.address 0.0.0.0