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
from app.controllers.andon import initializeAndonRoutes

from app.utils.httpResponses import error_401, error_504
from app.config import REQUEST_TIMEOUT, SECRET_KEY
from flask_jwt_extended import JWTManager
from app.extensions import db, bcrypt, ma

app = Flask(__name__)

app.config['PROPAGATE_EXCEPTIONS'] = True
# Configurações do Banco e Segurança
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = SECRET_KEY

# Inicialização de Extensões
jwt = JWTManager(app)

# --- BLINDAGEM DO FLASK-RESTFUL ---
# Impede que erros prévios (Token Ausente/Vencido ou Rota Inválida) virem Erro 500
custom_errors = {
    'NoAuthorizationError': {
        'status': 401,
        'code': 401,
        'message': 'Missing Authorization Header'
    },
    'ExpiredSignatureError': {
        'status': 401,
        'code': 401,
        'message': 'The token has expired'
    },
    'InvalidHeaderError': {
        'status': 401,
        'code': 401,
        'message': 'Invalid token format or signature'
    },
    'RevokedTokenError': {
        'status': 401,
        'code': 401,
        'message': 'The token has been revoked'
    },
    'NotFound': {
        'status': 404,
        'code': 404,
        'message': 'A rota solicitada não existe nesta API.'
    }
}

# Inicializa a API injetando as regras estritas
api = Api(app, errors=custom_errors)

db.init_app(app)
bcrypt.init_app(app)
ma.init_app(app)
CORS(app)

# --- TRATAMENTO RFC 9110 PARA EXCEÇÕES DE JWT ---
@jwt.unauthorized_loader
def missing_token_callback(error_string):
    return error_401("Missing Authorization Header")

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return error_401("The token has expired")

@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    return error_401("Invalid token format or signature")

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return error_401("The token has been revoked")

# Criação das tabelas (incluindo os novos campos do Log)
with app.app_context():
    print("Creating database...")
    db.create_all()

app.config['SWAGGER'] = {
    'title': 'Ticket Management API',
    'uiversion': 3
}

# --- Lógica de Timeout ---
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

# --- INICIALIZAÇÃO DAS ROTAS ---
initializeRoutes(api)      # Tickets
initializeLogRoutes(api)   # Logs
initializeAuthRoutes(api)  # Auth
initializeAndonRoutes(api) # IA Andon

# Configuração do Swagger
template = build_swagger_template()
swagger = Swagger(app, template=template)

if __name__ == "__main__":
    print("Server running on http://127.0.0.1:5000")
    if not IS_WINDOWS:
        print(f"Timeout global: {REQUEST_TIMEOUT} segundos.")
    print("Documentação Swagger: http://127.0.0.1:5000/apidocs")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=False)