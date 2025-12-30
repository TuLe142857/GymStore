from flask import Blueprint, jsonify, request
from app.models import *
brand_bp = Blueprint('brand', __name__, url_prefix='/brand')

@brand_bp.route('/', methods=['GET'])
def get_all_brands():
    brands = Brand.query.all()
    return jsonify([{
        "id": b.id,
        "name": b.name
    } for b in brands]), 200