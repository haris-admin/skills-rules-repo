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
