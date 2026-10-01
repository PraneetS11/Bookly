# Chapter 8: user account creation

Verified against https://jod35.github.io/fastapi-beyond-crud-docs/site/chapter8/
on 2026-09-30 (America/Toronto).

## Working behavior

POST /api/v1/auth/signup accepts first_name and last_name (maximum 25 characters),
username (maximum 8), email (maximum 40), and password (minimum 6 characters).
It returns 201 with public account fields. Repeating an existing email returns
403 with the chapter's duplicate-account message. Invalid input returns 422.
No login or JWT endpoints were added.

Passwords are hashed using the chapter's Passlib/bcrypt approach. The missing
bcrypt backend is installed and pinned to 4.0.1, compatible with Passlib 1.7.4;
requirements.txt records the tested dependencies. Bcrypt passwords are limited
to 72 UTF-8 bytes and cannot contain null characters, avoiding silent truncation
or backend failures. Hashing runs in a worker thread so it does not block the
async API event loop.

## Corrections

- Matched generate_password_hash's definition to its service import; repaired
  verify_password to use its supplied hash rather than Python's built-in hash.
- Replaced password max_length=6 with min_length=6 and added the missing names.
- Added UserModel as a separate response schema, excluding password and hash.
  Kept the user's model-level password_hash exclusion too.
- Retained the existing router registration and SQLModel AsyncSession pattern.
  The service excludes plaintext password from ORM construction, commits,
  refreshes generated values, and rolls back failed writes.
- Disabled SQL echo so account inserts do not write password hashes to logs.
- Added focused password, signup, input-validation, lookup and rollback tests.

## Database and verification

The configured development database is at a4bb1f95dc35; alembic check reports
no schema differences. That existing 'add pass hash' revision is intentionally
left intact: it has no operations because password_hash already exists, and
Field(exclude=True) changes serialization, not the table schema.

Real-database testing used a separate temporary local PostgreSQL database with
the Chapter 6 books baseline and both existing migrations. The actual app
returned signup 201, duplicate email 403, invalid password 422, and /docs and
book listing 200. A new application lifespan still rejected the same email;
separate database inspection confirmed one persisted account, generated UUID
and timestamp, false verification state, and a hash accepting only the correct
password. Responses contained no password/hash. The temporary database was
removed; the configured development database's account data was not changed.

Run from the Bookly repository root:

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m alembic current
.venv/bin/python -m alembic check
.venv/bin/python -m uvicorn src:app --reload
```

All 12 tests pass, including the four existing book tests. pip check passes.
The existing Starlette/httpx deprecation warning remains. This follows the
chapter's pre-insert duplicate-email lookup; database-enforced email uniqueness
and protection against simultaneous duplicate signups remain later hardening.
