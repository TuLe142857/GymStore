# GymStore
Đồ án môn học Phát triển các hệ thống thông minh PTIT HCM

# Note
Frontend: http://localhost:3000

Backend (Flask): http://localhost:5000

MySQL: 3306

Redis: 6379

# Hướng dẫn tải repo + run:

## Clone repo
```
# clone repo
git clone https://github.com/TuLe142857/GymStore.
cd GymStore
```

## Cấu hình biến môi trường sau khi clone
Copy file .env.example thành .env và điền các nội dung cần thiết, ví dụ:

```
# MySQL Config
MYSQL_DATABASE=gym_store
MYSQL_USER=db_user
MYSQL_PASSWORD=123456
MYSQL_ROOT_PASSWORD=123456

# Redis
REDIS_HOST=redis

# Backend Flask
FLASK_APP=run.py
FLASK_DEBUG=1
SECRET_KEY=your_flask_secret_key_sieu_bi_mat
```

## Build docker lần đầu
```
# buid docker
docker compose  build

```

## Chạy các service
```
docker compose  up -d
```

# Thay đổi code trong quá trình phát triển
Dev server React & Flask sẽ tự reload nhờ mount volume.

Nếu cài thêm package mới:

Frontend: 

``
docker exec -it frontend_service npm install <package>
``

Backend: 

```
docker exec -it backend_service pip install <package>
```

Nếu thay đổi Dockerfile → chạy lại docker compose build.