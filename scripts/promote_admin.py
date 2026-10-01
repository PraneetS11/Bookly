"""Promote one existing fictional local account; run with python -m scripts.promote_admin EMAIL."""

import asyncio
import sys

from sqlalchemy import select, update

from src.auth.models import User
from src.db.main import engine


async def main(email):
    engine.echo = False
    try:
        async with engine.begin() as connection:
            ids = (
                (await connection.execute(select(User.uid).where(User.email == email)))
                .scalars()
                .all()
            )
            if len(ids) != 1:
                raise ValueError("Expected exactly one existing account")
            await connection.execute(
                update(User).where(User.uid == ids[0]).values(role="admin")
            )
        print("Selected local account promoted to admin")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
