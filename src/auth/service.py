from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.concurrency import run_in_threadpool

from .models import User
from .schemas import UserCreateModel
from .utils import generate_password_hash


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        result = await session.exec(select(User).where(User.email == email))
        return result.first()

    async def user_exists(self, email: str, session: AsyncSession) -> bool:
        return await self.get_user_by_email(email, session) is not None

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        values = user_data.model_dump(exclude={"password"})
        password_hash = await run_in_threadpool(
            generate_password_hash, user_data.password
        )
        new_user = User(**values, password_hash=password_hash)
        try:
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
        except Exception:
            await session.rollback()
            raise
        return new_user
