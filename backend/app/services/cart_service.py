from app.extensions import db
from app.models.ecommerce_models import Cart, CartItem
from app.models.product_models import Product
from app.utils.serializers import serialize_cart, serialize_cart_item
from sqlalchemy.orm import joinedload


def get_user_cart_service(user_id):
    """
    Lấy giỏ hàng của user. Nếu chưa có, tạo mới.
    Eager load items và product của items để tối ưu truy vấn.
    """
    cart = Cart.query.options(
        joinedload(Cart.items)
        .joinedload(CartItem.product)
        .joinedload(Product.category),
        joinedload(Cart.items)
        .joinedload(CartItem.product)
        .joinedload(Product.brand),
    ).filter_by(user_id=user_id).first()

    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()

    return cart


def add_to_cart_service(user_id, product_id, quantity):
    """
    Thêm sản phẩm vào giỏ hàng, hoặc cập nhật số lượng nếu đã tồn tại.
    """
    cart = get_user_cart_service(user_id)
    product = Product.query.get(product_id)

    if not product or not product.is_active:
        return {"error": "Product not found or inactive"}, 404

    if product.stock_quantity < quantity:
        return {"error": "Not enough stock"}, 400

    cart_item = CartItem.query.filter_by(
        cart_id=cart.id, product_id=product_id
    ).first()

    if cart_item:
        new_quantity = cart_item.quantity + quantity
        if product.stock_quantity < new_quantity:
            return {"error": "Not enough stock for updated quantity"}, 400
        cart_item.quantity = new_quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id, product_id=product_id, quantity=quantity
        )
        db.session.add(cart_item)

    db.session.commit()

    return {
        "message": "Item added to cart",
        "cart_item": serialize_cart_item(cart_item),
    }, 201


def update_cart_item_service(user_id, cart_item_id, quantity):
    """
    Cập nhật số lượng của một item trong giỏ.
    Nếu quantity = 0 → xóa item.
    """
    cart = get_user_cart_service(user_id)
    cart_item = CartItem.query.get(cart_item_id)

    if not cart_item or cart_item.cart_id != cart.id:
        return {"error": "Cart item not found in user's cart"}, 404

    product = cart_item.product

    if quantity == 0:
        db.session.delete(cart_item)
        db.session.commit()
        return {"message": "Item removed from cart"}, 200

    if product.stock_quantity < quantity:
        return {"error": "Not enough stock"}, 400

    cart_item.quantity = quantity
    db.session.commit()

    return {
        "message": "Cart item updated",
        "cart_item": serialize_cart_item(cart_item),
    }, 200


def remove_from_cart_service(user_id, cart_item_id):
    """
    Xóa một item khỏi giỏ hàng.
    """
    cart = get_user_cart_service(user_id)
    cart_item = CartItem.query.get(cart_item_id)

    if not cart_item or cart_item.cart_id != cart.id:
        return {"error": "Cart item not found in user's cart"}, 404

    db.session.delete(cart_item)
    db.session.commit()

    return {"message": "Item removed from cart"}, 200


def clear_cart_service(user_id):
    """
    Xóa toàn bộ giỏ hàng của user (thường dùng sau khi đặt hàng).
    """
    cart = get_user_cart_service(user_id)
    if not cart.items:
        return {"message": "Cart already empty"}, 200

    for item in cart.items:
        db.session.delete(item)

    db.session.commit()
    return {"message": "Cart cleared"}, 200
