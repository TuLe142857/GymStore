import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    PORT = os.environ.get('PORT', 5000)

    # database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # jwt
    JWT_SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1h
    JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000))  # 30d

    # image uploads (from local) directory
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')

    # Flask-Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))

    MAIL_USE_TLS = bool(int(os.environ.get('MAIL_USE_TLS', True)))
    MAIL_USE_SSL = bool(int(os.environ.get('MAIL_USE_SSL', False)))

    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

class DevelopmentConfig(Config):
    DEBUG = True
    # Các cài đặt khác cho môi trường dev nếu cần
    
class ProductionConfig(Config):
    DEBUG = False
    # Các cài đặt khác cho môi trường production nếu cần
    
config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig
}