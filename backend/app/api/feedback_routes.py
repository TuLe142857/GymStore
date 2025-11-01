from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.feedback_service import (
    get_feedback_for_product, 
    add_product_feedback,
    has_user_reviewed_product
)

feedback_bp = Blueprint("feedback", __name__, url_prefix="/feedback")

@feedback_bp.route("/product/<int:product_id>", methods=["GET"])
def handle_get_feedback(product_id):
    """
    API Public: Lấy tất cả feedback cho 1 sản phẩm.
    """
    feedbacks, status = get_feedback_for_product(product_id)
    return jsonify(feedbacks), status

@feedback_bp.route("/product/<int:product_id>", methods=["POST"])
@jwt_required()
def handle_add_feedback(product_id):
    """
    API Private: User gửi feedback mới cho 1 sản phẩm.
    """
    try:
        current_user_id = int(get_jwt_identity())
    except ValueError:
        return jsonify({"error": "Invalid user identity"}), 401
        
    data = request.get_json()
    rating = data.get("rating")
    comment = data.get("comment", "") # Comment có thể không bắt buộc

    if not rating or not isinstance(rating, int) or not (1 <= rating <= 5):
        return jsonify({"error": "A valid rating (1-5) is required"}), 400

    result, status = add_product_feedback(
        user_id=current_user_id,
        product_id=product_id,
        rating=rating,
        comment=comment
    )
    
    return jsonify(result), status

@feedback_bp.route("/check/<int:product_id>", methods=["GET"])
@jwt_required()
def check_feedback(product_id):
    """
    [GET] Kiểm tra xem user đã review sản phẩm này chưa.
    """
    try:
        user_id = int(get_jwt_identity())
    except ValueError:
        return jsonify({"error": "Invalid user identity"}), 401
        
    has_reviewed = has_user_reviewed_product(user_id, product_id)
    return jsonify({"has_reviewed": has_reviewed}), 200