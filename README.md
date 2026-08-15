# Job Application Tracker API

A small REST API built with FastAPI to track job applications, with JWT-based authentication. Built as a focused 2-day exercise to get hands-on with REST API fundamentals - not a production app.

## Tech stack

- **FastAPI** - web framework
- **PostgreSQL** - database
- **SQLAlchemy** - ORM
- **Pydantic** - request/response validation
- **Passlib (bcrypt)** - password hashing
- **python-jose** - JWT encoding/decoding

## Features

- User registration with bcrypt-hashed passwords
- JWT-based login (`OAuth2PasswordRequestForm` + bearer tokens)
- All user and application routes scoped to the authenticated user via token - no client-supplied user IDs
- Full CRUD for:
  - **Users** — profile view, update, delete
  - **Job Applications** - create, list, update status, delete (each application belongs to the authenticated user)

## Project structure

```
.
├── main.py              # App entrypoint, router registration
├── models.py             # SQLAlchemy models (User, Application)
├── database.py            # Engine, session, Base
└── routers/
    ├── auth.py            # Signup, login, JWT creation, get_current_user dependency
    ├── user.py            # /user routes
    └── application.py       # /job_application routes
```

## Setup

1. Create a PostgreSQL database and update the connection string in `database.py`.
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

## Auth flow

1. `POST /auth/` - create an account (email, password, full name, age)
2. `POST /auth/token` - log in with email/password, receive a JWT
3. Click **Authorize** in `/docs` and paste the token — all protected routes will use it automatically
4. Every `/user` and `/job_application` route identifies the caller from the token, not from a URL parameter

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/auth/` | Create a new user |
| POST | `/auth/token` | Log in, get a JWT |
| GET | `/user/` | Get your own profile |
| PUT | `/user/` | Update your profile |
| DELETE | `/user/` | Delete your account |
| GET | `/job_application/` | List your job applications |
| POST | `/job_application/` | Add a new application |
| PUT | `/job_application/{application_id}` | Update an application's status/details |
| DELETE | `/job_application/{application_id}` | Delete an application |

## Notes / known limitations

- No Alembic migrations — schema changes during development were handled by dropping and recreating tables, since there was no data worth preserving. Alembic would be the right call for a project with real, persistent data.
- No automated tests yet (pytest) - manual testing via `/docs` only.
- No password reset, email verification, or role-based permissions - out of scope for this exercise.