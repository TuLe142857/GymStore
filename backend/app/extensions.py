from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_redis import FlaskRedis

db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
redis_client = FlaskRedis()
