from uuid import UUID

from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from .models import Book
from .schemas import BookCreateModel, BookUpdateModel


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))

        result = await session.exec(statement)

        return result.all()

    async def get_book(self, book_uid: UUID, session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)

        result = await session.exec(statement)

        return result.first()

    async def create_book(
        self,
        book_data: BookCreateModel,
        session: AsyncSession,
        user_uid: UUID | None = None,
    ):
        book_data_dict = book_data.model_dump()

        new_book = Book(**book_data_dict, user_uid=user_uid)

        try:
            session.add(new_book)
            await session.commit()
            await session.refresh(new_book)
        except Exception:
            await session.rollback()
            raise

        return new_book

    async def update_book(
        self,
        book_uid: UUID,
        update_data: BookUpdateModel,
        session: AsyncSession,
    ):
        book_to_update = await self.get_book(
            book_uid,
            session,
        )

        if book_to_update is None:
            return None

        update_data_dict = update_data.model_dump()

        for key, value in update_data_dict.items():
            setattr(
                book_to_update,
                key,
                value,
            )

        try:
            await session.commit()
            await session.refresh(book_to_update)
        except Exception:
            await session.rollback()
            raise

        return book_to_update

    async def delete_book(
        self,
        book_uid: UUID,
        session: AsyncSession,
    ):
        book_to_delete = await self.get_book(
            book_uid,
            session,
        )

        if book_to_delete is None:
            return None

        try:
            await session.delete(book_to_delete)
            await session.commit()
        except Exception:
            await session.rollback()
            raise

        return book_to_delete

    async def get_user_books(self, user_uid: UUID, session: AsyncSession):
        result = await session.exec(
            select(Book)
            .where(Book.user_uid == user_uid)
            .order_by(desc(Book.created_at))
        )
        return result.all()
