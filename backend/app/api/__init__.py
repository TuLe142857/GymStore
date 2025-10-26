from flask import Blueprint
from .auth_routes import auth_bp
from .brand_routes import brand_bp
from .cart_routes import cart_bp
from .category_routes import category_bp
from .order_route import order_bp
from .product_routes import product_bp
from .upload_routes import upload_bp

from .recommendation_routes import recommendation_bp
from .interaction_routes import interaction_bp

api_bp = Blueprint('api', __name__, url_prefix='/api')


api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(brand_bp)
api_bp.register_blueprint(cart_bp)
api_bp.register_blueprint(category_bp)
api_bp.register_blueprint(order_bp)
api_bp.register_blueprint(product_bp)
api_bp.register_blueprint(upload_bp)
api_bp.register_blueprint(recommendation_bp)
api_bp.register_blueprint(interaction_bp)  