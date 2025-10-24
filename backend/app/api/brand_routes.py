from flask import Blueprint, jsonify, request

brand_bp = Blueprint('brand', __name__, url_prefix='/brand')