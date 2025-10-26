# app/routes/cart_routes.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.cart_service import (
    get_user_cart_service,
    add_to_cart_service,
    update_cart_item_service,
    remove_from_cart_service
)
from app.utils.serializers import serialize_cart, serialize_cart_item

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/', methods=['GET'])
@jwt_required()
def get_cart():
    """ Lấy giỏ hàng của người dùng hiện tại. """
    user_id = int(get_jwt_identity())
    cart = get_user_cart_service(user_id)
    return jsonify(serialize_cart(cart)), 200

@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    """ Thêm sản phẩm vào giỏ hàng. """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id or not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "Invalid product_id or quantity"}), 400
        
    result, status_code = add_to_cart_service(user_id, product_id, quantity)
    
    if status_code == 201:
        # Thêm thành công, trả về giỏ hàng mới nhất
        cart = get_user_cart_service(user_id)
        return jsonify(serialize_cart(cart)), 201
    
    return jsonify(result), status_code

@cart_bp.route('/item/<int:cart_item_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(cart_item_id):
    """ Cập nhật số lượng của một item (có thể là 0 để xóa). """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    quantity = data.get('quantity')
    
    if quantity is None or not isinstance(quantity, int) or quantity < 0:
        return jsonify({"error": "Invalid quantity"}), 400
        
    result, status_code = update_cart_item_service(user_id, cart_item_id, quantity)
    
    if status_code == 200:
        cart = get_user_cart_service(user_id)
        return jsonify(serialize_cart(cart)), 200
        
    return jsonify(result), status_code

@cart_bp.route('/item/<int:cart_item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(cart_item_id):
    """ Xóa một item khỏi giỏ hàng. """
    user_id = int(get_jwt_identity())
    result, status_code = remove_from_cart_service(user_id, cart_item_id)
    
    if status_code == 200:
        cart = get_user_cart_service(user_id)
        return jsonify(serialize_cart(cart)), 200
        
    return jsonify(result), status_code