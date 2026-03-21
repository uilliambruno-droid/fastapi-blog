# FastAPI Blog API

Asynchronous REST API built with FastAPI for JWT authentication, user management, and post CRUD with owner-based authorization.

## Key Features

- JWT login (`/auth/token`)
- Public routes for reading posts
- Protected routes for creating/updating/deleting posts
- Owner-based authorization rules for posts (or `admin` override)
- Optional admin user seeding via configuration
- Unit + integration tests with high coverage

## Architecture

Layered structure:

- `src/controllers`: HTTP endpoints and dependency composition
- `src/services`: business rules
- `src/models`: SQLAlchemy table definitions
- `src/schemas`: input contracts (Pydantic)
- `src/views`: output contracts
- `src/dependencies`: reusable authentication/authorization dependencies
- `src/utils`: utilities (JWT and password helpers)
- `src/config.py`: environment-based settings

## Requirements

- Python `>=3.14`
- Poetry `>=2.x`

## Environment Configuration

Settings are read from environment variables (with `.env` file support).

### Available Variables

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | Environment (`development`, `test`, `production`) |
| `DATABASE_URL` | `sqlite:///./blog.db` | Database connection string |
| `JWT_SECRET_KEY` | `change-me-in-production` | JWT secret key (must be secure in production) |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token expiration time |
| `SEED_ADMIN_ENABLED` | `true` | Enables automatic admin creation |
| `SEED_ADMIN_USERNAME` | `admin` | Initial admin username |
| `SEED_ADMIN_PASSWORD` | `admin` | Initial admin password |

> In `APP_ENV=production`, application startup fails if `JWT_SECRET_KEY` is insecure.

## Running Locally

1. Install dependencies:

```zsh
poetry lock
poetry install --no-root
```

2. (Optional) Define variables in `.env`.

3. Run the API:

```zsh
poetry run uvicorn src.main:app --reload
```

4. Open interactive API docs:

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Quick cURL Flow

### 1) Login

```zsh
curl -s -X POST 'http://127.0.0.1:8000/auth/token' \
	-H 'Content-Type: application/json' \
	-d '{"username":"admin","password":"admin"}'
```

### 2) Create post (protected route)

```zsh
curl -s -X POST 'http://127.0.0.1:8000/posts/' \
	-H 'Authorization: Bearer <TOKEN>' \
	-H 'Content-Type: application/json' \
	-d '{"title":"My post","content":"Content","published":true}'
```

### 3) List posts (public route)

```zsh
curl -s 'http://127.0.0.1:8000/posts/?published=true&skip=0&limit=10'
```

## Authorization Rules

- `POST /posts/`: requires an authenticated user.
- `PATCH /posts/{id}` e `DELETE /posts/{id}`:
	- allowed for the post owner;
	- allowed for `admin`;
	- all other users receive `403`.

## Tests

Run tests:

```zsh
poetry run pytest -q
```

Run with coverage:

```zsh
poetry run pytest --cov=src --cov-report=term-missing -q
```

## Recommended Next Steps

- Add Alembic migrations for production schema evolution
- Add observability (structured logs and tracing)
- Implement refresh tokens and JWT secret rotation
