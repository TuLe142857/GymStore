# interaction_service.py
from datetime import datetime
# Giả sử db được import từ app.extensions hoặc app.models tùy cấu trúc của bạn
try:
    from app.extensions import db 
except ImportError:
    from app.models import db # Hoặc cách import db phù hợp

# Import các model mới
from app.models.ecommerce_models import Interaction, InteractionType # <-- Dùng Enum
from app.models.user_models import User
from app.models.product_models import Product

def log_interaction(user_id, product_id, interaction_type_str): # Nhận vào string
    """
    Ghi lại một tương tác của người dùng với sản phẩm.
    interaction_type_str phải là một trong các giá trị của InteractionType Enum.
    """
    user = User.query.get(user_id)
    product = Product.query.get(product_id)

    if not user or not product:
        return {"error": "User or Product not found"}, 404

    # Chuyển đổi string sang Enum member
    try:
        interaction_type_enum = InteractionType[interaction_type_str.upper()]
    except KeyError:
        # Nếu string không khớp với bất kỳ member nào của Enum
        valid_types = [e.name for e in InteractionType]
        return {"error": f"Invalid interaction type. Valid types are: {valid_types}"}, 400

    try:
        new_interaction = Interaction(
            user_id=user_id,
            product_id=product_id,
            type=interaction_type_enum, # <-- Lưu Enum member vào DB
            # timestamp tự động được set bởi default=func.now() trong model
        )

        db.session.add(new_interaction)
        db.session.commit()

        return {"message": "Interaction logged successfully"}, 201

    except Exception as e:
        db.session.rollback()
        # Log lỗi ra console để debug
        print(f"Error logging interaction: {str(e)}")
        return {"error": "An internal error occurred while logging interaction."}, 500 