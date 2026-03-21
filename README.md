# fastapi-blog

A simple blog REST API built with [FastAPI](https://fastapi.tiangolo.com/).

## Requirements

- Python 3.10+

## Installation

```bash
pip install -r requirements.txt
```

## Running the server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

Interactive API docs (Swagger UI): `http://localhost:8000/docs`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/posts` | List all posts |
| GET | `/posts/{id}` | Get a single post |
| POST | `/posts` | Create a new post |
| DELETE | `/posts/{id}` | Delete a post |

## Example

```bash
# Create a post
curl -X POST http://localhost:8000/posts \
  -H "Content-Type: application/json" \
  -d '{"title": "Hello", "content": "World", "author": "Alice"}'

# List posts
curl http://localhost:8000/posts
```
