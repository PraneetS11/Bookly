# Bookly API

A PostgreSQL-backed book catalog with creators, book reviews and shared tags. Verified users and admins can manage books; only a review's author can delete it. Authentication includes hashed passwords, JWT access/refresh, per-token Redis logout, inactive-account checks, email verification and password recovery.

## Run locally

Use Python 3.12 and install `requirements.txt` in `.venv`. Copy `.env.example` to ignored `.env`, configure PostgreSQL/Redis and a random JWT secret, then apply `.venv/bin/alembic upgrade head`.

```sh
docker compose -p bookly-mail -f compose.mail.yaml up -d
.venv/bin/celery -A src.tasks:celery_app worker --pool=solo --concurrency=1 --loglevel=INFO
# In another terminal:
.venv/bin/uvicorn src:app --host 127.0.0.1 --port 8000
```

Swagger: http://127.0.0.1:8000/docs; schema: `/openapi.json`; reference: `/redoc`. Sandbox inbox: http://127.0.0.1:8026. Signup, verify using the sandbox link, then login and use the bearer access token in Swagger's Authorize control. Local admin promotion: `.venv/bin/python -m scripts.promote_admin EMAIL`.

Run `.venv/bin/python -m unittest discover -s tests -q`. Stop foreground workers with Ctrl-C; stop the catcher with `docker compose -p bookly-mail -f compose.mail.yaml stop`.

## Limits

Mail is queued and sent only to the local sandbox; API acceptance is not confirmed delivery. Recovery links expire but remain reusable until expiry and do not invalidate existing sessions. Refresh rotation, production delivery guarantees, public HTTPS hosting and a production security review are not implemented. Use fictional data. Development CORS/host settings are explicit in `.env.example`.
