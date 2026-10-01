from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from redis.exceptions import RedisError

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
