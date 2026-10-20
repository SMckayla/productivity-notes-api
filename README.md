# Productivity Notes API

A session-based Flask API for a personal workout log. Each account owns its own workouts. Authentication uses an HTTP-only session cookie, and passwords are stored only as bcrypt hashes.

The frontend can keep its existing signup, login, logout, and session-check flow. Workout screens can be built against the resource routes below.

## Installation

Python 3.12 and Pipenv are required.

```bash
pipenv install
pipenv shell
export FLASK_APP=server/app.py
flask db upgrade
python seed.py
```

`flask db upgrade` creates the SQLite database at `instance/app.db`. `python seed.py` loads starter users and workouts. It is safe to run again; it replaces existing seed data.

Without activating the shell:

```bash
pipenv run flask --app server/app.py db upgrade
pipenv run python seed.py
```

Set `SECRET_KEY` in the environment before running the app anywhere other than your machine. The development fallback is only for local use.

## Run

From the project root, with the Pipenv shell active:

```bash
flask run --port 5555
```

Or:

```bash
pipenv run flask --app server/app.py run --port 5555
```

The API listens on `http://127.0.0.1:5555`.

### Try the demo account

The seed file creates a known user:

- Username: `alex`
- Password: `password123`

Other seeded users use the same password.

### Connect a frontend

Session cookies are stored by the browser. The reliable local setup is a dev-server proxy to `http://127.0.0.1:5555`, so the browser treats the API as the same origin. Requests to auth and workout routes should send cookies (`credentials: "include"` if the client calls the API directly).

The API also allows credentialed requests from `http://localhost:3000`, `http://127.0.0.1:3000`, `http://localhost:4000`, and `http://127.0.0.1:4000`.

## Endpoints

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| POST | `/signup` | No | Create a user, hash the password, and start a session. Returns the user with status 201. Duplicate or missing fields return 422. |
| POST | `/login` | No | Check the username and password. On success, start a session and return the user with status 200. Invalid credentials return 401. |
| DELETE | `/logout` | Yes | End the current session. Returns 204. Returns 401 when nobody is logged in. |
| GET | `/check_session` | Yes | Return the user for the current session cookie. Returns 200, or 401 when the cookie is missing or stale. Use this to stay logged in across a refresh. |
| GET | `/workouts` | Yes | List the logged-in user's workouts, newest first. Supports `page` and `per_page` (default 5, maximum 20). Returns 401 when logged out. |
| POST | `/workouts` | Yes | Create a workout owned by the logged-in user. Returns 201, or 422 when the body is invalid. A client-supplied `user_id` is ignored. |
| GET | `/workouts/<id>` | Yes | Return one workout. Returns 404 if it does not exist, 403 if it belongs to someone else, and 401 if logged out. |
| PATCH | `/workouts/<id>` | Yes | Update any of `name`, `duration`, `notes`, and `performed_on`. Returns 200. Ownership rules match the show route. |
| DELETE | `/workouts/<id>` | Yes | Delete one of the logged-in user's workouts. Returns 204. Ownership rules match the show route. |

### Workout body

```json
{
  "name": "Easy Run",
  "duration": 30,
  "notes": "Felt good",
  "performed_on": "2026-10-20"
}
```

`duration` is minutes, from 1 to 1440. `notes` is optional. `performed_on` defaults to today when omitted. Dates use `YYYY-MM-DD`.

### Paginated list

`GET /workouts?page=1&per_page=5`

```json
{
  "workouts": [],
  "page": 1,
  "per_page": 5,
  "total": 0,
  "pages": 0
}
```

The list never includes another user's workouts.

### User body

Signup, login, and check-session return:

```json
{
  "id": 1,
  "username": "alex"
}
```

The password hash is never included.

## Tests

```bash
pipenv run pytest
```

## Project layout

- `server/app.py` starts the application
- `server/config.py` builds the Flask app, database, bcrypt, and CORS rules
- `server/models.py` defines `User` and `Workout`
- `server/schemas.py` serializes JSON with Marshmallow
- `server/routes/` holds auth and workout resources
- `seed.py` loads example users and workouts
- `migrations/` holds the database schema
- `tests/` covers auth, ownership, CRUD, pagination, and seeding
