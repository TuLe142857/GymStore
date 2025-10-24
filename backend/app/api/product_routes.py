from flask import Blueprint, jsonify, request

product_bp = Blueprint('product', __name__, url_prefix='/product')