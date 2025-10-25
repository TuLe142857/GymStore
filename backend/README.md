# [UPDATE] chỉnh cấu trúc db (một chút) + sinh dữ liệu mẫu
> Note: dữ liệu mẫu chỉ gồm thông tin liên quan user và product, chưa bao gồm tương tác và mua hàng
- user, user_infor, role
- product, category, brand, ingredient, product_ingredient

> Note: Ảnh sản phẩm lưu trên server
- Thư mục trên máy host: backend/uploads/product_images
- Thu mục trên container: /app/uploads/product_images
- (docker compose  mount backend/uploads: /app/)
- mục backend/uploads có trong gitignore nên sẽ không được push lên 


# [FIX] pull code về có lỗi xảy ra thì thử xóa và build lại docker để database tự cập nhật

```commandline
docker compose down --volumes --remove-orphans 

docker compose build 

docker compose up -d

```