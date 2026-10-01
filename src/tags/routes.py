from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import RoleChecker
from src.books.schemas import BookDetailModel
from src.db.main import get_session

from .schemas import TagAddModel, TagCreateModel, TagModel
from .service import TagService

tags_router = APIRouter(
    responses={
        403: {"description": "Access token, verification or permitted role required"},
        404: {"description": "Requested resource does not exist"},
    },
    dependencies=[Depends(RoleChecker(["user", "admin"]))],
)
service = TagService()


@tags_router.get("/", response_model=list[TagModel])
async def list_tags(session: AsyncSession = Depends(get_session)):
    return await service.get_tags(session)


@tags_router.post("/", response_model=TagModel, status_code=201)
async def create_tag(
    data: TagCreateModel, session: AsyncSession = Depends(get_session)
):
    return await service.add_tag(data, session)


@tags_router.post("/book/{book_uid}/tags", response_model=BookDetailModel)
async def attach_tags(
    book_uid: UUID, data: TagAddModel, session: AsyncSession = Depends(get_session)
):
    return await service.add_tags_to_book(book_uid, data, session)


@tags_router.get("/{tag_uid}", response_model=TagModel)
async def get_tag(tag_uid: UUID, session: AsyncSession = Depends(get_session)):
    return await service.get_tag(tag_uid, session)


@tags_router.put("/{tag_uid}", response_model=TagModel)
async def update_tag(
    tag_uid: UUID, data: TagCreateModel, session: AsyncSession = Depends(get_session)
):
    return await service.update_tag(tag_uid, data, session)


@tags_router.delete("/{tag_uid}", status_code=204)
async def delete_tag(tag_uid: UUID, session: AsyncSession = Depends(get_session)):
    await service.delete_tag(tag_uid, session)
