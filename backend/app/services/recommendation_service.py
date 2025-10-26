# recommendation_service.py
import pandas as pd
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
from sqlalchemy import func, desc

# Giả sử db được import từ app.extensions hoặc app.models tùy cấu trúc của bạn
try:
    from app.extensions import db
except ImportError:
    from app.models import db # Hoặc cách import db phù hợp

# Import các model mới
from app.models.product_models import Product, Category, Brand, Ingredient, ProductIngredient
from app.models.ecommerce_models import Interaction, InteractionType # <-- Import Enum

# Thư viện Surprise (giữ nguyên)
from surprise import Dataset, Reader, SVD

# --- ĐỊNH NGHĨA ĐƯỜNG DẪN (Giữ nguyên hoặc điều chỉnh nếu cần) ---
# Xác định thư mục gốc của project (nơi chứa thư mục app)
# Điều chỉnh nếu cấu trúc thư mục của bạn khác
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODEL_DIR = os.path.join(BASE_DIR, 'instance', 'recommendations') # Lưu vào instance để không bị ghi đè khi deploy

MATRIX_PATH = os.path.join(MODEL_DIR, 'similarity_matrix.pkl')
MAPPING_PATH = os.path.join(MODEL_DIR, 'product_id_mapping.pkl')
CF_MODEL_PATH = os.path.join(MODEL_DIR, 'cf_model.pkl')
# Bỏ CF_DATA_PATH vì đã lưu trainset trong CF_MODEL_PATH

print(f"[DEBUG] Model directory set to: {MODEL_DIR}")

# --- HÀM LẤY TOP SẢN PHẨM (FALLBACK - Dùng Enum) ---
def get_top_products(top_n=10):
    """
    Lấy Top N sản phẩm được mua nhiều nhất (sử dụng Enum).
    """
    print(f"Fetching top {top_n} products based on purchase count...")
    try:
        top_products_query = db.session.query(
            Interaction.product_id,
            func.count(Interaction.product_id).label('purchase_count')
        ).filter(
            Interaction.type == InteractionType.PURCHASE # <-- Dùng Enum
        ).group_by(
            Interaction.product_id
        ).order_by(
            desc('purchase_count')
        ).limit(
            top_n
        )
        # print(f"DEBUG: Top products query: {top_products_query}") # Debug query
        top_products = top_products_query.all()

        if not top_products:
            print("No purchase data found. Falling back to first N products.")
            products = Product.query.limit(top_n).all()
            return [p.id for p in products], 200

        product_ids = [p[0] for p in top_products]
        print(f"Top product IDs: {product_ids}")
        return product_ids, 200

    except Exception as e:
        print(f"Error fetching top products: {e}")
        db.session.rollback() # Quan trọng: rollback nếu có lỗi DB
        return [], 500

# --- CẬP NHẬT HÀM LẤY CORPUS SẢN PHẨM (Đúng relationship) ---
def _get_product_corpus():
    """
    Lấy dữ liệu sản phẩm từ DB và tạo 'văn bản' mô tả cho mỗi sản phẩm.
    Đã cập nhật tên relationship.
    """
    print("Fetching product data from database...")
    products = db.session.query(Product).options(
        db.joinedload(Product.category),
        db.joinedload(Product.brand),
        # Sử dụng tên relationship 'ingredient_associations' từ Product model
        # và join tiếp từ ProductIngredient tới Ingredient qua relationship 'ingredient'
        db.joinedload(Product.ingredient_associations).joinedload(ProductIngredient.ingredient)
    ).filter(Product.is_active == True).all() # Chỉ lấy sản phẩm active

    data = []
    for p in products:
        category_name = p.category.name if p.category else ''
        brand_name = p.brand.name if p.brand else ''
        # Truy cập ingredient thông qua association
        ingredients = ' '.join([assoc.ingredient.name for assoc in p.ingredient_associations if assoc.ingredient])

        corpus = f"{p.name or ''} {p.desc or ''} {category_name} {brand_name} {ingredients}"

        data.append({
            "id": p.id,
            "name": p.name,
            "corpus": corpus.strip() # Loại bỏ khoảng trắng thừa
        })

    if not data:
        raise Exception("No active product data found to build model.")

    return pd.DataFrame(data)

