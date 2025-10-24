import tabulate

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .api import api_bp
from .admin_routes import admin_bp
from .models import db
from .errors import init_error_handler

# jwt
jwt = JWTManager()

def print_debug(app, config_class=None):
    w = 100
    print("*"*w, "*" + "DEBUG".center(w-2) + "*", "*"*w, sep='\n')

    if config_class is not None:
        config_list = [
            {"key": key, "value": getattr(config_class, key)}
            for key in dir(config_class)
            if key.isupper()
        ]
        if config_list:
            table = tabulate.tabulate(config_list, headers="keys", tablefmt="pretty", stralign='left')
            w = len(table.split("\n")[0])
            print("=" * w, "CONFIG LIST".center(w), sep="\n")
            print(table)
    else:
        print("Config class not defined")

    with app.app_context():

        api_list = [
            {
                "endpoint":rule.endpoint,
                "rule":rule.rule,
                "method":rule.methods
             }
            for rule in app.url_map.iter_rules()]
        table = tabulate.tabulate(api_list, headers="keys", tablefmt="pretty", stralign='left')
        w = len(table.split("\n")[0])
        print("=" * w,"API LIST".center(w), sep="\n")
        print(table)

def create_app(config_class=None):
    app = Flask(__name__)

    # config
    if config_class is not None:
        app.config.from_object(config_class)
    CORS(app)

    db.init_app(app)
    jwt.init_app(app)
    init_error_handler(app)

    # create db if not exist
    with app.app_context():
        db.create_all()

    # api route
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    @app.route('/')
    def index():
        return "Hello World!"

    print_debug(app, config_class)
    return app
