from flask import Blueprint, jsonify, request

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')