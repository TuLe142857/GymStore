import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    PORT = os.environ.get('PORT', 5000)