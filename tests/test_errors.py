import os
import unittest

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("JWT_SECRET_KEY", "bookly-unit-test-secret-not-for-production")
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.errors import (
    BookNotFound,
    InvalidToken,
    TagAlreadyExists,
    register_error_handlers,
)


class ErrorTests(unittest.TestCase):
    def test_domain_errors_and_unknown_errors_are_safe(self):
        for error, status, code in [
            (BookNotFound(), 404, "book_not_found"),
            (InvalidToken(), 403, "invalid_token"),
            (TagAlreadyExists(), 409, "tag_exists"),
            (RuntimeError("secret-database-password"), 500, "server_error"),
        ]:
            app = FastAPI()
            register_error_handlers(app)

            @app.get("/")
            async def fail():
                raise error

            with TestClient(app, raise_server_exceptions=False) as client:
                response = client.get("/")
                self.assertEqual(response.status_code, status)
                self.assertEqual(response.json()["error_code"], code)
                self.assertNotIn("secret-database-password", response.text)
                if code == "invalid_token":
                    self.assertEqual(response.headers["www-authenticate"], "Bearer")
