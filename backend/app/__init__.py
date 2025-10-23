from flask import Flask
from flask_cors import CORS

def create_app(config_class=None):
    app = Flask(__name__)

    # config
    if config_class is not None:
        app.config.from_object(config_class)

    # CORS allow all
    # CORS(app)

    @app.route('/')
    def index():
        return "Hello World!"

    return app
