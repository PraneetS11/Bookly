from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import AccessTokenBearer, RoleChecker, get_current_user
from src.auth.models import User
from src.books.schemas import Book, BookCreateModel, BookDetailModel, BookUpdateModel
from src.books.service import BookService
from src.db.main import get_session
from src.errors import BookNotFound

book_router = APIRouter(
    responses={
        403: {"description": "Access token, verification or permitted role required"},
        404: {"description": "Requested resource does not exist"},
    },
    dependencies=[Depends(RoleChecker(["admin", "user"]))],
)
book_service = BookService()
access_token_bearer = AccessTokenBearer()


@book_router.get(
    "/",
    response_model=List[Book],
)
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    books = await book_service.get_all_books(session)

    return books


@book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Book,
)
async def create_book(
    book_data: BookCreateModel,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    new_book = await book_service.create_book(
        book_data,
        session,
        user_uid=user.uid,
    )

    return new_book


@book_router.get(
    "/{book_uid}",
    response_model=BookDetailModel,
)
async def get_book(
    book_uid: UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    book = await book_service.get_book(
        book_uid,
        session,
    )

    if book is None:
        raise BookNotFound()

    return book


@book_router.patch(
    "/{book_uid}",
    response_model=Book,
)
async def update_book(
    book_uid: UUID,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    updated_book = await book_service.update_book(
        book_uid,
        book_update_data,
        session,
    )

    if updated_book is None:
        raise BookNotFound()

    return updated_book


@book_router.delete(
    "/{book_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_book(
    book_uid: UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    deleted_book = await book_service.delete_book(
        book_uid,
        session,
    )

    if deleted_book is None:
        raise BookNotFound()

    return None
