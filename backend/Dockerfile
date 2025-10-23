# Dùng image Python 3.10 bản gọn nhẹ
FROM python:3.10-slim

# Đặt thư mục làm việc bên trong container
WORKDIR /app

# Cài đặt các thư viện hệ thống (nếu cần, ví dụ: để build mysqlclient)
# RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential

# Copy file requirements
COPY requirements.txt .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code backend còn lại vào
COPY . .

# Mở port mà Flask dev server sẽ chạy
EXPOSE 5000

# Lệnh mặc định để chạy server dev của Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]