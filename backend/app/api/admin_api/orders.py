from flask import jsonify, request
from app.services.admin_service import get_all_orders_service, update_order_status_service
from . import admin_bp
from .decorators import admin_required

@admin_bp.route("/orders", methods=["GET"])
@admin_required
def handle_get_all_orders():
    """[ADMIN] Lấy tất cả đơn hàng."""
    result, status = get_all_orders_service()
    return jsonify(result), status

@admin_bp.route("/orders/<int:order_id>/status", methods=["PUT"])
@admin_required
def handle_update_order_status(order_id):
    """[ADMIN] Cập nhật trạng thái đơn hàng."""
    data = request.get_json()
    new_status = data.get("status")

    if not new_status:
        return jsonify({"error": "Missing 'status' in request body"}), 400

    result, status = update_order_status_service(order_id, new_status)
    return jsonify(result), status