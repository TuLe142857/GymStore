from flask import jsonify
from sqlalchemy import func
from app.models import *
from . import admin_bp
from .decorators import admin_required


@admin_bp.route("/stats", methods=["GET"])
@admin_required
def get_dashboard_stats():
    return jsonify({
        "data": "dang code, cho xiu..."
    }), 200