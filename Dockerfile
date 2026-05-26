# 1. Sử dụng hệ điều hành Linux siêu nhẹ có cài sẵn Python 3.10
FROM python:3.11-slim

# 2. Tạo thư mục làm việc mặc định bên trong container
WORKDIR /app

# [QUAN TRỌNG] Cài đặt hệ sinh thái Tesseract OCR cho Linux để parser CV dạng ảnh/scan hoạt động
RUN apt-get update && apt-get install -y tesseract-ocr git && rm -rf /var/lib/apt/lists/*

# 3. Copy file requirements.txt vào trước để cài đặt thư viện
COPY requirements.txt .
# 4. Cài đặt các thư viện không lưu cache
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy toàn bộ mã nguồn còn lại vào container
COPY . .

# 6. Cấp quyền thực thi (execute) cho file start.sh
RUN chmod +x start.sh

# 7. Khởi chạy hệ thống thông qua start.sh để bật cả Backend lẫn Frontend
CMD ["./start.sh"]