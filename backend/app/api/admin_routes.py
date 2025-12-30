# from flask import Blueprint, jsonify, request
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from app.services.admin_service import (
#     get_all_orders_service,
#     update_order_status_service
# )
# from app.models.user_models import User # Import User để kiểm tra is_admin
#
# admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
#
#
# # --- Helper: Decorator để kiểm tra Admin ---
# from functools import wraps
# def admin_required(fn):
#     @wraps(fn)
#     @jwt_required()
#     def wrapper(*args, **kwargs):
#         try:
#             current_user_id = int(get_jwt_identity())
#             current_user = User.query.get(current_user_id)
#         except Exception:
#             return jsonify({"error": "Invalid user identity"}), 401
#
#         if not current_user or not current_user.role or current_user.role.name != "ADMIN":
#             return jsonify({"error": "Admin access required"}), 403
#
#         return fn(*args, **kwargs)
#     return wrapper
# # --- Hết Helper ---
#
#
# @admin_bp.route("/orders", methods=["GET"])
# @admin_required
# def handle_get_all_orders():
#     """
#     [ADMIN] Lấy tất cả đơn hàng trong hệ thống.
#     """
#     result, status = get_all_orders_service()
#     return jsonify(result), status
#
# @admin_bp.route("/orders/<int:order_id>/status", methods=["PUT"])
# @admin_required
# def handle_update_order_status(order_id):
#     """
#     [ADMIN] Cập nhật trạng thái một đơn hàng
#     (PROCESSING, DELIVERED, CANCELLED)
#     """
#     data = request.get_json()
#     new_status = data.get("status")
#
#     if not new_status:
#         return jsonify({"error": "Missing 'status' in request body"}), 400
#
#     result, status = update_order_status_service(order_id, new_status)
#     return jsonify(result), status