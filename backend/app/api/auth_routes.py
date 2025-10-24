from flask import Blueprint, jsonify, request

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')