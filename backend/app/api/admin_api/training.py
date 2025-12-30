import threading
from flask import jsonify, Blueprint
from . import admin_bp
from .decorators import admin_required
import time
training_bp = Blueprint('training', __name__, url_prefix='/training')
admin_bp.register_blueprint(training_bp)

TRAINING_STATUS = {
    "search":
        {
            "status": "idle", # or "running" or "failed" or "success"
            "last_run": None, # or timestamp
            "message": ""
        },
    "recommendation":
        {
            "status": "idle",
            "last_run": None,
            "message": ""
        },
    "sentiment":
        {
            "status": "idle",
            "last_run": None,
            "message": ""
        }
}


def run_task_in_background(task_type, task_func):
    """
    :param task_type: string -recommendation/search/sentiment
    :param task_func: function callable - training task
    """
    def wrapper():
        TRAINING_STATUS[task_type]["status"] = "running"
        TRAINING_STATUS[task_type]["message"] = "Training in progress..."
        try:
            # Gọi hàm train thực tế
            task_func()

            TRAINING_STATUS[task_type]["status"] = "success"
            TRAINING_STATUS[task_type]["message"] = "Training completed successfully."
            TRAINING_STATUS[task_type]["last_run"] = time.time()
        except Exception as e:
            print(f"Error training {task_type}: {e}")
            TRAINING_STATUS[task_type]["status"] = "failed"
            TRAINING_STATUS[task_type]["message"] = str(e)

    thread = threading.Thread(target=wrapper)
    thread.start()

def train_recommendation():
    time.sleep(5)


def train_search():
    time.sleep(5)

def train_sentiment():
    time.sleep(5)



@training_bp.route('/status', methods=['GET'])
@admin_required
def get_status():
    return jsonify(TRAINING_STATUS)

@training_bp.route('/recommendation', methods=['POST'])
@admin_required
def api_train_recommendation():
    if TRAINING_STATUS["recommendation"]["status"] == "running":
        return jsonify({"error": "Job is already running"}), 400
    run_task_in_background("recommendation", train_recommendation)
    return jsonify(TRAINING_STATUS)

@training_bp.route('/search', methods=['POST'])
# @admin_required
def api_train_search():
    if TRAINING_STATUS["search"]["status"] == "running":
        return jsonify({"error": "Job is already running"}), 400
    run_task_in_background("search", train_search)
    return jsonify(TRAINING_STATUS)

@training_bp.route('/sentiment', methods=['POST'])
@admin_required
def api_train_sentiment():
    if TRAINING_STATUS["sentiment"]["status"] == "running":
        return jsonify({"error": "Job is already running"}), 400
    run_task_in_background("sentiment", train_sentiment)
    return jsonify(TRAINING_STATUS)