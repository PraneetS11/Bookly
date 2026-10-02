import asyncio

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def live() -> dict[str, str]:
    """Process liveness only; dependency outages must not trigger restart loops."""
    return {"status": "ok"}


async def check_dependencies(request: Request) -> dict[str, str]:
    async def database() -> str:
        try:
            async with asyncio.timeout(2):
                async with request.app.state.engine.connect() as connection:
                    await connection.execute(text("SELECT 1"))
            return "ok"
        except Exception:
            return "unavailable"

    async def cache() -> str:
        try:
            async with asyncio.timeout(2):
                await request.app.state.redis.ping()
            return "ok"
        except Exception:
            return "unavailable"

    db_status, redis_status = await asyncio.gather(database(), cache())
    return {"database": db_status, "redis": redis_status}


@router.get("/health/ready", responses={503: {"description": "Dependencies unavailable"}})
async def ready(request: Request) -> JSONResponse:
    checks = await check_dependencies(request)
    healthy = all(value == "ok" for value in checks.values())
    return JSONResponse(
        status_code=200 if healthy else 503,
        content={"status": "ready" if healthy else "not_ready", "checks": checks},
    )
