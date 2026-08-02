import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URI', f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-dev-key-change-me')

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

# Extension
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


API_ERRORS = {
    'NoAuthorizationError': {
        'message': 'Missing or invalid Authorization header',
        'status': 401,
    },
    'InvalidHeaderError': {
        'message': 'Invalid Authorization header',
        'status': 422,
    },
    'DecodeError': {
        'message': 'Invalid or malformed token',
        'status': 422,
    },
    'ExpiredSignatureError': {
        'message': 'Token has expired',
        'status': 401,
    },
    'InvalidSignatureError': {
        'message': 'Invalid token signature',
        'status': 422,
    },
    'WrongTokenError': {
        'message': 'Wrong token type',
        'status': 422,
    },
    'RevokedTokenError': {
        'message': 'Token has been revoked',
        'status': 401,
    },
}

api = Api(app, errors=API_ERRORS)

CORS(app, supports_credentials=True)