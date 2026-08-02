from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates

from config import bcrypt, db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column('password_hash', db.String, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    notes = db.relationship(
        'Note', backref='user', cascade='all, delete-orphan', lazy=True
    )

    # password handling
    @hybrid_property
    def password_hash(self):
        raise AttributeError('password_hash is not a readable attribute')

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

    # basic validation
    @validates('username')
    def validate_username(self, key, username):
        if not username or not username.strip():
            raise ValueError('Username must not be empty')
        return username.strip()

    @validates('email')
    def validate_email(self, key, email):
        if not email or '@' not in email:
            raise ValueError('A valid email is required')
        return email.strip().lower()

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<User {self.id}: {self.username}>'


class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    @validates('title')
    def validate_title(self, key, title):
        if not title or not title.strip():
            raise ValueError('Title must not be empty')
        return title.strip()

    @validates('content')
    def validate_content(self, key, content):
        if not content or not content.strip():
            raise ValueError('Content must not be empty')
        return content.strip()

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Note {self.id}: {self.title}>'
