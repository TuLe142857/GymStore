import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    PORT = os.environ.get('PORT', 5000)

    # database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # jwt
    JWT_SECRET_KEY = os.environ.get('SECRET_KEY')

    # image uploads (from local) directory
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')