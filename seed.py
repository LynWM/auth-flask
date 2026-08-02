from faker import Faker

from config import app, db
from models import Note, User

fake = Faker()

USERS_TO_CREATE = 5
NOTES_PER_USER = 6


def seed():
    with app.app_context():
        print('Clearing existing data...')
        Note.query.delete()
        User.query.delete()

        print('Creating users...')
        users = []
        for _ in range(USERS_TO_CREATE):
            user = User(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
            )
            user.password_hash = 'password123'  # simple known password for testing
            users.append(user)
        db.session.add_all(users)
        db.session.commit()

        print('Creating notes...')
        notes = []
        for user in users:
            for _ in range(NOTES_PER_USER):
                notes.append(
                    Note(
                        title=fake.sentence(nb_words=4).rstrip('.'),
                        content=fake.paragraph(nb_sentences=3),
                        user_id=user.id,
                    )
                )
        db.session.add_all(notes)
        db.session.commit()

        print(f'Seeded {len(users)} users and {len(notes)} notes.')
        print('Sample login -> username:', users[0].username, '| password: password123')


if __name__ == '__main__':
    seed()
