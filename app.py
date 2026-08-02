from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import api, app, db
from models import Note, User


def current_user():
    # Return the User row for the identity embedded in the JWT.

    user_id = get_jwt_identity()
    return User.query.get(int(user_id))

# Auth routes
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


# Note (resource) routes
class Notes(Resource):
    @jwt_required()
    def get(self):
        user = current_user()

        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
        except ValueError:
            return {'error': 'page and per_page must be integers'}, 400

        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)  # cap page size

        pagination = Note.query.filter_by(user_id=user.id) \
            .order_by(Note.created_at.desc()) \
            .paginate(page=page, per_page=per_page, error_out=False)

        return {
            'notes': [note.to_dict() for note in pagination.items],
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'total_pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        }, 200

    @jwt_required()
    def post(self):
        user = current_user()
        data = request.get_json() or {}

        try:
            note = Note(
                title=data.get('title'),
                content=data.get('content'),
                user_id=user.id,
            )
            db.session.add(note)
            db.session.commit()
        except ValueError as e:
            db.session.rollback()
            return {'error': str(e)}, 422

        return note.to_dict(), 201


class NoteByID(Resource):
    def _get_owned_note_or_none(self, id):
        user = current_user()
        return Note.query.filter_by(id=id, user_id=user.id).first()

    @jwt_required()
    def get(self, id):
        note = self._get_owned_note_or_none(id)
        if not note:
            return {'error': 'Note not found'}, 404
        return note.to_dict(), 200

    @jwt_required()
    def patch(self, id):
        note = self._get_owned_note_or_none(id)
        if not note:
            return {'error': 'Note not found'}, 404

        data = request.get_json() or {}
        try:
            for attr in ('title', 'content'):
                if attr in data:
                    setattr(note, attr, data[attr])
            db.session.commit()
        except ValueError as e:
            db.session.rollback()
            return {'error': str(e)}, 422

        return note.to_dict(), 200

    @jwt_required()
    def delete(self, id):
        note = self._get_owned_note_or_none(id)
        if not note:
            return {'error': 'Note not found'}, 404

        db.session.delete(note)
        db.session.commit()
        return {}, 204


# Route registration
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Logout, '/logout')
api.add_resource(Notes, '/notes')
api.add_resource(NoteByID, '/notes/<int:id>')


# Error handlers (make sure JWT errors come back as clean JSON, not HTML)
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


if __name__ == '__main__':
    app.run(port=5555, debug=True, use_reloader=False)
