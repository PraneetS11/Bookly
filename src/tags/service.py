from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.db.models import Book, BookTag, Tag


class TagService:
    async def get_tags(self, session):
        return (await session.exec(select(Tag).order_by(Tag.created_at.desc()))).all()

    async def get_tag(self, tag_uid, session):
        tag = await session.get(Tag, tag_uid)
        if tag is None:
            raise HTTPException(404, "Tag not found")
        return tag

    async def save(self, tag, session):
        try:
            session.add(tag)
            await session.commit()
            await session.refresh(tag)
        except IntegrityError:
            await session.rollback()
            raise HTTPException(409, "Tag name already exists") from None
        except Exception:
            await session.rollback()
            raise
        return tag

    async def add_tag(self, data, session):
        return await self.save(Tag(name=data.name), session)

    async def update_tag(self, tag_uid, data, session):
        tag = await self.get_tag(tag_uid, session)
        tag.name = data.name
        return await self.save(tag, session)

    async def delete_tag(self, tag_uid, session):
        tag = await self.get_tag(tag_uid, session)
        try:
            await session.delete(tag)
            await session.commit()
        except Exception:
            await session.rollback()
            raise

    async def add_tags_to_book(self, book_uid, data, session):
        book = await session.get(Book, book_uid)
        if book is None:
            raise HTTPException(404, "Book not found")
        try:
            for item in data.tags:
                new_tag = Tag(name=item.name)
                await session.execute(
                    insert(Tag)
                    .values(
                        uid=new_tag.uid,
                        name=new_tag.name,
                        created_at=new_tag.created_at,
                    )
                    .on_conflict_do_nothing(index_elements=["name"])
                )
                tag = (
                    await session.exec(select(Tag).where(Tag.name == item.name))
                ).one()
                await session.execute(
                    insert(BookTag)
                    .values(book_id=book_uid, tag_id=tag.uid)
                    .on_conflict_do_nothing()
                )
            await session.commit()
            await session.refresh(book, attribute_names=["tags", "reviews"])
        except Exception:
            await session.rollback()
            raise
        return book
