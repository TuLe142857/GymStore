from flask import jsonify, request
from app.extensions import db
from app.models.product_models import Brand, Category, Ingredient
from . import admin_bp
from .decorators import admin_required


# ==============================================================================
# 1. QUẢN LÝ THƯƠNG HIỆU (BRAND)
# ==============================================================================

@admin_bp.route("/brand", methods=["POST"])
@admin_required
def create_brand():
    """Tạo thương hiệu mới"""
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "Name is required"}), 400

    if Brand.query.filter_by(name=name).first():
        return jsonify({"error": "Brand already exists"}), 400

    try:
        new_brand = Brand(name=name)
        db.session.add(new_brand)
        db.session.commit()
        return jsonify({"message": "Brand created", "id": new_brand.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/brand/<int:id>", methods=["PUT"])
@admin_required
def update_brand(id):
    """Sửa tên thương hiệu"""
    brand = Brand.query.get(id)
    if not brand:
        return jsonify({"error": "Brand not found"}), 404

    data = request.get_json()
    new_name = data.get("name")

    if new_name and new_name != brand.name:
        # Check trùng tên với brand khác
        if Brand.query.filter_by(name=new_name).first():
            return jsonify({"error": "Brand name already exists"}), 400
        brand.name = new_name

    db.session.commit()
    return jsonify({"message": "Brand updated"}), 200


# ==============================================================================
# 2. QUẢN LÝ DANH MỤC (CATEGORY)
# ==============================================================================

@admin_bp.route("/category", methods=["POST"])
@admin_required
def create_category():
    """Tạo danh mục mới"""
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "Name is required"}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({"error": "Category already exists"}), 400

    try:
        new_cat = Category(name=name)
        db.session.add(new_cat)
        db.session.commit()
        return jsonify({"message": "Category created", "id": new_cat.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/category/<int:id>", methods=["PUT"])
@admin_required
def update_category(id):
    """Sửa danh mục"""
    cat = Category.query.get(id)
    if not cat:
        return jsonify({"error": "Category not found"}), 404

    data = request.get_json()
    new_name = data.get("name")

    if new_name and new_name != cat.name:
        if Category.query.filter_by(name=new_name).first():
            return jsonify({"error": "Category name already exists"}), 400
        cat.name = new_name

    db.session.commit()
    return jsonify({"message": "Category updated"}), 200


# ==============================================================================
# 3. QUẢN LÝ ĐỊNH NGHĨA NGUYÊN LIỆU (INGREDIENT DEF)
# ==============================================================================

@admin_bp.route("/ingredient", methods=["POST"])
@admin_required
def create_ingredient_def():
    """Tạo mới định nghĩa nguyên liệu (Ví dụ: Vitamin C, Whey Protein...)"""
    data = request.get_json()
    name = data.get("name")
    unit = data.get("measurement_unit")  # Lấy unit, không set default ở đây nữa

    # 1. Validate Name
    if not name:
        return jsonify({"error": "Name is required"}), 400

    # 2. Validate Unit (Bắt buộc nhập, tránh việc hệ thống tự gán 'g' sai lệch)
    if not unit:
        return jsonify({"error": "Measurement unit is required (e.g., 'g', 'mg', 'ml')"}), 400

    if Ingredient.query.filter_by(name=name).first():
        return jsonify({"error": "Ingredient already exists"}), 400

    try:
        new_ing = Ingredient(
            name=name,
            desc=data.get("desc", ""),
            measurement_unit=unit  # Dùng giá trị người dùng gửi
        )
        db.session.add(new_ing)
        db.session.commit()
        return jsonify({"message": "Ingredient created", "id": new_ing.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/ingredient/<int:id>", methods=["PUT"])
@admin_required
def update_ingredient_def(id):
    """Sửa thông tin nguyên liệu"""
    ing = Ingredient.query.get(id)
    if not ing:
        return jsonify({"error": "Ingredient not found"}), 404

    data = request.get_json()

    # 1. Update Name (có check trùng)
    if "name" in data:
        new_name = data["name"]
        if new_name != ing.name:
            if Ingredient.query.filter_by(name=new_name).first():
                return jsonify({"error": "Ingredient name already exists"}), 400
            ing.name = new_name

    # 2. Update các field khác
    if "desc" in data:
        ing.desc = data["desc"]

    if "measurement_unit" in data:
        ing.measurement_unit = data["measurement_unit"]

    db.session.commit()
    return jsonify({"message": "Ingredient updated"}), 200