from flask import Blueprint, jsonify, request

order_bp = Blueprint('order', __name__, url_prefix='/order')