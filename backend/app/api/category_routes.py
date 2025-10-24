from flask import Blueprint, jsonify, request

category_bp = Blueprint('category', __name__, url_prefix='/category')