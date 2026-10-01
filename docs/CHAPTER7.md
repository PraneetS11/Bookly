# Chapter 7 completion

Verified on 2026-09-30. Chapter reference:
https://jod35.github.io/fastapi-beyond-crud-docs/site/chapter7/

The existing account model and async Alembic files are retained. User accounts
have generated UUIDs, nullable names, verification state and a database-generated
timezone-aware creation timestamp. Removed redundant UNIQUE(uid) from the model
and the uncommitted initial migration: the primary key already enforces
uniqueness, and the duplicate declaration caused an Alembic schema-check diff.
The applied revision identity remains 428d0696df90.

Alembic loads DATABASE_URL through Settings and imports both Book and User into
metadata. Percent-encoded URL characters are escaped for Alembic's config parser.
No database URL is stored in alembic.ini. Environment variants and virtual
environments are ignored. Startup no longer creates tables; engine cleanup is
preserved. No signup/login functionality was introduced.

## Existing Chapter 6 baseline

Following the chapter, revision 428d0696df90 adds user_accounts to a database
that already contains the Chapter 6 books table. It is not a complete initial
migration for a blank database. The configured development database already
has that baseline and is at this revision. No changes to its data were made.

Run migrations before starting the app:

```bash
.venv/bin/python -m alembic upgrade head
.venv/bin/python -m alembic current
.venv/bin/python -m alembic check
.venv/bin/python -m uvicorn src:app --reload
```

For a separate empty development database, set DATABASE_URL to that database,
create only the Chapter 6 Book table once, then apply the migration. Do not run
create_all for all metadata or stamp an unverified schema. The one-time baseline
can be created using the configured engine:

```python
import asyncio
from src.books.models import Book
from src.db.main import engine

async def create_baseline():
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Book.__table__.create)
    finally:
        await engine.dispose()

asyncio.run(create_baseline())
```

## Verification

- Configured database: Alembic current is 428d0696df90 (head), and alembic check
  reports no new operations; offline migration SQL compiles.
- Separate temporary local PostgreSQL database: created the Chapter 6 Book
  baseline, applied upgrade twice, checked schema agreement, downgraded only
  user_accounts and upgraded again. All passed. Temporary database removed.
- Persisted User in a rolled-back transaction: UUID generated, names nullable,
  is_verified false, created_at populated with timezone information.
- Application lifespan succeeded with create_all patched to raise if invoked.
- Existing unittest suite: 4 tests passed; existing Starlette/httpx deprecation
  warning remains.
