# app/services/order_service.py
try:
    from app.extensions import db
except ImportError:
    from app.models import db
    
from app.models.ecommerce_models import Order, OrderItem, OrderStatus, Cart
from app.models.product_models import Product
from app.services.cart_service import get_user_cart_service # Tái sử dụng
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

def create_order_from_cart_service(user_id, shipping_address):
    """
    Tạo đơn hàng từ giỏ hàng của user.
    Đây là một giao dịch (transaction):
    1. Kiểm tra giỏ hàng
    2. Kiểm tra tồn kho
    3. Tạo Order, OrderItem
    4. Trừ tồn kho
    5. Xóa CartItem
    """
    cart = get_user_cart_service(user_id)
    if not cart.items:
        return {"error": "Cart is empty"}, 400
    
    # Bắt đầu 1 transaction
    try:
        total_amount = 0
        order_items_to_create = []
        products_to_update = []
        
        # 1. & 2. Kiểm tra giỏ hàng và tồn kho
        for item in cart.items:
            product = item.product
            if not product.is_active:
                raise ValueError(f"Product '{product.name}' is no longer active.")
            if product.stock_quantity < item.quantity:
                raise ValueError(f"Not enough stock for '{product.name}'. Available: {product.stock_quantity}")
            
            # Tính tổng tiền
            item_total = product.price * item.quantity
            total_amount += item_total
            
            # Chuẩn bị OrderItem
            order_items_to_create.append(OrderItem(
                product_id=product.id,
                quantity=item.quantity,
                price_at_purchase=product.price # Lưu giá tại thời điểm mua
            ))
            
            # Chuẩn bị cập nhật kho
            products_to_update.append({"product": product, "quantity": item.quantity})

        # 3. Tạo Order
        new_order = Order(
            user_id=user_id,
            status=OrderStatus.PROCESSING,
            address=shipping_address,
            total_amount=total_amount
        )
         
        # Gắn OrderItem vào Order
        new_order.items = order_items_to_create
        db.session.add(new_order)
        
        # 4. Trừ tồn kho
        for p_info in products_to_update:
            # Dùng for_update để khóa hàng, đảm bảo tính nhất quán
            product_to_lock = Product.query.with_for_update().get(p_info["product"].id)
            if product_to_lock.stock_quantity < p_info["quantity"]: # Kiểm tra lại trong transaction
                 raise ValueError(f"Stock for '{product_to_lock.name}' was updated by another transaction.")
            product_to_lock.stock_quantity -= p_info["quantity"]
            
        # 5. Xóa CartItems
        for item in cart.items:
            db.session.delete(item)
            
        # Commit toàn bộ giao dịch
        db.session.commit()
        
        return {"message": "Order created successfully", "order": new_order}, 201

    except ValueError as e:
        db.session.rollback()
        return {"error": str(e)}, 400
    except Exception as e:
        import traceback
        print("❌ Error creating order:", e)
        traceback.print_exc()
        db.session.rollback()
        return {"error": str(e)}, 500

def get_user_orders_service(user_id):
    """ Lấy lịch sử đơn hàng của user, eager load items. """
    orders = Order.query.options(
        joinedload(Order.items) # Load item để đếm
    ).filter_by(
        user_id=user_id
    ).order_by(
        Order.created_at.desc()
    ).all()
    
    return orders

def get_order_details_service(user_id, order_id):
    """ Lấy chi tiết 1 đơn hàng, xác thực đúng user. """
    order = Order.query.options(
        joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.category),
        joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.brand)
    ).filter_by(
        id=order_id,
        user_id=user_id
    ).first()
    
    if not order:
        return None
        
    return order