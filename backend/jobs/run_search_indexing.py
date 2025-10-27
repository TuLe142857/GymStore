"""
Manual FAISS indexing builder.
Có thể gọi trực tiếp: python -m jobs.run_search_indexing
"""
import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from app import create_app, db
from app.models.product_models import Product
from config import DevelopmentConfig

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
SAVE_PATH = "instance/search"
INDEX_FILE = os.path.join(SAVE_PATH, "search_index.faiss")
MAP_FILE = os.path.join(SAVE_PATH, "product_id_map.pkl")


def build_search_index():
    """Build FAISS index từ dữ liệu sản phẩm."""
    print("[INFO] Building FAISS search index...")

    app = create_app(DevelopmentConfig)
    with app.app_context():
        os.makedirs(SAVE_PATH, exist_ok=True)

        products = Product.query.filter_by(is_active=True).all()
        if not products:
            print("[WARN] No products found for indexing.")
            return

        model = SentenceTransformer(MODEL_NAME)
        texts = []
        for p in products:
            name_part = p.name or ""
            desc_part = getattr(p, "description", "") or ""  # không lỗi nếu không có cột
            texts.append(f"{name_part} {desc_part}")
        vectors = model.encode(texts, convert_to_tensor=False)
        vectors = np.array(vectors, dtype="float32")

        index = faiss.IndexFlatL2(vectors.shape[1])
        index.add(vectors)
        faiss.write_index(index, INDEX_FILE)

        id_map = {i: p.id for i, p in enumerate(products)}
        with open(MAP_FILE, "wb") as f:
            pickle.dump(id_map, f)

        # Lưu meta thông tin để auto rebuild có thể check thay đổi
        with open(os.path.join(SAVE_PATH, "meta.txt"), "w") as f:
            f.write(str(len(products)))

        print(f"[OK] Search index built with {len(products)} products.")


if __name__ == "__main__":
    build_search_index()
