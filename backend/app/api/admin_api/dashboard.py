from flask import jsonify
from sqlalchemy import func
from app.models import *
from . import admin_bp
from .decorators import admin_required
from sqlalchemy.sql import func

def get_statistic_data():
    total_product = Product.query.count()
    out_stock_product = Product.query.filter(Product.stock_quantity < 0).count() | 0
    low_stock_product = Product.query.filter(Product.stock_quantity < 10).count() | 0

    pending_order = Order.query.filter(Order.status == OrderStatus.PROCESSING).count()


    return {
        "cards": [
            { "label": "Total Products", "value": total_product },
            { "label": "Out Stock Products", "value": out_stock_product },
            { "label": "Low Stock Products", "value": low_stock_product },
            { "label": "Pending Order", "value": pending_order }
        ],
        # "charts":[
        #     {
        #         "name": "chart 1",
        #         "type": "BarChart",
        #         "data": [
        #             {"label": "key1", "value": "1"},
        #             {"label": "key2", "value": "10"},
        #         ]
        #     },
        #     {
        #         "name": "chart 2",
        #         "type": "PieChart",
        #         "data": [
        #             {"label": "key1", "value": "1"},
        #             {"label": "key2", "value": "10"},
        #         ]
        #     }
        # ]
    }

@admin_bp.route("/statistics", methods=["GET"])
# @admin_required
def get_dashboard_stats():
    return jsonify(get_statistic_data()), 200
