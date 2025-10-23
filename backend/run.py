from app import create_app
from config import Config

if __name__ == '__main__':
    app = create_app(Config)

    print("hello world")
    app.run(debug=True, host='0.0.0.0', port=int(app.config.get('PORT', 5000)))