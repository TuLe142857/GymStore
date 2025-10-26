from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.order_service import (
    create_order_from_cart_service,
    get_user_orders_service,
    get_order_details_service
)
from app.utils.serializers import serialize_order, serialize_order_list

order_bp = Blueprint('order', __name__, url_prefix='/order')

@order_bp.route('/create', methods=['POST'])
@jwt_required()
def create_order():
    """
    Tạo đơn hàng mới từ giỏ hàng của user.
    Cần 'shipping_address' trong body.
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    shipping_address = data.get('shipping_address')
    
    if not shipping_address:
        return jsonify({"error": "Shipping address is required"}), 400
        
    result, status_code = create_order_from_cart_service(user_id, shipping_address)
    
    if status_code == 201:
        return jsonify(serialize_order(result.get('order'))), 201
        
    return jsonify(result), status_code

@order_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    """ Lấy lịch sử đơn hàng của user. """
    user_id = int(get_jwt_identity())
    orders = get_user_orders_service(user_id)
    return jsonify([serialize_order_list(o) for o in orders]), 200

@order_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_details(order_id):
    """ Lấy chi tiết 1 đơn hàng. """
    user_id = int(get_jwt_identity())
    order = get_order_details_service(user_id, order_id)
    
    if not order:
        return jsonify({"error": "Order not found or access denied"}), 404
        
    return jsonify(serialize_order(order)), 200