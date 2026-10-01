import os
import unittest
from unittest.mock import AsyncMock
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("JWT_SECRET_KEY", "bookly-unit-test-secret-not-for-production")
from fastapi import HTTPException
from pydantic import ValidationError

from src.books.schemas import BookCreateModel
from src.books.service import BookService
from src.db.models import Review, User
from src.reviews.schemas import ReviewCreateModel
from src.reviews.service import ReviewService
from src.tags.service import TagService


class RelationshipTests(unittest.IsolatedAsyncioTestCase):
    async def test_review_missing_book_is_404_without_write(self):
        session = AsyncMock()
        session.get.return_value = None
        with self.assertRaises(HTTPException) as error:
            await ReviewService().add_review_to_book(
                uuid4(),
                uuid4(),
                ReviewCreateModel(rating=5, review_text="Good"),
                session,
            )
        self.assertEqual(error.exception.status_code, 404)
        session.commit.assert_not_awaited()

    async def test_review_delete_checks_owner_and_deletes(self):
        owner = uuid4()
        review = Review(user_uid=owner, book_uid=uuid4(), rating=5, review_text="Good")
        session = AsyncMock()
        session.get.return_value = review
        with self.assertRaises(HTTPException) as error:
            await ReviewService().delete_review(review.uid, uuid4(), session)
        self.assertEqual(error.exception.status_code, 403)
        session.delete.assert_not_awaited()
        await ReviewService().delete_review(review.uid, owner, session)
        session.delete.assert_awaited_once_with(review)
        session.commit.assert_awaited_once()

    async def test_creator_comes_from_authenticated_account(self):
        from unittest.mock import MagicMock

        session = AsyncMock()
        session.add = MagicMock()
        user = User()
        data = BookCreateModel(
            title="Fictional",
            author="Test",
            publisher="Test",
            published_date="2024-01-01",
            page_count=10,
            language="English",
            user_uid=uuid4(),
        )
        book = await BookService().create_book(data, session, user_uid=user.uid)
        self.assertEqual(book.user_uid, user.uid)

    async def test_missing_tag_update_delete_are_404(self):
        session = AsyncMock()
        session.get.return_value = None
        for operation in ("get_tag", "delete_tag"):
            with self.assertRaises(HTTPException) as error:
                await getattr(TagService(), operation)(uuid4(), session)
            self.assertEqual(error.exception.status_code, 404)

    def test_rating_bounds(self):
        for rating in (0, 6):
            with self.assertRaises(ValidationError):
                ReviewCreateModel(rating=rating, review_text="Test")
        self.assertEqual(ReviewCreateModel(rating=5, review_text="Test").rating, 5)