# --- HÀM BUILD MA TRẬN TƯƠNG TỰ (Không đổi logic chính) ---
def build_similarity_matrix():
    """ Huấn luyện TF-IDF và tính Cosine Similarity. """
    try:
        nltk.download('stopwords', quiet=True)
        stop_words = set(stopwords.words('english'))
    except Exception as e:
        print(f"Warning: Could not download stopwords: {e}")
        stop_words = None

    df = _get_product_corpus()
    if df.empty:
      print("Cannot build similarity matrix: No product data.")
      return

    print(f"Building TF-IDF matrix for {len(df)} products...")
    tfidf = TfidfVectorizer(stop_words=list(stop_words) if stop_words else None, min_df=2) # min_df=2 để bỏ từ quá hiếm
    tfidf_matrix = tfidf.fit_transform(df['corpus'])

    print("Calculating cosine similarity matrix...")
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    id_to_index = pd.Series(df.index, index=df['id']).to_dict()
    index_to_id = pd.Series(df['id'], index=df.index).to_dict()

    os.makedirs(MODEL_DIR, exist_ok=True)
    print(f"Saving similarity models to {MODEL_DIR}...")
    try:
        with open(MATRIX_PATH, 'wb') as f:
            pickle.dump(cosine_sim, f)
        with open(MAPPING_PATH, 'wb') as f:
            pickle.dump({'id_to_index': id_to_index, 'index_to_id': index_to_id}, f)
        print("Content-based model built successfully.")
    except Exception as e:
        print(f"ERROR saving similarity models: {e}")


# --- CẬP NHẬT HÀM LẤY DỮ LIỆU TƯƠNG TÁC (Dùng Enum) ---
def _get_interaction_data():
    """ Lấy dữ liệu Interaction và gán rating dựa trên Enum type. """
    print("Fetching interaction data...")
    interactions = Interaction.query.all()

    if not interactions:
        raise Exception("No interaction data found for CF model.")

    interaction_weights = {
        InteractionType.VIEW: 1.0,
        InteractionType.ADD_TO_CART: 3.0,
        InteractionType.PURCHASE: 5.0
    }

    data = []
    for i in interactions:
        if i.type in interaction_weights:
            data.append({
                'user_id': i.user_id,
                'product_id': i.product_id,
                'rating': interaction_weights[i.type]
            })

    df = pd.DataFrame(data)
    if df.empty:
         raise Exception("Interaction data processed but resulted in empty DataFrame.")

    # Lấy rating cao nhất nếu có nhiều tương tác trùng
    df = df.groupby(['user_id', 'product_id'])['rating'].max().reset_index()

    print(f"Processed {len(df)} user-item ratings.")
    return df

# --- HÀM BUILD MÔ HÌNH CF (Không đổi logic chính) ---
def build_collaborative_model():
    """ Huấn luyện mô hình SVD và lưu lại. """
    try:
        df = _get_interaction_data()
    except Exception as e:
        print(f"Cannot build CF model: {e}")
        return

    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[['user_id', 'product_id', 'rating']], reader)
    trainset = data.build_full_trainset()

    print("Training SVD model...")
    algo = SVD(n_factors=50, n_epochs=30, lr_all=0.005, reg_all=0.04, random_state=42) # Tinh chỉnh tham số
    algo.fit(trainset)

    os.makedirs(MODEL_DIR, exist_ok=True)
    print(f"Saving CF model to {MODEL_DIR}...")
    dump_data = {'model': algo, 'trainset': trainset}
    try:
        with open(CF_MODEL_PATH, 'wb') as f:
            pickle.dump(dump_data, f)
        print("Collaborative Filtering model built successfully.")
    except Exception as e:
        print(f"ERROR saving CF model: {e}")


