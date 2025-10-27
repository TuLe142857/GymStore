from sqlalchemy.orm import joinedload
from sqlalchemy import case
from app.models.product_models import Product, Category, Brand, ProductIngredient, Ingredient
from app.models.ecommerce_models import Feedback
from app.models.user_models import User
from app.utils.serializers import serialize_product_list, serialize_pagination
from app.services.search_service import search_service_instance

# Intent mapping (rule-based hybrid layer)
INTENT_KEYWORDS = {
    "build muscle": ["whey", "protein", "isolate", "casein"],
    "gain weight": ["mass", "gainer", "bulking"],
    "lose fat": ["fat burner", "cutting", "lean", "thermogenic"],
    "increase energy": ["pre-workout", "caffeine", "booster"],
    "recovery": ["bcaa", "amino", "glutamine", "electrolyte"],
    "tired": ["pre-workout", "booster", "caffeine"],
    "focus": ["nootropic", "pre-workout", "energy"],
}


def get_all_products_service(args):
    """
    Lấy danh sách sản phẩm với tìm kiếm thông minh (semantic + intent hybrid),
    tránh N+1 query, có fallback an toàn.
    """
    query = Product.query.filter(Product.is_active == True)

    # --- Bộ lọc cơ bản ---
    category_id = args.get("category_id")
    if category_id:
        query = query.filter(Product.category_id == category_id)

    brand_id = args.get("brand_id")
    if brand_id:
        query = query.filter(Product.brand_id == brand_id)

    # --- Phân trang ---
    try:
        page = int(args.get("page", 1))
        per_page = int(args.get("per_page", 12))
    except ValueError:
        page, per_page = 1, 12

    # --- Tìm kiếm thông minh ---
    q = args.get("search") or args.get("q")
    semantic_search_applied = False  # Cờ kiểm soát sắp xếp semantic

    if q:
        q_lower = q.lower()

        # 1️⃣ Thử Semantic Search trước
        matched_product_ids = search_service_instance.search_products(q, k=50) or []

        if matched_product_ids:
            # Nếu FAISS trả về kết quả
            if len(matched_product_ids) > 0:
                query = query.filter(Product.id.in_(matched_product_ids))
                ordering = case(
                    {id_: idx for idx, id_ in enumerate(matched_product_ids)},
                    value=Product.id
                )
                query = query.order_by(ordering)
                semantic_search_applied = True
        else:
            # 2️⃣ Nếu semantic trống, thử Intent Detection
            intent_matches = []
            for intent, keywords in INTENT_KEYWORDS.items():
                if any(kw in q_lower for kw in [intent] + keywords):
                    intent_matches.extend(keywords)

            if intent_matches:
                intent_keyword = intent_matches[0]
                intent_query = query.filter(Product.name.ilike(f"%{intent_keyword}%"))
                if intent_query.count() > 0:
                    query = intent_query
                else:
                    # 3️⃣ Intent không ra gì → fallback keyword
                    query = query.filter(Product.name.ilike(f"%{q}%"))
            else:
                # 4️⃣ Không có intent nào → fallback keyword
                query = query.filter(Product.name.ilike(f"%{q}%"))

    # --- Sắp xếp (chỉ khi không dùng semantic) ---
    if not semantic_search_applied:
        sort_by = args.get("sort_by", "name")
        sort_order = args.get("order", "asc")
        if hasattr(Product, sort_by):
            query = query.order_by(
                getattr(Product, sort_by).desc() if sort_order == "desc"
                else getattr(Product, sort_by).asc()
            )

    # --- Load quan hệ cần thiết ---
    query = query.options(
        joinedload(Product.category),
        joinedload(Product.brand)
    )

    # --- Phân trang ---
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # --- Serialize (danh sách gọn nhẹ, không feedback/ingredients) ---
    serialized_products = [serialize_product_list(p) for p in pagination.items]
    serialized_pagination = serialize_pagination(pagination, "product.get_all_products")

    return {
        "products": serialized_products,
        "pagination": serialized_pagination,
    }


def get_product_by_id_service(product_id):
    """Lấy chi tiết sản phẩm (dùng eager load đầy đủ)."""
    product = Product.query.options(
        joinedload(Product.category),
        joinedload(Product.brand),
        joinedload(Product.ingredient_associations).joinedload(ProductIngredient.ingredient),
        joinedload(Product.feedbacks).joinedload(Feedback.user),
    ).filter(
        Product.id == product_id,
        Product.is_active == True,
    ).first()
    return product


def get_all_categories_service():
    """Lấy danh mục."""
    return Category.query.all()


def get_all_brands_service():
    """Lấy thương hiệu."""
    return Brand.query.all()
