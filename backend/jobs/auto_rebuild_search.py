import os, sys
from sqlalchemy import func
from app import create_app, db
from app.models.product_models import Product
from jobs.run_search_indexing import build_search_index
from config import DevelopmentConfig

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
print("[DEBUG] Added to sys.path:", BASE_DIR)

INDEX_FILE = "instance/search/search_index.faiss"
MAP_FILE = "instance/search/product_id_map.pkl"

def auto_rebuild_search_index():
    """Tự động rebuild FAISS index nếu chưa tồn tại hoặc DB có sản phẩm mới."""
    print("[AUTO] Checking FAISS search index...")

    # Tạo Flask app context

    app = create_app(DevelopmentConfig)

    with app.app_context():
        # Đếm số sản phẩm hiện có
        product_count = db.session.query(func.count(Product.id)).scalar() or 0
        print(f"[AUTO] Product count in DB: {product_count}")

        # Nếu không có index, rebuild
        if not os.path.exists(INDEX_FILE) or not os.path.exists(MAP_FILE):
            print("[AUTO] Search index not found, building new one...")
            build_search_index()
            return

        # Nếu index tồn tại, kiểm tra xem có thay đổi DB (số lượng sản phẩm)
        meta_file = "instance/search/meta.txt"
        previous_count = 0
        if os.path.exists(meta_file):
            with open(meta_file, "r") as f:
                try:
                    previous_count = int(f.read().strip())
                except ValueError:
                    previous_count = 0

        if product_count != previous_count:
            print("[AUTO] Product count changed, rebuilding FAISS index...")
            build_search_index()
        else:
            print("[AUTO] Search index already up-to-date.")

        # Cập nhật meta.txt
        os.makedirs(os.path.dirname(meta_file), exist_ok=True)
        with open(meta_file, "w") as f:
            f.write(str(product_count))

if __name__ == "__main__":
    auto_rebuild_search_index()