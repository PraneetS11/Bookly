from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.concurrency import run_in_threadpool

from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist

from .dependencies import AccessTokenBearer, RefreshTokenBearer
from .schemas import UserCreateModel, UserLoginModel, UserModel
from .service import UserService
from .utils import create_access_token, verify_password

auth_router = APIRouter()
user_service = UserService()

REFRESH_TOKEN_EXPIRY = timedelta(days=2)


@auth_router.post(
    "/signup",
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_account(
    user_data: UserCreateModel,
    session: AsyncSession = Depends(get_session),
):
    if await user_service.user_exists(
        user_data.email,
        session,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with email already exists",
        )

    return await user_service.create_user(
        user_data,
        session,
    )


@auth_router.post("/login")
async def login_user(
    login_data: UserLoginModel,
    session: AsyncSession = Depends(get_session),
):
    user = await user_service.get_user_by_email(
        login_data.email,
        session,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid email or password",
        )

    password_valid = await run_in_threadpool(
        verify_password,
        login_data.password,
        user.password_hash,
    )

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid email or password",
        )

    user_data = {
        "email": user.email,
        "uid": str(user.uid),
    }

    access_token = create_access_token(
        user_data=user_data,
    )

    refresh_token = create_access_token(
        user_data=user_data,
        expiry=REFRESH_TOKEN_EXPIRY,
        refresh=True,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user_data,
        },
    )


@auth_router.get("/refresh_token")
async def get_new_access_token(
    token_details: dict = Depends(RefreshTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    user = await user_service.get_user_by_email(token_details["user"]["email"], session)
    if user is None or str(user.uid) != token_details["user"]["uid"]:
        raise HTTPException(403, "Invalid or expired token")
    return {
        "access_token": create_access_token({"email": user.email, "uid": str(user.uid)})
    }


@auth_router.get("/logout")
async def revoke_token(
    request: Request, token_details: dict = Depends(AccessTokenBearer())
):
    try:
        await add_jti_to_blocklist(
            request.app.state.redis, token_details["jti"], token_details["exp"]
        )
    except RedisError:
        raise HTTPException(503, "Authentication service unavailable") from None
    return {"message": "Logged Out Successfully"}
