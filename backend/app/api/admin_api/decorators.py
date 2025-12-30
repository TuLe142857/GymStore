from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user_models import User


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        try:
            current_user_id = int(get_jwt_identity())
            current_user = User.query.get(current_user_id)
        except Exception:
            return jsonify({"error": "Invalid user identity"}), 401

        if not current_user or not current_user.role or current_user.role.name != "ADMIN":
            return jsonify({"error": "Admin access required"}), 403

        return fn(*args, **kwargs)

    return wrapper