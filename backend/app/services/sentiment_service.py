import os
import pickle
import numpy as np
from app.extensions import db
from app.models.ecommerce_models import Feedback

# --- Định nghĩa đường dẫn ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODEL_DIR = os.path.join(BASE_DIR, 'instance', 'sentiment')
MODEL_PATH = os.path.join(MODEL_DIR, 'sentiment_model.pkl')

# --- Tải mô hình (load on startup) ---
def load_sentiment_model():
    """ Tải mô hình sentiment từ file .pkl """
    if not os.path.exists(MODEL_PATH):
        print(f"[WARN] Sentiment model file not found at {MODEL_PATH}. Feature will be disabled.")
        return None
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        print(f"[INFO] Sentiment model loaded successfully from {MODEL_PATH}.")
        return model
    except Exception as e:
        print(f"[ERROR] Failed to load sentiment model: {e}")
        return None

# Biến toàn cục chứa mô hình
SENTIMENT_MODEL = load_sentiment_model()

# --- Hàm service chính ---
def analyze_product_sentiment(product_id):
    """
    Phân tích cảm xúc của tất cả feedback cho một sản phẩm
    và trả về tỷ lệ % Positive, Neutral, Negative.
    """
    if SENTIMENT_MODEL is None:
        return {"error": "Sentiment analysis service is not available."}, 503

    try:
        # 1. Lấy tất cả comment của sản phẩm
        results = db.session.query(Feedback.comment).filter(
            Feedback.product_id == product_id,
            Feedback.comment.isnot(None) & (Feedback.comment != '')
        ).all()

        if not results:
            return {"total_reviews": 0, "summary": {}}, 200

        comments = [c[0] for c in results]
        total_reviews = len(comments)

        # 2. Dùng mô hình để dự đoán
        predictions = SENTIMENT_MODEL.predict(comments)

        # 3. Tổng hợp kết quả
        (unique, counts) = np.unique(predictions, return_counts=True)
        sentiment_counts = dict(zip(unique, counts))

        summary = {
            "POSITIVE": int(sentiment_counts.get("POSITIVE", 0)),
            "NEUTRAL": int(sentiment_counts.get("NEUTRAL", 0)),
            "NEGATIVE": int(sentiment_counts.get("NEGATIVE", 0)),
        }
        
        # Tính toán phần trăm
        summary_pct = {
            "positive_pct": round((summary["POSITIVE"] / total_reviews) * 100, 1),
            "neutral_pct": round((summary["NEUTRAL"] / total_reviews) * 100, 1),
            "negative_pct": round((summary["NEGATIVE"] / total_reviews) * 100, 1),
        }

        return {
            "total_reviews": total_reviews,
            "summary_counts": summary,
            "summary_percent": summary_pct
        }, 200

    except Exception as e:
        print(f"[ERROR] analyze_product_sentiment: {e}")
        return {"error": "Failed to analyze sentiment"}, 500