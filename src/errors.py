from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse


class BooklyException(HTTPException):
    status = 500
    message = "An unexpected error occurred"
    error_code = "server_error"

    def __init__(self):
        super().__init__(
            self.status,
            self.message,
            headers={"WWW-Authenticate": "Bearer"}
            if self.error_code == "invalid_token"
            else None,
        )


class InvalidToken(BooklyException):
    status = 403
    message = "Invalid or expired token"
    error_code = "invalid_token"


class RevokedToken(BooklyException):
    status = 403
    message = "Token has been revoked"
    error_code = "token_revoked"


class AccessTokenRequired(BooklyException):
    status = 403
    message = "Please provide an access token"
    error_code = "access_token_required"


class RefreshTokenRequired(BooklyException):
    status = 403
    message = "Please provide a refresh token"
    error_code = "refresh_token_required"


class UserAlreadyExists(BooklyException):
    status = 403
    message = "User with email already exists"
    error_code = "user_exists"


class InvalidCredentials(BooklyException):
    status = 403
    message = "Invalid email or password"
    error_code = "invalid_credentials"


class InsufficientPermission(BooklyException):
    status = 403
    message = "You are not allowed to perform this action"
    error_code = "insufficient_permissions"


class BookNotFound(BooklyException):
    status = 404
    message = "Book not found"
    error_code = "book_not_found"


class TagNotFound(BooklyException):
    status = 404
    message = "Tag not found"
    error_code = "tag_not_found"


class TagAlreadyExists(BooklyException):
    status = 409
    message = "Tag name already exists"
    error_code = "tag_exists"


class UserNotFound(BooklyException):
    status = 403
    message = "Account is unavailable"
    error_code = "account_unavailable"


class ReviewNotFound(BooklyException):
    status = 404
    message = "Review not found"
    error_code = "review_not_found"


class AuthenticationUnavailable(BooklyException):
    status = 503
    message = "Authentication service unavailable"
    error_code = "authentication_unavailable"


def register_error_handlers(app: FastAPI):
    async def domain_error(request: Request, exc: BooklyException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.message, "error_code": exc.error_code},
            headers=exc.headers,
        )

    async def server_error(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "message": "An unexpected error occurred",
                "error_code": "server_error",
            },
        )

    app.add_exception_handler(BooklyException, domain_error)
    app.add_exception_handler(Exception, server_error)
