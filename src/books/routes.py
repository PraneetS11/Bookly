from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import AccessTokenBearer
from src.books.schemas import Book, BookCreateModel, BookUpdateModel
from src.books.service import BookService
from src.db.main import get_session

book_router = APIRouter()
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
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    new_book = await book_service.create_book(
        book_data,
        session,
    )

    return new_book


@book_router.get(
    "/{book_uid}",
    response_model=Book,
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    return None
