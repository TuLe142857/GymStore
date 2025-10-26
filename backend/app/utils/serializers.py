#File này để quản lý việc chuyển đổi model sang JSON.

def serialize_product_list(p):
    """
    Serialize đối tượng Product cho chế độ xem danh sách (đơn giản).
    Sử dụng avg_rating và price từ model mới.
    """
    rating_value = float(p.avg_rating) if p.avg_rating is not None else 0.0
    
    return {
        "id": str(p.id),
        "name": p.name,
        "price": p.price, # price là Integer
        "image_url": p.image_url,
        "category": p.category.name if p.category else "Uncategorized",
        "brand": p.brand.name if p.brand else "Unbranded",
        "rating": round(rating_value, 1),
        "stock_quantity": p.stock_quantity
    }

def serialize_feedback(f):
    """ Serialize đối tượng Feedback. """
    return {
        "id": f.id,
        "rating": f.rating,
        "comment": f.comment,
        "created_at": f.created_at.isoformat(),
        "user": f.user.email if f.user else "Anonymous" # Chỉ hiển thị email hoặc tên
    }

def serialize_ingredient(pi):
    """ Serialize đối tượng ProductIngredient. """
    return {
        "id": pi.ingredient.id,
        "name": pi.ingredient.name,
        "quantity": pi.quantity
    }

def serialize_product_detail(p):
    """
    Serialize đối tượng Product cho chế độ xem chi tiết (đầy đủ).
    """
    base_data = serialize_product_list(p) # Kế thừa từ serializer đơn giản
    
    # Thêm thông tin chi tiết
    base_data.update({
        "desc": p.desc,
        "package_quantity": p.package_quantity,
        "package_unit": p.package_unit,
        "serving_quantity": p.serving_quantity,
        "serving_unit": p.serving_unit,
        "is_active": p.is_active,
        # Lấy danh sách thành phần
        "ingredients": [serialize_ingredient(pi) for pi in p.ingredient_associations],
        # Lấy danh sách feedback
        "feedbacks": [serialize_feedback(f) for f in p.feedbacks]
    })
    return base_data

def serialize_category(c):
    """ Serialize đối tượng Category. """
    return {
        "id": c.id,
        "name": c.name
    }

def serialize_brand(b):
    """ Serialize đối tượng Brand. """
    return {
        "id": b.id,
        "name": b.name
    }

def serialize_cart_item(ci):
    """ Serialize đối tượng CartItem. """
    return {
        "id": ci.id,
        "quantity": ci.quantity,
        "product": serialize_product_list(ci.product) if ci.product else None
    }

def serialize_cart(c):
    """ Serialize đối tượng Cart. """
    if not c:
        return None
    
    cart_items = [serialize_cart_item(item) for item in c.items]
    total_amount = sum(item['product']['price'] * item['quantity'] for item in cart_items if item['product'])
    
    return {
        "id": c.id,
        "user_id": c.user_id,
        "items": cart_items,
        "total_amount": total_amount,
        "updated_at": c.updated_at.isoformat()
    }

def serialize_order_item(oi):
    """ Serialize đối tượng OrderItem. """
    return {
        "id": oi.id,
        "quantity": oi.quantity,
        "price_at_purchase": oi.price_at_purchase, # Giá tại thời điểm mua
        "product": serialize_product_list(oi.product) if oi.product else None
    }

def serialize_order(o):
    """ Serialize đối tượng Order (chi tiết). """
    return {
        "id": o.id,
        "user_id": o.user_id,
        "status": o.status.name, # Lấy tên của Enum
        "address": o.address,
        "total_amount": o.total_amount,
        "items": [serialize_order_item(item) for item in o.items],
        "created_at": o.created_at.isoformat(),
        "updated_at": o.updated_at.isoformat()
    }

def serialize_order_list(o):
    """ Serialize đối tượng Order (cho danh sách, đơn giản). """
    return {
        "id": o.id,
        "status": o.status.name,
        "total_amount": o.total_amount,
        "item_count": len(o.items),
        "created_at": o.created_at.isoformat()
    }