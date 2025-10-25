import os
from flask import Blueprint, send_from_directory, abort, current_app
from werkzeug.exceptions import NotFound
upload_bp = Blueprint("upload", __name__)

@upload_bp.route("/uploads/<path:filename>", methods=["GET"])
def get_uploaded_file(filename):
    if "UPLOAD_FOLDER" not in current_app.config or not current_app.config["UPLOAD_FOLDER"]:
        raise Exception("UPLOAD_FOLDER must be set in app.config[UPLOAD_FOLDER]")

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)
    if not os.path.exists(file_path):
        raise NotFound("File not found")

    return send_from_directory(upload_folder, filename)
