---
name: postgres-rls-isolation
description: Implement airtight multi-tenant data isolation using native PostgreSQL Row-Level Security (RLS) and session context variables.
---

# PostgreSQL Native RLS Isolation

## Architecture
- Use `ALTER TABLE <table> ENABLE ROW LEVEL SECURITY;` and `FORCE ROW LEVEL SECURITY;`.
- Set session context via `SET LOCAL app.current_tenant_id = '<uuid>';` upon acquiring a connection.
- Write RLS policies ensuring queries only return rows matching `tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid`.

## Safety Tests
- Test cross-tenant access is blocked at the database engine level.
- Test missing or malformed tenant context fails closed (0 rows returned or explicit error).

