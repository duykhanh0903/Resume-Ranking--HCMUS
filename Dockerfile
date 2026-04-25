# 1. Sử dụng hệ điều hành Linux siêu nhẹ có cài sẵn Python 3.10
FROM python:3.10-slim

# 2. Tạo thư mục làm việc mặc định bên trong container
WORKDIR /app

# 3. Copy file requirements.txt vào trước để cài đặt thư viện
COPY requirements.txt .

# 4. Cài đặt các thư viện không lưu cache
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy toàn bộ mã nguồn còn lại vào container
COPY . .

# 6. Mở cổng 8501
EXPOSE 8501

# 7. Lệnh khởi chạy web khi container được bật
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
