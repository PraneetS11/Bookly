# Chapter 12: domain errors

Named errors now represent token failures, revoked tokens, wrong token type, unavailable accounts, duplicate accounts, bad credentials, role failures, missing books/reviews/tags, duplicate tags, and authentication infrastructure failure. Registered handlers return stable `message` and `error_code` fields; unexpected failures return a generic 500 without exception text. Existing HTTP statuses remain compatible with earlier chapters, including Bookly's 403 authentication policy. FastAPI's input-validation errors remain 422.

Verified 2026-10-01: 24 unit tests pass, including safe unexpected-error output and preserved bearer challenge. Live HTTP regression checks verify error envelopes on missing related records while authenticated relationship CRUD and restart persistence continue to work. Chapter 11 commit: `a47d902`.
