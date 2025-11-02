# NỘI DUNG SỬA CHO: backend/jobs/run_sentiment_training.py

import os
import pickle
from collections import Counter
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.ecommerce_models import Feedback
from config import DevelopmentConfig 

# ---------------------------------------------------------
# 1️⃣ Tạo app context để truy cập database
# ---------------------------------------------------------
app = create_app(DevelopmentConfig) 
app.app_context().push()

print("🔹 Starting Sentiment Model Training...")

# ---------------------------------------------------------
# 2️⃣ Tải dữ liệu feedback từ database
# ---------------------------------------------------------
# (Code của bạn ở đây rất tốt, giữ nguyên)
feedbacks = Feedback.query.all()
if not feedbacks:
    print("⚠️ No feedback found in the database.")
    exit()

data = pd.DataFrame(
    [(f.id, f.product_id, f.comment, f.rating) for f in feedbacks],
    columns=["id", "product_id", "comment", "rating"]
)
print(f"📦 Loaded {len(data)} feedback entries from database.")

# ---------------------------------------------------------
# 3️⃣ Tiền xử lý và gán nhãn cảm xúc (positive / neutral / negative)
# ---------------------------------------------------------
# (Code của bạn ở đây rất tốt, giữ nguyên)
def map_sentiment(rating):
    if rating >= 4:
        return "POSITIVE"
    elif rating == 3:
        return "NEUTRAL"
    else:
        return "NEGATIVE"

data["sentiment"] = data["rating"].apply(map_sentiment)
print("📊 Sentiment distribution:", Counter(data["sentiment"]))

# Lọc bỏ comment rỗng
data = data.dropna(subset=['comment'])
data = data[data['comment'].str.strip() != '']

X = data["comment"]
y = data["sentiment"]

# ---------------------------------------------------------
# 4️⃣ Chia train/test có stratify (Code của bạn rất tốt)
# ---------------------------------------------------------
try:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
except ValueError:
    print("⚠️ Not enough samples per class for stratified split. Using random split.")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

print(f"🧩 Training samples: {len(X_train)}, Testing samples: {len(X_test)}")

# ---------------------------------------------------------
# 5️⃣ Tạo pipeline (Code của bạn rất tốt, 'class_weight' rất quan trọng)
# ---------------------------------------------------------
model = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english', max_features=5000, ngram_range=(1,2))),
    ('clf', LogisticRegression(max_iter=1000, class_weight='balanced'))
])

# ---------------------------------------------------------
# 6️⃣ Train và đánh giá mô hình
# ---------------------------------------------------------
print("\n🚀 Training TF-IDF + Logistic Regression model...")
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("\n--- Model Evaluation ---")
print(classification_report(y_test, y_pred, zero_division=0))

# ---------------------------------------------------------
# 7️⃣ Lưu mô hình vào instance/sentiment/
# ---------------------------------------------------------
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
model_dir = os.path.join(base_dir, "instance", "sentiment")
model_path = os.path.join(model_dir, "sentiment_model.pkl")

os.makedirs(model_dir, exist_ok=True)

with open(model_path, "wb") as f:
    pickle.dump(model, f)

print(f"\n✅ Model saved successfully to: {model_path}")
print("🎉 Sentiment Analysis training job completed successfully.\n")