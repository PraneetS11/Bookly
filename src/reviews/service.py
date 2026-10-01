from uuid import UUID

from fastapi import HTTPException
from sqlmodel import select

from src.db.models import Book, Review


class ReviewService:
    async def get_all_reviews(self, session):
        return (
            await session.exec(select(Review).order_by(Review.created_at.desc()))
        ).all()

    async def get_review(self, review_uid: UUID, session):
        review = await session.get(Review, review_uid)
        if review is None:
            raise HTTPException(404, "Review not found")
        return review

    async def add_review_to_book(self, user_uid, book_uid, data, session):
        if await session.get(Book, book_uid) is None:
            raise HTTPException(404, "Book not found")
        review = Review(**data.model_dump(), user_uid=user_uid, book_uid=book_uid)
        try:
            session.add(review)
            await session.commit()
            await session.refresh(review)
        except Exception:
            await session.rollback()
            raise
        return review

    async def delete_review(self, review_uid, user_uid, session):
        review = await self.get_review(review_uid, session)
        if review.user_uid != user_uid:
            raise HTTPException(403, "Cannot delete another user's review")
        try:
            await session.delete(review)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
