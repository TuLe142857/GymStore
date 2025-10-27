import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
BASE_PATH = "instance/search"
INDEX_FILE = os.path.join(BASE_PATH, "search_index.faiss")
MAP_FILE = os.path.join(BASE_PATH, "product_id_map.pkl")


class SearchService:
    """
    Service chịu trách nhiệm load model và FAISS index.
    Không rebuild tại đây để tránh circular import — việc rebuild được tách riêng ra job auto_rebuild_search.py
    """
    def __init__(self):
        self.model = None
        self.index = None
        self.product_id_map = None
        try:
            print("[INFO] Loading SearchService...")
            self.model = SentenceTransformer(MODEL_NAME)

            if not os.path.exists(INDEX_FILE) or not os.path.exists(MAP_FILE):
                raise FileNotFoundError(f"{INDEX_FILE} not found. Please run FAISS indexing job first.")

            self.index = faiss.read_index(INDEX_FILE)
            with open(MAP_FILE, "rb") as f:
                self.product_id_map = pickle.load(f)

            print(f"[INFO] SearchService loaded successfully with {len(self.product_id_map)} products.")

        except Exception as e:
            print(f"[WARN] SearchService initialization failed: {e}")
            self.model = self.index = self.product_id_map = None

    def search_products(self, query_text, k=20):
        """
        Tìm kiếm sản phẩm tương tự bằng FAISS + SentenceTransformer.
        """
        if not all([self.model, self.index, self.product_id_map]):
            print("[WARN] SearchService not initialized properly.")
            return []

        try:
            qv = self.model.encode([query_text], convert_to_tensor=False)
            D, I = self.index.search(np.array(qv, dtype="float32"), k)
            return [self.product_id_map.get(i) for i in I[0] if i != -1]
        except Exception as e:
            print(f"[ERROR] Search failed: {e}")
            return []


# Singleton instance (global)
search_service_instance = SearchService()
