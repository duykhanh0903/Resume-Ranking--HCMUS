#!/bin/bash

export MALLOC_ARENA_MAX=2

# ÉP CÁC THƯ VIỆN AI CHỈ CHẠY 1 LUỒNG ĐỂ TIẾT KIỆM HÀNG TRĂM MB RAM
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

if [ "$SERVICE_TYPE" == "backend" ]; then
    echo "⚙️ KHỞI ĐỘNG HỆ THỐNG: BACKEND FASTAPI"
    echo "🚀 Đang kích hoạt Backend FastAPI ở cổng $PORT..."
    uvicorn src.api.main:app --host 0.0.0.0 --port $PORT

elif [ "$SERVICE_TYPE" == "frontend" ]; then
    echo "⚙️ KHỞI ĐỘNG HỆ THỐNG: FRONTEND STREAMLIT"
    echo "🎨 Đang kích hoạt Frontend Streamlit ở cổng $PORT..."
    
    # Frontend chạy trực tiếp độc lập, không tải mô hình, tắt tính năng quét file đổi mã nguồn để tiết kiệm RAM
    streamlit run src/ui/app.py \
        --server.port $PORT \
        --server.address 0.0.0.0 \
        --server.enableCORS false \
        --server.enableWebsocketCompression false \
        --server.fileWatcherType none

else
    echo "❌ LỖI: Không xác định được biến SERVICE_TYPE (Phải là 'backend' hoặc 'frontend')."
    exit 1
fi