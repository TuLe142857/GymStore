# app/services/feedback_service.py
from datetime import datetime
from app.extensions import db
from app.models.product_models import Product
from app.models.ecommerce_models import Feedback, Order, OrderItem
from app.models.user_models import User, UserInfor


# 🟢 LẤY DANH SÁCH FEEDBACK CHO 1 SẢN PHẨM
def get_feedback_for_product(product_id):
    """
    Trả về danh sách feedback (rating + comment + user_name) của một sản phẩm.
    """
    try:
        # Kiểm tra sản phẩm tồn tại
        product = Product.query.get(product_id)
        if not product:
            return {"error": "Product not found"}, 404

        # Join Feedback + User + UserInfor
        feedbacks = (
            db.session.query(
                Feedback.id,
                Feedback.rating,
                Feedback.comment,
                Feedback.created_at,
                UserInfor.full_name.label("user_name"),
            )
            .join(User, Feedback.user_id == User.id)
            .join(UserInfor, UserInfor.user_id == User.id)
            .filter(Feedback.product_id == product_id)
            .order_by(Feedback.created_at.desc())
            .all()
        )

        # Format dữ liệu trả về
        feedback_list = [
            {
                "id": f.id,
                "rating": f.rating,
                "comment": f.comment,
                "created_at": f.created_at,
                "user_name": f.user_name,
            }
            for f in feedbacks
        ]

        return feedback_list, 200

    except Exception as e:
        print(f"[ERROR] get_feedback_for_product(): {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


# 🟢 THÊM / CẬP NHẬT FEEDBACK CHO 1 SẢN PHẨM
def add_product_feedback(user_id, product_id, rating, comment):
    """
    Tạo hoặc cập nhật feedback của người dùng cho một sản phẩm.
    - Nếu user đã từng feedback sản phẩm đó → cập nhật
    - Nếu chưa → tạo mới
    """
    try:
        # Kiểm tra sản phẩm tồn tại
        product = Product.query.get(product_id)
        if not product:
            return {"error": "Product not found"}, 404

        # Validate rating
        if rating is None or not (1 <= rating <= 5):
            return {"error": "A valid rating (1-5) is required"}, 400

        # Tìm feedback cũ (nếu có)
        feedback = Feedback.query.filter_by(user_id=user_id, product_id=product_id).first()

        if feedback:
            # Cập nhật feedback cũ
            feedback.rating = rating
            feedback.comment = comment
            feedback.created_at = datetime.utcnow()
        else:
            # Tạo feedback mới
            feedback = Feedback(
                user_id=user_id,
                product_id=product_id,
                rating=rating,
                comment=comment,
                created_at=datetime.utcnow(),
            )
            db.session.add(feedback)

        db.session.commit()

        # Sau khi commit → cập nhật điểm trung bình sản phẩm
        update_product_rating_stats(product_id)

        return {"message": "Feedback submitted successfully"}, 201

    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] add_product_feedback(): {str(e)}")
        return {"error": "Failed to submit feedback"}, 500


# 🟢 HÀM CẬP NHẬT ĐIỂM TRUNG BÌNH FEEDBACK CHO SẢN PHẨM
def update_product_rating_stats(product_id):
    """
    Cập nhật avg_rating và feedback_count trong bảng Product
    """
    try:
        stats = (
            db.session.query(
                db.func.count(Feedback.id),
                db.func.avg(Feedback.rating)
            )
            .filter(Feedback.product_id == product_id)
            .first()
        )

        count, avg = stats
        product = Product.query.get(product_id)
        if product:
            product.feedback_count = count or 0
            product.avg_rating = float(round(avg, 2)) if avg else 0.0
            db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] update_product_rating_stats(): {str(e)}")

def has_user_reviewed_product(user_id, product_id):
    """
    Kiểm tra xem user đã review sản phẩm này chưa.
    """
    existing = Feedback.query.filter_by(
        user_id=user_id, 
        product_id=product_id
    ).first()
    return existing is not None