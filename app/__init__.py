from flask import Flask
from flask_cors import CORS

# Função para criar a aplicação Flask
def create_app():
    app = Flask(__name__)

    CORS(app)

    from app.views import bp as main_bp
    app.register_blueprint(main_bp)

    return app 
