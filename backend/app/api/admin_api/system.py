# import threading
# from flask import jsonify
# from . import admin_bp
# from .decorators import admin_required
#
# # Import các job function (đảm bảo path import đúng với project của bạn)
# from app.jobs.run_training import main as run_recom_training
# from app.jobs.run_sentiment_training import main as run_sent_training
#
# @admin_bp.route("/train/recommendation", methods=["POST"])
# @admin_required
# def trigger_recommendation_training():
#     try:
#         # Chạy thread riêng để không block request
#         thread = threading.Thread(target=run_recom_training)
#         thread.start()
#         return jsonify({"message": "Recommendation training started in background"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
# @admin_bp.route("/train/sentiment", methods=["POST"])
# @admin_required
# def trigger_sentiment_training():
#     try:
#         thread = threading.Thread(target=run_sent_training)
#         thread.start()
#         return jsonify({"message": "Sentiment training started in background"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500