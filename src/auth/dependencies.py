from uuid import UUID

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from redis.exceptions import RedisError
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.models import User
from src.db.main import get_session
from src.db.redis import token_in_blocklist

from .utils import decode_token


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=False)

    async def __call__(self, request: Request) -> dict:
        creds = await super().__call__(request)
        data = decode_token(creds.credentials) if creds else None
        if data is None:
            raise HTTPException(
                403, "Invalid or expired token", headers={"WWW-Authenticate": "Bearer"}
            )
        self.verify_token_data(data)
        try:
            revoked = await token_in_blocklist(request.app.state.redis, data["jti"])
        except RedisError:
            raise HTTPException(503, "Authentication service unavailable") from None
        if revoked:
            raise HTTPException(403, "Token has been revoked")
        return data

    def token_valid(self, token: str) -> bool:
        return decode_token(token) is not None

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data["refresh"]:
            raise HTTPException(403, "Please provide an access token")


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if not token_data["refresh"]:
            raise HTTPException(403, "Please provide a refresh token")


async def get_current_user(
    token: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
) -> User:
    user = await session.get(User, UUID(token["user"]["uid"]))
    if user is None or not user.is_active:
        raise HTTPException(403, "Account is unavailable")
    return user


class RoleChecker:
    def __init__(self, allowed_roles):
        self.allowed_roles = frozenset(allowed_roles)

    async def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(403, "You are not allowed to perform this action")
        return user
