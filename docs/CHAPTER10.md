# Chapter 10: roles and current accounts

Implemented the [tutorial role policy](https://jod35.github.io/fastapi-beyond-crud-docs/site/chapter10/): active users with `user` or `admin` roles can use book CRUD. Signup always creates an active ordinary user. Client input cannot assign privileged roles. `/api/v1/auth/me` returns safe account fields, never password hashes.

Access requests resolve the account from PostgreSQL, so deleted or inactive accounts are rejected and role changes take effect without minting a new token. Login and refresh also reject inactive accounts. Token validation and Redis revocation remain in place.

Apply the additive migration with `.venv/bin/alembic upgrade head`. Existing accounts receive the ordinary role and active status. To deliberately promote an existing local account, run `.venv/bin/python -m scripts.promote_admin EMAIL`. No account is automatically promoted.

Verified 2026-10-01: 18 unit tests pass; import/compile and import-order checks pass. Migration upgrade, repeated upgrade and Alembic schema check pass against the configured database. Live fictional-account checks covered safe signup defaults, `/me`, promotion, deactivation, deleted accounts, authenticated CRUD, invalid/expired token rejection, refresh, logout TTL and revocation across API restart. Verification records and exact Redis keys were cleaned up.
