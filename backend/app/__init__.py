from flask import Flask
from flask_cors import CORS

from .api import api_bp
from .admin_routes import admin_bp
from .extensions import db, jwt
from .errors import init_error_handler
from .commands import register_commands

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)

    db.init_app(app)

    jwt.init_app(app)

    init_error_handler(app)

    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    register_commands(app)

    # create db if not exist
    with app.app_context():
        db.create_all()

    return app
