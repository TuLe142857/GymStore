from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services import AuthService
from ..errors import BaseAppError
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

"""
            REGISTRATION
"""
@auth_bp.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    email = data.get('email')
    if email is None:
        raise BaseAppError('email is required', 400)

    AuthService.verify(email)

    return jsonify({'message': 'ok', 'data': []}), 200

@auth_bp.route('/verify-confirm', methods=['POST'])
def verify_confirm():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    if (not email) or (not otp) or (not otp):
        raise BaseAppError('email or otp is required', 400)

    registration_token = AuthService.verify_confirm(email, otp)

    return jsonify({'message': 'ok', 'data': {'registration_token': registration_token}}), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    registration_token = data.get('registration_token')

    refresh_token, access_token = AuthService.register(email, password, full_name, registration_token)

    return jsonify(
        {
            'message': 'ok',
            'data':{
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        }
    ), 200


"""
            LOGIN & AUTHENTICATION
"""

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    access_token, refresh_token = AuthService.login(data['email'], data['password'])
    return jsonify({
        'message':'ok',
        'data':{
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = AuthService.refresh_access_token(identity)
    return jsonify({'message': 'ok', 'data':{'access_token':access_token}}), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    if email is None:
        raise BaseAppError('email is required', 400)
    AuthService.forgot_password(email)
    return jsonify({'message': 'ok', 'data':[]}), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')
    if (not email) or (not otp) or (not new_password):
        raise BaseAppError('email or password or otp is required', 400)
    AuthService.reset_password(email, otp, new_password)
    return jsonify({'message': 'ok', 'data':[]}), 200


@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    data = request.get_json()
    identity = get_jwt_identity()
    password = data.get('password')
    new_password = data.get('new_password')
    if (not identity) or (not password) or (not new_password):
        raise BaseAppError('email or password or new_password is required', 400)

    AuthService.change_password(identity, password, new_password)
    return jsonify({'message': 'ok', 'data':[]}), 200

"""
            PROFILE
"""

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    identity = get_jwt_identity()
    profile = AuthService.get_profile(identity)
    return jsonify({'message': 'ok', 'data':{'profile': profile}}), 200


@auth_bp.route('/profile', methods=['POST'])
@jwt_required()
def update_profile():
    identity = get_jwt_identity()
    data = request.get_json()

    AuthService.update_profile(identity, data)
    return jsonify({'message': 'ok', 'data':[]}), 200
