from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import RoleChecker, get_current_user
from src.db.main import get_session
from src.db.models import User

from .schemas import ReviewCreateModel, ReviewModel
from .service import ReviewService

review_router = APIRouter(dependencies=[Depends(RoleChecker(["user", "admin"]))])
service = ReviewService()


@review_router.get("/", response_model=list[ReviewModel])
async def list_reviews(session: AsyncSession = Depends(get_session)):
    return await service.get_all_reviews(session)


@review_router.get("/{review_uid}", response_model=ReviewModel)
async def get_review(review_uid: UUID, session: AsyncSession = Depends(get_session)):
    return await service.get_review(review_uid, session)


@review_router.post("/book/{book_uid}", response_model=ReviewModel, status_code=201)
async def add_review(
    book_uid: UUID,
    data: ReviewCreateModel,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await service.add_review_to_book(user.uid, book_uid, data, session)


@review_router.delete("/{review_uid}", status_code=204)
async def delete_review(
    review_uid: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await service.delete_review(review_uid, user.uid, session)
