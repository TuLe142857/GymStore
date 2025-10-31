from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.interaction_service import log_interaction

interaction_bp = Blueprint("interaction", __name__, url_prefix="/interaction")

@interaction_bp.route("/log", methods=["POST"])
@jwt_required()
def log_user_interaction():
    """
    Endpoint để frontend gửi dữ liệu tương tác lên.
    """
    data = request.get_json()
    product_id = data.get("product_id")
    interaction_type = data.get("type") # 'view', 'add_to_cart', 'purchase'
    
    if not product_id or not interaction_type:
        return jsonify({"error": "product_id and type are required"}), 400
        
    current_user_id = get_jwt_identity()
    
    result, status = log_interaction(
        user_id=int(current_user_id), 
        product_id=int(product_id), 
        interaction_type_str=interaction_type
    )
    
    return jsonify(result), status 