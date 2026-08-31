# SQLite In-Memory Test Pattern (AMLHive Backend)

## Discovery (Jul 2026)
The AMLHive backend tests do NOT require PostgreSQL/RDS. The `conftest.py` (line 4-5) states:

> *"DB strategy: each test gets a fresh AsyncSession backed by an in-memory SQLite database. The session is rolled back after each test — no truncate/seed."*

This means:
- **No Docker** needed for test execution
- **No RDS/VPC access** needed from WSL
- **No test database setup** required
- Works fully on WSL without any infrastructure

## Why This Matters for Cron Testing
Previous assumption was that backend tests require RDS and should be skipped in WSL cron jobs. This was WRONG for AMLHive. Always check `conftest.py` first before deciding to skip backend tests.

## How It Works
```python
# tests/conftest.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

engine = create_async_engine(
    "sqlite+aiosqlite://",  # In-memory — no file needed
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
```

## Constraints
- SQLite doesn't support all PostgreSQL features (e.g. full-text search, some JSON operators, `ARRAY` type)
- Tests that use PostgreSQL-specific `ARRAY` columns or native PostGIS will fail on SQLite
- The `psycopg2`/`asyncpg` driver must be swapped for `aiosqlite` at the test level (done in conftest.py)
- Migration tests that test Alembic SQL generation may produce different SQL for SQLite vs PostgreSQL

## When to Use
- Unit tests and integration tests that don't use PostgreSQL-specific features
- CI/CD pipelines where running a PostgreSQL container is impractical
- WSL cron test runners where Docker/RDS is unavailable
- Development environments for quick test feedback

## When NOT to Use
- Tests that need PostgreSQL-specific features (array columns, tsvector, PostGIS)
- Production-like integration tests that must verify exact query behavior
- Tests that exercise Alembic migrations with PostgreSQL-specific DDL
