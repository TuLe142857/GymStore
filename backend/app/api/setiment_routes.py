from flask import Blueprint, jsonify
from app.services.sentiment_service import analyze_product_sentiment
# Đặt prefix /sentiment cho API này
sentiment_bp = Blueprint("sentiment", __name__, url_prefix="/api/sentiment")

@sentiment_bp.route("/product/<int:product_id>", methods=["GET"])
def handle_get_sentiment_summary(product_id):
    """
    [PUBLIC] API để lấy tóm tắt phân tích cảm xúc
    cho một sản phẩm.
    """
    result, status = analyze_product_sentiment(product_id)
    return jsonify(result), status