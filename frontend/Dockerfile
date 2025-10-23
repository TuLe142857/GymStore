# Dùng image node làm cơ sở
FROM node:22-alpine


# Đặt thư mục làm việc bên trong container
WORKDIR /app

# Copy file package.json và lock file
# Tận dụng cache của Docker nếu các file này không đổi
COPY package.json package-lock.json ./

# Cài đặt tất cả thư viện
RUN npm install

# Copy toàn bộ code frontend còn lại vào
COPY . .

# Mở port của server dev (React)
EXPOSE 3000

# Lệnh mặc định để chạy server dev (sẽ được docker-compose gọi)
CMD ["npm", "start"]