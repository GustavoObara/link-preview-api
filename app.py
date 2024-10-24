from flask import Flask
from flask_cors import CORS
from app.views import bp as main_bp

# Função para criar a aplicação Flask e configurar as rotas
def create_app():
    app = Flask(__name__)  
    CORS(app)  # Configura o CORS para permitir acessos de diferentes origens
    app.register_blueprint(main_bp) 
    return app

# Executa a aplicação Flask com o modo de debug ativado
if __name__ == '__main__':
    app = create_app()  
    app.run(host='0.0.0.0', port=5000, debug=True)
    