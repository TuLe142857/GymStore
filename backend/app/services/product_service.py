try:
    from app.extensions import db
except ImportError:
    from app.models import db
    
from app.models.product_models import Product, Category, Brand, ProductIngredient, Ingredient
from app.models.ecommerce_models import Feedback
from app.models.user_models import User
from sqlalchemy.orm import joinedload, subqueryload

def get_all_products_service(args):
    """ Lấy danh sách sản phẩm với filter và phân trang. """
    query = Product.query.filter(Product.is_active == True)
    
    # Filter theo category
    category_id = args.get('category_id')
    if category_id:
        query = query.filter(Product.category_id == category_id)
        
    # Filter theo brand
    brand_id = args.get('brand_id')
    if brand_id:
        query = query.filter(Product.brand_id == brand_id)
        
    search = args.get('search')
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
        
    # Tối ưu query: chỉ load category và brand
    query = query.options(
        joinedload(Product.category),
        joinedload(Product.brand)
    )
    
    # Sắp xếp
    sort_by = args.get('sort_by', 'name')
    sort_order = args.get('order', 'asc')
    
    if hasattr(Product, sort_by):
        if sort_order == 'desc':
            query = query.order_by(getattr(Product, sort_by).desc())
        else:
            query = query.order_by(getattr(Product, sort_by).asc())

    # Phân trang
    try:
        page = int(args.get('page', 1))
        per_page = int(args.get('per_page', 10))
    except ValueError:
        page = 1
        per_page = 10
        
    paginated_products = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return paginated_products

def get_product_by_id_service(product_id):
    """ Lấy chi tiết 1 sản phẩm, eager load các quan hệ. """
    product = Product.query.options(
        joinedload(Product.category),
        joinedload(Product.brand),
        # Load thành phần: Product -> ProductIngredient -> Ingredient
        joinedload(Product.ingredient_associations).joinedload(ProductIngredient.ingredient),
        # Load feedback: Product -> Feedback -> User
        joinedload(Product.feedbacks).joinedload(Feedback.user)
    ).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        return None
    
    return product

def get_all_categories_service():
    """ Lấy tất cả danh mục. """
    return Category.query.all()

def get_all_brands_service():
    """ Lấy tất cả thương hiệu. """
    return Brand.query.all()