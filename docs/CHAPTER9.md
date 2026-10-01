# Chapter 9: JWT login, refresh and logout

Completed and verified 2026-10-01. Reference:
https://jod35.github.io/fastapi-beyond-crud-docs/site/chapter9/

Preserved the existing login, refresh and book-route work. Fixed the mismatch
between JWT_SECRET_KEY used for signing and JWT_SECRET used for decoding. Both
now use the same environment secret with an explicit HS256 allowlist. Missing
or malformed claims and wrong token roles fail before a protected handler runs.

## Endpoints and behavior

- POST /api/v1/auth/login: email/password JSON returns access_token, refresh_token
  and public user identifiers. Wrong password and unknown email share a generic
  403 response, retaining the chapter's convention. Hash verification runs outside
  the event loop; no password or password_hash is returned.
- All /api/v1/books CRUD routes require an access bearer token. Missing, expired,
  tampered, malformed or revoked credentials return 403.
- GET /api/v1/auth/refresh_token: send a refresh bearer token for a new access
  token. Access tokens are rejected here; refresh tokens cannot access books.
  Refresh also checks that the matching account still exists.
- GET /api/v1/auth/logout: revokes the presented access token's jti in Redis.
  Only that token is revoked, not its refresh token, other tokens or every device.
  A new login remains usable. Full session rotation is outside this chapter.

Tokens contain user identifiers, exp, jti and a boolean refresh flag. Access
expiry defaults to one hour; login refresh tokens expire in two days. JWT signing
prevents undetected modification but does not hide the payload: do not put
passwords or other secrets in it.

## Configuration and Redis

JWT_SECRET_KEY stays in ignored .env (minimum 32 characters); .env.example has
placeholders only. JWT_ALGORITHM is fixed to HS256. REDIS_URL defaults to the
existing Bookly Redis instance at localhost:6381, database 0. Keys use the
bookly:revoked: prefix. The client is owned and closed by the app lifespan.

Used redis.asyncio from redis 6.4.0 rather than the tutorial's older aioredis
package. Requirements now include redis and the installed PyJWT 2.15.1.
Blocklist TTL matches the token's remaining lifetime instead of an arbitrary
fixed duration. Redis lookup/write failures return a generic 503; validation
fails closed and logout does not falsely report success. Login/signup can still
operate during an outage, but protected requests and refresh cannot.

## Verification

- All 18 unittest tests pass, including the existing signup/CRUD checks and new
  token claims, login, role separation, revocation TTL and Redis outage tests.
- Live PostgreSQL/Redis HTTP checks passed for signup/login, generic bad
  credentials, all protected CRUD methods, invalid signatures, missing claims,
  expired access/refresh tokens, refresh renewal and deleted-account rejection.
- Revocation had a finite observed TTL of 3599 seconds and remained effective
  after a separate API process restart. The original refresh token and a new
  login still worked, confirming logout's per-token scope.
- Removed only fictional verification records and their exact Redis keys.
- Dependency consistency, compile/import and changed-file lint/format checks
  passed. No GitHub Actions workflow is configured in this repository.
