import uuid
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from src.config import Config

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def generate_password_hash(password: str) -> str:
    return password_context.hash(password)


def verify_password(
    password: str,
    hashed_password: str,
) -> bool:
    try:
        return password_context.verify(password, hashed_password)
    except (ValueError, TypeError):
        return False


def create_access_token(
    user_data: dict,
    expiry: timedelta | None = None,
    refresh: bool = False,
) -> str:
    payload = {
        "user": user_data,
        "exp": datetime.now(timezone.utc)
        + (expiry if expiry is not None else timedelta(minutes=60)),
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }

    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET_KEY.get_secret_value(),
        algorithm=Config.JWT_ALGORITHM,
    )

    return token


def decode_token(token: str) -> dict | None:
    try:
        data = jwt.decode(
            token,
            Config.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[Config.JWT_ALGORITHM],
            options={"require": ["user", "exp", "jti", "refresh"]},
        )
        if type(data["refresh"]) is not bool or type(data["exp"]) is not int:
            return None
        uuid.UUID(data["jti"])
        uuid.UUID(data["user"]["uid"])
        if not isinstance(data["user"]["email"], str):
            return None
        return data
    except (jwt.PyJWTError, ValueError, TypeError, KeyError, AttributeError):
        return None
