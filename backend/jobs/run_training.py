import sys
import os

# Thêm thư mục /app vào Python path để có thể import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import DevelopmentConfig

from app import create_app, db
from app.services.recommendation_service import build_similarity_matrix
from app.services.recommendation_service import build_collaborative_model

def run_job():
    print("Starting recommendation model training job...")
    
    # Tạo app context để có thể truy cập database
    app = create_app(DevelopmentConfig)
    with app.app_context():
        try:
            print("\n--- Building Content-Based Model ---")
            build_similarity_matrix()
            
            print("\n--- Building Collaborative-Filtering Model ---")
            build_collaborative_model()
            
            print("Training jobs completed successfully.")  
        except Exception as e:
            print(f"An error occurred during the training job: {e}")
            sys.exit(1)

if __name__ == "__main__":
    run_job()