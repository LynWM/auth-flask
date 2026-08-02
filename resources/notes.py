from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from config import db
from models import Note
from resources.auth import current_user


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