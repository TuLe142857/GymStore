# recommendation_routes.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.recommendation_service import (
    get_similar_products,
    get_collaborative_recommendations,
    get_top_products
)
# Import model Product mới
from app.models.product_models import Product

# Đổi tên blueprint nếu muốn, ví dụ: reco_bp
recommendation_bp = Blueprint("recommendation", __name__, url_prefix="/recommend")

# --- CẬP NHẬT HÀM SERIALIZE ---
def serialize_product(p):
    """Helper để chuyển Product object sang JSON"""
    # Lấy rating thực tế từ model mới
    rating_value = float(p.avg_rating) if p.avg_rating is not None else 0.0

    return {
        "id": str(p.id),
        "name": p.name,
        "price": p.price, # Giữ nguyên là Integer theo model mới
        "image": p.image_url,
        "category": p.category.name if p.category else "Uncategorized",
        "rating": rating_value # Dùng avg_rating
    }

# --- CÁC ROUTE KHÁC GIỮ NGUYÊN LOGIC ---
@recommendation_bp.route("/similar-products/<int:product_id>", methods=["GET"])
def get_recommendations(product_id):
    """ Lấy sản phẩm tương tự (Content-Based). """
    product_ids, status = get_similar_products(product_id, top_n=4)

    if status == 503:
         return jsonify({"error": "Recommendation model is currently unavailable. Please try again later."}), status
    if status != 200:
        return jsonify({"error": "Could not retrieve recommendations"}), status
    if not product_ids:
         return jsonify([]), 200 # Trả về rỗng nếu không tìm thấy

    try:
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        products_dict = {p.id: p for p in products}
        # Đảm bảo giữ đúng thứ tự gợi ý từ service
        sorted_products = [products_dict[pid] for pid in product_ids if pid in products_dict]
        return jsonify([serialize_product(p) for p in sorted_products]), 200
    except Exception as e:
        print(f"Error querying/serializing products: {e}")
        return jsonify({"error": "Failed to retrieve product details"}), 500

@recommendation_bp.route("/for-you", methods=["GET"])
@jwt_required()
def get_cf_recommendations():
    """ API Hybrid: Lấy CF recos, fallback sang Top Products. """
    try:
        current_user_id = int(get_jwt_identity())
    except ValueError:
        return jsonify({"error": "Invalid user identity"}), 401

    product_ids, status = get_collaborative_recommendations(current_user_id, top_n=6)

    if status == 503:
         return jsonify({"error": "Recommendation model is currently unavailable. Please try again later."}), status
    if status != 200:
        return jsonify({"error": "Could not retrieve collaborative recommendations"}), status

    # Logic Fallback nếu CF trả về rỗng (user mới hoặc đã xem hết)
    if not product_ids:
        print(f"CF returned empty for user {current_user_id}. Falling back to top products.")
        product_ids, status = get_top_products(top_n=6)
        if status != 200:
            return jsonify({"error": "Could not retrieve fallback recommendations"}), status
        if not product_ids:
             return jsonify([]), 200 # Trả về rỗng nếu cả fallback cũng rỗng

    try:
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        products_dict = {p.id: p for p in products}
        sorted_products = [products_dict[pid] for pid in product_ids if pid in products_dict]
        return jsonify([serialize_product(p) for p in sorted_products]), 200
    except Exception as e:
        print(f"Error querying/serializing products in /for-you: {e}")
        return jsonify({"error": "Failed to retrieve product details"}), 500

@recommendation_bp.route("/top-products", methods=["GET"])
def get_public_recommendations():
    """ API public: Lấy top sản phẩm bán chạy. """
    product_ids, status = get_top_products(top_n=6)

    if status != 200:
        return jsonify({"error": "Could not retrieve top products"}), status
    if not product_ids:
         return jsonify([]), 200 # Trả về rỗng nếu không có top products

    try:
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        products_dict = {p.id: p for p in products}
        sorted_products = [products_dict[pid] for pid in product_ids if pid in products_dict]
        return jsonify([serialize_product(p) for p in sorted_products]), 200
    except Exception as e:
        print(f"Error querying/serializing products in /top-products: {e}")
        return jsonify({"error": "Failed to retrieve product details"}), 500