# --- HÀM GET GỢI Ý (Không đổi logic chính) ---
def get_similar_products(product_id, top_n=5):
    """ Lấy Top N sản phẩm tương tự (Content-Based). """
    print(f"Loading similarity models for product_id: {product_id}")
    if not os.path.exists(MATRIX_PATH) or not os.path.exists(MAPPING_PATH):
         print("Error: Similarity model files not found. Please run the training job.")
         # Cân nhắc build lại nếu file không tồn tại? Hoặc chỉ trả lỗi.
         # build_similarity_matrix() # Có thể thêm dòng này nếu muốn tự build khi thiếu
         return [], 503 # Service Unavailable

    try:
        with open(MATRIX_PATH, 'rb') as f:
            cosine_sim = pickle.load(f)
        with open(MAPPING_PATH, 'rb') as f:
            mapping = pickle.load(f)
            id_to_index = mapping['id_to_index']
            index_to_id = mapping['index_to_id']
    except Exception as e:
        print(f"Error loading similarity models: {e}")
        return [], 500

    if product_id not in id_to_index:
        print(f"Warning: Product ID {product_id} not found in model mapping.")
        return [], 404 # Not Found hợp lý hơn

    idx = id_to_index[product_id]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:top_n+1]
    product_indices = [i[0] for i in sim_scores]
    # Lọc ra các index hợp lệ trước khi truy cập index_to_id
    recommended_product_ids = [index_to_id[i] for i in product_indices if i in index_to_id]

    print(f"Similar product IDs found: {recommended_product_ids}")
    return recommended_product_ids, 200

def get_collaborative_recommendations(user_id, top_n=10):
    """ Lấy Top N gợi ý cá nhân hóa (Collaborative Filtering). """
    print(f"Loading CF model for user_id: {user_id}")
    if not os.path.exists(CF_MODEL_PATH):
        print("Error: CF Model file not found. Please run the training job.")
        # build_collaborative_model() # Có thể thêm dòng này nếu muốn tự build khi thiếu
        return [], 503 # Service Unavailable

    try:
        with open(CF_MODEL_PATH, 'rb') as f:
            dump_data = pickle.load(f)
            algo = dump_data['model']
            trainset = dump_data['trainset']
    except Exception as e:
        print(f"Error loading CF models: {e}")
        return [], 500

    try:
        user_inner_id = trainset.to_inner_uid(user_id)
    except ValueError:
        print(f"User ID {user_id} is a new user (cold start). Cannot provide CF recos.")
        return [], 200 # OK, trả về rỗng để route xử lý fallback

    interacted_items = set([item_inner_id for (item_inner_id, rating) in trainset.ur[user_inner_id]])
    all_items = set(trainset.all_items())
    items_to_predict = all_items - interacted_items

    if not items_to_predict:
        print(f"User {user_id} has interacted with all available items. No new recommendations.")
        return [], 200

    predictions = []
    # Lấy danh sách raw_iids (product_id gốc) để dự đoán
    raw_iids_to_predict = [trainset.to_raw_iid(inner_id) for inner_id in items_to_predict]

    # Kiểm tra xem sản phẩm có còn active không trước khi dự đoán
    active_product_ids = {p.id for p in Product.query.filter(Product.id.in_(raw_iids_to_predict), Product.is_active == True).all()}

    for item_raw_id in active_product_ids:
         pred = algo.predict(uid=user_id, iid=item_raw_id)
         predictions.append((item_raw_id, pred.est))

    predictions.sort(key=lambda x: x[1], reverse=True)
    recommended_product_ids = [pid for (pid, rating) in predictions[:top_n]]

    print(f"CF recommendations for user {user_id}: {recommended_product_ids}")
    return recommended_product_ids, 200