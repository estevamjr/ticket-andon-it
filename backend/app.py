from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flasgger import Swagger
from app.swagger import build_swagger_template
import signal
import os

# Imports de Controllers
from app.controllers.ticket import initializeRoutes
from app.controllers.log import initializeLogRoutes
from app.controllers.auth import initializeAuthRoutes
# --- NOVO IMPORT DO CONTROLLER DE IA (ANDON) ---
from app.controllers.andon import initializeAndonRoutes

from app.utils.httpResponses import error_504
from app.config import REQUEST_TIMEOUT, SECRET_KEY
from flask_jwt_extended import JWTManager
from app.extensions import db, bcrypt, ma

app = Flask(__name__)

# Configurações do Banco e Segurança
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = SECRET_KEY

# Inicialização de Extensões
jwt = JWTManager(app)
api = Api(app)
db.init_app(app)
bcrypt.init_app(app)
ma.init_app(app)
CORS(app)

# Criação das tabelas (incluindo os novos campos do Log)
with app.app_context():
    print("Creating database...")
    db.create_all()

app.config['SWAGGER'] = {
    'title': 'Ticket Management API',
    'uiversion': 3
}

# --- Lógica de Timeout (Mantida conforme seu original) ---
IS_WINDOWS = os.name == 'nt'

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError(f"Request timed out after {REQUEST_TIMEOUT} seconds.")

if not IS_WINDOWS:
    @app.before_request
    def start_request_timeout():
        from flask import request
        if request.path.startswith(('/apidocs', '/api/auth')):
            return
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(REQUEST_TIMEOUT)
        except AttributeError:
            pass

    @app.after_request
    def clear_request_timeout(response):
        try:
            signal.alarm(0)
        except AttributeError:
            pass
        return response

    @app.errorhandler(TimeoutError)
    def handle_timeout_error(e):
        return error_504(str(e))
else:
    print("Warning: Request timeout feature is disabled on Windows platforms.")

# --- INICIALIZAÇÃO DAS ROTAS (PADRÃO DO PROJETO) ---
initializeRoutes(api)      # Tickets
initializeLogRoutes(api)   # Logs
initializeAuthRoutes(api)  # Auth
initializeAndonRoutes(api) # IA Andon (Novo)

# Configuração do Swagger
template = build_swagger_template()
swagger = Swagger(app, template=template)

if __name__ == "__main__":
    print(f"Server running on http://127.0.0.1:5000")
    if not IS_WINDOWS:
        print(f"Timeout global: {REQUEST_TIMEOUT} segundos.")
    print("Documentação Swagger: http://127.0.0.1:5000/apidocs")
    app.run(debug=True)