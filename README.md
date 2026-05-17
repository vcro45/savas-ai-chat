# Savas AI Chat

A Django chat application with session-based conversation history, theme switching, and an external LLM backend adapter.

## Features

- Anonymous session tracking with UUID-backed users
- Multiple chat sessions per user
- Chat history persisted in SQLite during local development
- Theme switching through Django templates and static CSS
- Backend adapter for an LLM service endpoint

## Tech Stack

- Python
- Django
- SQLite
- HTML, CSS, JavaScript
- Requests

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/chat/`.

## Configuration

The app reads these environment variables:

- `DJANGO_SECRET_KEY`: Django secret key
- `DJANGO_DEBUG`: `true` or `false`
- `DJANGO_ALLOWED_HOSTS`: comma-separated host list
- `LLM_SERVER_ENDPOINT`: backend URL that accepts chat requests

The default LLM endpoint is local-only: `http://localhost:8080/wa/get-llm-response`.

## Notes

This repository is a cleaned portfolio version of an experimental chat interface. Local databases, virtual environments, generated files, and private deployment settings are intentionally excluded.


