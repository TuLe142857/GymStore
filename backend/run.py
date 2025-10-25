import app
from config import Config

def create_app():
    return app.create_app(Config)

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=int(app.config.get('PORT', 5000)))