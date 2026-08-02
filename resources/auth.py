from flask import request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import db
from models import User


def current_user():

    user_id = get_jwt_identity()
    return User.query.get(int(user_id))


class Signup(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return {'error': 'username, email, and password are required'}, 422

        try:
            user = User(username=username, email=email)
            user.password_hash = password
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Username or email already taken'}, 422
        except ValueError as e:
            db.session.rollback()
            return {'error': str(e)}, 422

        access_token = create_access_token(identity=str(user.id))
        return {'user': user.to_dict(), 'access_token': access_token}, 201


class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if not user or not user.authenticate(password or ''):
            return {'error': 'Invalid username or password'}, 401

        access_token = create_access_token(identity=str(user.id))
        return {'user': user.to_dict(), 'access_token': access_token}, 200


class CheckSession(Resource):

    @jwt_required()
    def get(self):
        user = current_user()
        if not user:
            return {'error': 'User not found'}, 404
        return user.to_dict(), 200


class Logout(Resource):
    
    @jwt_required()
    def delete(self):
        return {}, 204