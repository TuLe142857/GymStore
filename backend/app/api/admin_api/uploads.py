import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from .decorators import admin_required
from . import admin_bp

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_upload_folder():
    return current_app.config.get('UPLOAD_FOLDER', 'app/uploads')


def get_image_stored_directory():
    IMAGE_FOLDER = "product_images"
    directory = os.path.join(get_upload_folder(), IMAGE_FOLDER)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

@admin_bp.route('/image', methods=['POST'])
@admin_required
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        # 1. Tạo tên file ngẫu nhiên (UUID) để tránh trùng lặp
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        new_filename = f"{uuid.uuid4().hex}.{extension}"

        # 2. Lưu file vào ổ cứng
        save_directory = get_image_stored_directory()
        file_path = os.path.join(save_directory, new_filename)

        try:
            file.save(file_path)
        except Exception as e:
            return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

        # 3. Tạo URL trả về (Theo đúng format bạn yêu cầu)
        # Format: http://localhost:5000/api/uploads/product_images/<filename>

        # Lấy domain hiện tại (ví dụ http://localhost:5000)
        base_url = request.host_url.rstrip('/')

        # Ghép chuỗi URL
        file_url = f"{base_url}/api/uploads/product_images/{new_filename}"

        return jsonify({
            'message': 'Upload successful',
            'url': file_url
        }), 201

    return jsonify({'error': 'File type not allowed'}), 400



@admin_bp.route('/image', methods=['DELETE'])
@admin_required
def delete_image():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing image URL'}), 400

    file_url = data['url']

    # URL mẫu: http://localhost:5000/api/uploads/product_images/rule1-protein.jpg

    try:
        # 1. Trích xuất tên file từ URL (Lấy phần cuối cùng sau dấu /)
        filename = file_url.split('/')[-1]
        filename = secure_filename(filename)

        # 2. Xác định vị trí file trên ổ cứng
        store_directory = get_image_stored_directory()
        file_path = os.path.join(store_directory, filename)

        # 3. Thực hiện xóa
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'message': 'Image deleted successfully'}), 200
        else:
            # File không tồn tại (có thể đã bị xóa trước đó), vẫn trả về success hoặc 404 tùy logic
            return jsonify({'error': 'File not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500