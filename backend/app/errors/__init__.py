from .app_errors import *
from ..extensions import db
from flask import jsonify
from werkzeug.exceptions import MethodNotAllowed, NotFound

def init_error_handler(app):

    @app.errorhandler(BaseAppError)
    def base_app_error_handler(e):
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code

    @app.errorhandler(NotFound)
    def handle_not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(MethodNotAllowed)
    def handle_method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    # place this at the end
    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        app.logger.error(f"Unhandled exception: {str(e)}", exc_info=True)

        db.session.rollback()
        return jsonify({
            "error": "Unknown error",
        }), 500