from flask import jsonify

from config import api, app
from resources.auth import CheckSession, Login, Logout, Signup
from resources.notes import NoteByID, Notes

# Route registration
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Logout, '/logout')
api.add_resource(Notes, '/notes')
api.add_resource(NoteByID, '/notes/<int:id>')


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


if __name__ == '__main__':
    app.run(port=5555, debug=True, use_reloader=False)