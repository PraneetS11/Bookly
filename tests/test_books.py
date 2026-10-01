import os
import unittest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

# Unit tests do not connect to this URL or require the developer's .env.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("JWT_SECRET_KEY", "bookly-unit-test-secret-not-for-production")

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.books.models import Book
from src.books.routes import access_token_bearer, book_router
from src.books.schemas import BookCreateModel, BookUpdateModel
from src.books.service import BookService
from src.db.main import get_session

VALUES = {
    "title": "Test book",
    "author": "Test author",
    "publisher": "Test publisher",
    "published_date": "2024-01-01",
    "page_count": 100,
    "language": "English",
}


class BookRoutesTests(unittest.TestCase):
    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.session.exec.return_value = MagicMock()
        self.app = FastAPI()
        self.app.include_router(book_router, prefix="/api/v1/books")
        self.app.dependency_overrides[access_token_bearer] = lambda: {}
        self.app.dependency_overrides[get_current_user] = lambda: User(
            is_verified=True, role="user"
        )

        async def override():
            yield self.session

        self.app.dependency_overrides[get_session] = override
        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)

    def test_create_validates_date_and_returns_generated_fields(self):
        response = self.client.post("/api/v1/books/", json=VALUES)
        self.assertEqual(response.status_code, 201, response.text)
        self.assertIn("uid", response.json())
        self.assertIn("updated_at", response.json())
        self.assertEqual(response.json()["published_date"], "2024-01-01")
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once()
        invalid = dict(VALUES, published_date="not-a-date")
        self.assertEqual(
            self.client.post("/api/v1/books/", json=invalid).status_code, 422
        )
        self.assertEqual(self.client.post("/api/v1/books/", json={}).status_code, 422)

    def test_missing_and_malformed_ids(self):
        self.session.exec.return_value.first.return_value = None
        update = {k: v for k, v in VALUES.items() if k != "published_date"}
        for method, body in (("get", None), ("patch", update), ("delete", None)):
            kwargs = {} if body is None else {"json": body}
            self.assertEqual(
                self.client.request(
                    method, f"/api/v1/books/{uuid4()}", **kwargs
                ).status_code,
                404,
            )
            self.assertEqual(
                self.client.request(
                    method, "/api/v1/books/bad-id", **kwargs
                ).status_code,
                422,
            )

    def test_delete_has_no_response_body(self):
        self.session.exec.return_value.first.return_value = Book()
        response = self.client.delete(f"/api/v1/books/{uuid4()}")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")


class BookServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_all_failed_writes_rollback(self):
        for operation in ("create", "update", "delete"):
            with self.subTest(operation=operation):
                session = AsyncMock(spec=AsyncSession)
                session.exec.return_value = MagicMock()
                session.exec.return_value.first.return_value = Book()
                session.commit.side_effect = RuntimeError("write failed")
                service = BookService()
                with self.assertRaisesRegex(RuntimeError, "write failed"):
                    if operation == "create":
                        await service.create_book(BookCreateModel(**VALUES), session)
                    elif operation == "update":
                        await service.update_book(
                            uuid4(), BookUpdateModel(**VALUES), session
                        )
                    else:
                        await service.delete_book(uuid4(), session)
                session.rollback.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
