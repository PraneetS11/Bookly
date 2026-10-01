# Chapter 6 completion

Verified on 2026-09-30 against the existing configured PostgreSQL database.
Reference: https://jod35.github.io/fastapi-beyond-crud-docs/site/chapter6/

The existing BookService, SQLModel AsyncSession dependency and database routes
were retained. Remaining fixes correct BookCreateModel's name, add a validated
publication date, use the separate Book response schema with updated_at, roll
back failed writes, and dispose the existing engine during shutdown. The old
root main.py deletion is retained; run the application as src:app.

The API exposes GET/POST /api/v1/books/ and GET/PATCH/DELETE
/api/v1/books/{book_uid}. IDs are UUIDs. Create returns 201, delete returns an
empty 204, missing records return 404 and invalid UUIDs/bodies return 422.
Updates retain the chapter's required title, author, publisher, page_count and
language fields. Lists are ordered by creation time descending.

## Publication-date compatibility

The existing books.published_date column was VARCHAR while the Python model
expected a datetime. It is now consistently a Python date/PostgreSQL DATE,
accepting YYYY-MM-DD JSON input. The existing database received this one-time
schema correction (create_all does not change existing columns):

```sql
ALTER TABLE books ALTER COLUMN published_date TYPE date
USING published_date::date;
```

The table had no pre-existing records during verification. The single temporary
record from the failed initial check was removed by its exact UUID. The table
was not dropped. New databases get DATE from the model automatically.

The configured database uses a connection pooler. Following the column change,
live requests reproduced stale prepared-query errors. Both asyncpg's statement
cache and SQLAlchemy's prepared-statement cache are disabled for this development
connection; SSL and the existing URL are preserved. No credentials are committed.

## Verification

- `python -m compileall -q src` and application import passed.
- `python -m unittest discover -s tests -v`: four tests passed, covering create
  response/date validation, UUID/404 behavior, empty delete responses and rollback
  for each write operation. Unit tests do not contact the database.
- Live HTTP: create/list/read passed; created UUID survived a stopped/restarted
  API process; update survived another restart; delete returned 204 then 404.
- Unknown UUIDs returned 404, malformed UUIDs and invalid bodies/dates returned
  422. Only verification records were created and deleted.
- No GitHub Actions workflow is currently configured in this repository.
