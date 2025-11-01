from app.extensions import db
from app.models.ecommerce_models import Order, OrderStatus
from app.models.user_models import User
from sqlalchemy.orm import joinedload
import enum

def get_all_orders_service():
    """ Lấy tất cả đơn hàng, join với thông tin user và tránh lỗi null. """
    try:
        orders = db.session.query(Order).options(
            joinedload(Order.user)
        ).order_by(
            Order.created_at.desc()
        ).all()

        result = []
        for order in orders:
            user_info = None
            if order.user:
                user_info = {
                    "id": order.user.id,
                    "email": order.user.email,
                }
                # nếu user có user_info thì lấy thêm full_name
                if hasattr(order.user, "user_info") and order.user.user_info:
                    user_info["name"] = order.user.user_info.full_name
                else:
                    user_info["name"] = None

            result.append({
                "id": order.id,
                "user": user_info,
                "address": order.address,
                "total_amount": order.total_amount,
                "status": order.status.name if order.status else None,
                "created_at": order.created_at
            })

        return {"orders": result}, 200

    except Exception as e:
        print(f"Error fetching all orders: {e}")
        return {"error": "Failed to retrieve orders"}, 500


def update_order_status_service(order_id, new_status_str):
    """ Cập nhật trạng thái của một đơn hàng. """
    order = Order.query.get(order_id)
    if not order:
        return {"error": "Order not found"}, 404

    try:
        new_status_enum = OrderStatus[new_status_str.upper()]
    except KeyError:
        valid_statuses = [s.name for s in OrderStatus]
        return {"error": f"Invalid status. Must be one of: {valid_statuses}"}, 400

    try:
        order.status = new_status_enum
        db.session.commit()
        return {"message": f"Order {order_id} status updated to {new_status_enum.name}"}, 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating order status: {e}")
        return {"error": "Failed to update order status"}, 500
