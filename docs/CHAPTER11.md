# Chapter 11: relationships

Books now record the authenticated creator in `user_uid`. `/auth/me` includes submitted books. Book detail includes safe reviews and tags, loaded explicitly for async responses. Database models live in `src/db/models.py`; old model import paths re-export the same classes.

Review routes support list, detail, create for a book, and author-only deletion. Rating accepts 1 through 5 inclusive. Missing books/reviews return 404. Tag routes support create/list/detail/update/delete and attaching names to a book; duplicate names return 409 and repeated attachment is idempotent, including concurrent inserts through PostgreSQL conflict handling. All routes retain role and account checks.

Migration `c192d6831daa` preserves existing books with nullable creator IDs. No creator is invented for historical rows. A later backfill requires a verified owner mapping; until then those rows stay unassigned. Deleting a book removes its reviews and tag links; tags remain shared. Deleting an account clears book ownership and removes its authored reviews.

Verified 2026-10-01: 23 unit tests pass. Migration upgrade and schema comparison pass. Live HTTP checks verified creator spoof prevention, safe `/me`, review isolation, owner-only deletion, rating validation, missing records, shared tags, duplicate names/attachments, tag updates/deletes, and persistence after API restart. All fictional verification records were cleaned up. Existing records were preserved.

Chapter 10 commit: `2545d62`.
