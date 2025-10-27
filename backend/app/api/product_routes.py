from flask import Blueprint, jsonify, request
from app.services.product_service import (
    get_all_products_service, 
    get_product_by_id_service,
    get_all_categories_service,
    get_all_brands_service
)
from app.utils.serializers import (
    serialize_product_list, 
    serialize_product_detail, 
    serialize_category, 
    serialize_brand
)

product_bp = Blueprint('product', __name__, url_prefix='/product')

@product_bp.route('/', methods=['GET'])
def get_products():
    """
    Lấy danh sách sản phẩm, hỗ trợ filter và phân trang.
    Query params: category_id, brand_id, page, per_page, sort_by, order
    """
    args = request.args
    paginated_result = get_all_products_service(args)
    
    return jsonify({
    "products": paginated_result["products"],
    "pagination": paginated_result["pagination"]
    }), 200

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product_detail(product_id):
    """ Lấy chi tiết một sản phẩm. """
    product = get_product_by_id_service(product_id)
    
    if not product:
        return jsonify({'error': 'Product not found or inactive'}), 404
        
    return jsonify(serialize_product_detail(product)), 200

@product_bp.route('/categories', methods=['GET'])
def get_categories():
    """ Lấy tất cả danh mục. """
    categories = get_all_categories_service()
    return jsonify([serialize_category(c) for c in categories]), 200

@product_bp.route('/brands', methods=['GET'])
def get_brands():
    """ Lấy tất cả thương hiệu. """
    brands = get_all_brands_service()
    return jsonify([serialize_brand(b) for b in brands]), 200