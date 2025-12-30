from flask import Blueprint, jsonify, request
from app.models import *
category_bp = Blueprint('category', __name__, url_prefix='/category')

@category_bp.route('/', methods=['GET'])
def get_all_categories():
    cats = Category.query.all()
    return jsonify([{
        "id": c.id,
        "name": c.name
    } for c in cats]), 200