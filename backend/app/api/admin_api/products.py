from flask import jsonify, request
from app.models import *
from . import admin_bp
from .decorators import admin_required


# ==========================================
# 1. QUẢN LÝ SẢN PHẨM (PRODUCT)
# ==========================================

@admin_bp.route("/products", methods=["POST"])
@admin_required
def create_product():
    """
    [ADMIN] Tạo sản phẩm mới.
    Quy trình:
    1. FE upload ảnh -> lấy URL.
    2. FE gọi API này kèm image_url và các ID (category_id, brand_id).
    """
    data = request.get_json()

    # Validate cơ bản
    required_fields = ["name", "price", "category_id", "brand_id"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        # 1. Tạo Product Base
        # Lưu ý: Nhận thẳng URL ảnh từ FE gửi lên
        new_product = Product(
            name=data.get("name"),
            desc=data.get("desc", ""),
            image_url=data.get("image_url", ""),  # URL ảnh đã upload
            price=float(data.get("price")),

            # Thông tin đóng gói
            package_quantity=float(data.get("package_quantity", 0)),
            package_unit=data.get("package_unit", ""),
            serving_quantity=float(data.get("serving_quantity", 0)),
            serving_unit=data.get("serving_unit", ""),

            stock_quantity=int(data.get("stock_quantity", 0)),

            # Foreign Keys (Nhận ID từ FE)
            category_id=int(data.get("category_id")),
            brand_id=int(data.get("brand_id")),

            is_active=True
        )
        db.session.add(new_product)
        db.session.flush()  # Có ID ngay để dùng cho bảng phụ

        # 2. Thêm Ingredients (Danh sách ID và số lượng)
        # Sample ingredients: [{"id": 1, "quantity": 10}, {"id": 5, "quantity": 2}]
        ingredients_data = data.get("ingredients", [])
        for item in ingredients_data:
            ing_id = item.get("id") or item.get("ingredient_id")
            qty = item.get("quantity")

            if ing_id and qty:
                association = ProductIngredient(
                    product_id=new_product.id,
                    ingredient_id=int(ing_id),
                    quantity=float(qty)
                )
                db.session.add(association)

        db.session.commit()
        return jsonify({
            "message": "Product created successfully",
            "product_id": new_product.id
        }), 201

    except Exception as e:
        db.session.rollback()
        # Log lỗi ra console để debug
        print(f"Error creating product: {str(e)}")
        return jsonify({"error": "Failed to create product. Check data integrity."}), 500


@admin_bp.route("/products/<int:product_id>", methods=["PUT"])
@admin_required
def update_product(product_id):
    """
    [ADMIN] Cập nhật sản phẩm.
    - Cho phép đổi ảnh (FE gửi image_url mới).
    - Cập nhật Ingredients (Cơ chế: Xóa cũ -> Thêm mới).
    """
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json()
    try:
        # 1. Update thông tin cơ bản (Nếu có gửi lên mới update)
        if "name" in data: product.name = data["name"]
        if "desc" in data: product.desc = data["desc"]

        # Logic đổi ảnh: Frontend gửi URL mới vào field này
        if "image_url" in data: product.image_url = data["image_url"]

        if "price" in data: product.price = float(data["price"])
        if "stock_quantity" in data: product.stock_quantity = int(data["stock_quantity"])
        if "is_active" in data: product.is_active = bool(data["is_active"])

        # Update ID
        if "category_id" in data: product.category_id = int(data["category_id"])
        if "brand_id" in data: product.brand_id = int(data["brand_id"])

        # Update thông số
        if "package_quantity" in data: product.package_quantity = data["package_quantity"]
        if "package_unit" in data: product.package_unit = data["package_unit"]
        if "serving_quantity" in data: product.serving_quantity = data["serving_quantity"]
        if "serving_unit" in data: product.serving_unit = data["serving_unit"]

        # 2. Update Ingredients (Reset)
        if "ingredients" in data:
            # Xóa sạch liên kết cũ
            ProductIngredient.query.filter_by(product_id=product_id).delete()

            # Thêm danh sách mới
            for item in data["ingredients"]:
                ing_id = item.get("id") or item.get("ingredient_id")
                qty = item.get("quantity")
                if ing_id and qty:
                    association = ProductIngredient(
                        product_id=product_id,
                        ingredient_id=int(ing_id),
                        quantity=float(qty)
                    )
                    db.session.add(association)

        db.session.commit()
        return jsonify({"message": "Product updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error updating product: {str(e)}")
        return jsonify({"error": str(e)}), 500