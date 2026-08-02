# Notes API — JWT-Authenticated Flask Backend

A Flask REST API for a personal notes / productivity app. Users register
and log in with a hashed password, receive a JWT, and use it to create, read,
update, and delete their own notes. Users can never see or modify another
user's notes.

## Project Description

The resource being tracked is **Notes** (a `title` + `content` journal-style
entry), but the same patterns (ownership checks, pagination, CRUD) would apply
to any user-owned resource such as workouts or expenses.

Each `Note` belongs to exactly one `User` via a `user_id` foreign key. Every
resource route requires a valid JWT and filters/validates against the
currently authenticated user, so:

- A user can only ever see their **own** notes in `GET /notes`.
- A user cannot `GET`, `PATCH`, or `DELETE` a note that belongs to someone
  else — the API returns `404 Not Found` rather than leaking that the note
  exists.

## Installation

**Requirements:** Python 3.8.13+ and `pipenv`.

```bash
git clone <your-repo-url>
cd notes-api-jwt
pipenv install
pipenv shell
```

Set up the database:

```bash
export FLASK_APP=app.py
flask db upgrade
python seed.py
```

## Running the Server

```bash
flask run
```

## Authentication Flow

All protected routes require the header:

```
Authorization: Bearer <access_token>
```

The token is returned by `/signup` and `/login`.

## API Endpoints

### Auth

| Method | Route             | Auth required | Description |
|--------|-------------------|:---:|-------------|
| POST   | `/signup`         | No | Create a new user. Body: `{ "username", "email", "password" }`. Returns the created user + an access token. |
| POST   | `/login`          | No | Authenticate with `{ "username", "password" }`. Returns the user + an access token. |
| GET    | `/check_session`  | Yes | Returns the currently authenticated user, based on the token. Used by the frontend to restore a session on page refresh. |
| DELETE | `/logout`         | Yes | Confirms the token was valid. (JWTs are stateless — the frontend discards the token client-side to "log out".) |

### Notes (resource)

| Method | Route            | Auth required | Description |
|--------|------------------|:---:|-------------|
| GET    | `/notes`         | Yes | Paginated list of the **current user's** notes. Query params: `page` (default 1), `per_page` (default 10, max 100). |
| POST   | `/notes`         | Yes | Create a note owned by the current user. Body: `{ "title", "content" }`. |
| GET    | `/notes/<id>`    | Yes | Get a single note by id — only if it belongs to the current user, else `404`. |
| PATCH  | `/notes/<id>`    | Yes | Update `title` and/or `content` on a note the current user owns, else `404`. |
| DELETE | `/notes/<id>`    | Yes | Delete a note the current user owns, else `404`. |

**Example — `GET /notes?page=1&per_page=5` response:**

```json
{
  "notes": [
    { "id": 12, "title": "Groceries", "content": "Milk, eggs, bread",
      "user_id": 3, "created_at": "...", "updated_at": "..." }
  ],
  "page": 1,
  "per_page": 5,
  "total": 18,
  "total_pages": 4,
  "has_next": true,
  "has_prev": false
}
```