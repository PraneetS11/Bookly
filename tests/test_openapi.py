import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("JWT_SECRET_KEY", "bookly-unit-test-secret-not-for-production")
import unittest

from src import app


class OpenAPITests(unittest.TestCase):
    def test_contract_has_examples_auth_and_actual_routes(self):
        schema = app.openapi()
        self.assertTrue(schema["info"]["description"])
        self.assertTrue(schema["tags"])
        self.assertTrue(schema["components"]["schemas"]["BookCreateModel"]["examples"])
        operation = schema["paths"]["/api/v1/books/"]["post"]
        self.assertTrue(operation["security"])
        self.assertIn("403", operation["responses"])
        self.assertIn("404", operation["responses"])
        self.assertIn("201", operation["responses"])
        self.assertFalse(any("practice" in path for path in schema["paths"]))
