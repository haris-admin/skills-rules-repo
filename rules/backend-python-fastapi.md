# Backend Engineering: Python & FastAPI Guidelines

Guidelines for building high-performance, robust, and maintainable backend services with Python and FastAPI.

## Architecture & Code Quality

1. **FastAPI & Async Conventions**:
   - Use asynchronous route handlers (`async def`) when calling async libraries (e.g. `httpx`, `asyncpg`, `motor`).
   - Use synchronous route handlers (`def`) when using blocking/CPU-bound libraries so FastAPI executes them in the thread pool.
   - Group related endpoints using `APIRouter` with modular tags and prefixes.

2. **Pydantic & Data Validation**:
   - Use Pydantic v2 models for all request bodies, query parameter schemas, and response models.
   - Explicitly define `response_model` on endpoints to filter internal fields and guarantee schema output.
   - Implement field validators using `@field_validator` with descriptive error messages.

3. **Dependency Injection**:
   - Use FastAPI's `Depends(...)` for authentication, database sessions, external clients, and common services.
   - Prefer yield-based dependencies for context managers (e.g. database sessions that auto-commit or rollback).

4. **Logging & Observability**:
   - Use structured logging (e.g. `structlog` or `logging` with JSON formatters).
   - Never log sensitive user credentials, auth tokens, or private customer data.
   - Include request IDs in all downstream logs for traceability.

5. **Package Management & Tooling**:
   - Maintain dependencies with `pyproject.toml` or `uv` / `poetry`.
   - Format with `ruff` and run type checks with `mypy` or `pyright`.

6. **Transaction Boundaries in Batch Loops (SQLAlchemy async)**:
   - Never call `session.rollback()` "to release the connection before a slow network call" in a
     session that other work shares. A rollback discards everything flushed but not yet
     committed, so a loop that reuses one session across items and commits once at the end
     silently keeps only the last item. Found in production (2026-09): a monthly screening batch
     lost every party's result and audit row but the last, while its metrics stayed green.
   - A rollback also ends the transaction, which drops any `SET LOCAL` context (e.g. an RLS tenant
     or bypass GUC). Re-apply it at the start of every transaction.
   - For batch work, commit per item or open a fresh session per item, so one item's failure
     cannot discard another's committed evidence. Prove it with a real-session test that asserts
     N committed rows for N items.

7. **Auth Identity Mutations**:
   - Any code path that updates an existing auth-provider identity (password, email, metadata) on
     behalf of an unauthenticated caller must first refuse privileged identities (platform or staff
     accounts), and must never set a password on an identity the caller has not proven they
     control. "No row in the app's users table" does not mean "no account" when staff identities
     live in a separate table.

8. **Shared Caches and Verbatim Provider Data**:
   - When two code paths share one cache entry and one writer adds internal markers (e.g.
     `_source_result_id`), every reader must strip them before persisting the payload as "the
     provider's response". A reader that only strips the keys it knows about will store the other
     writer's markers inside an immutable evidence row. Keep one shared strip-list constant and a
     test per reader that seeds the cache with the other writer's shape.
