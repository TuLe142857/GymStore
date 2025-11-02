from flask import Flask
from flask_cors import CORS

from .api import api_bp
from .api import admin_bp
from .extensions import db, jwt, mail, redis_client
from .errors import init_error_handler
from .commands import register_commands
from .api.setiment_routes import sentiment_bp

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    redis_client.init_app(app)

    init_error_handler(app)

    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(sentiment_bp)

    register_commands(app)
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    # create db if not exist
    with app.app_context():
        db.create_all()

    return app
