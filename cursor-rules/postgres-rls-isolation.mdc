---
name: postgres-rls-isolation
description: Implement airtight multi-tenant data isolation and role-based access control (RBAC) using native PostgreSQL Row-Level Security (RLS) and session context variables. Use when adding tenant-scoped tables, writing admin/teacher/student access policies, or creating transaction-scoped empirical RLS test suites.
---

# PostgreSQL Native RLS Isolation & Role-Based Access Control

## 1. Multi-Tenant Session Context (`current_setting`)
- Enable RLS on every table: `ALTER TABLE <table> ENABLE ROW LEVEL SECURITY;` and `ALTER TABLE <table> FORCE ROW LEVEL SECURITY;`.
- Set session context via `SET LOCAL app.current_tenant_id = '<uuid>';` upon acquiring a connection from the pool.
- Write RLS policies ensuring queries only return rows matching:
  ```sql
  tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid
  ```

## 2. Supabase & PostgREST Role-Based Access Control (RBAC)

### The Infinite Recursion Trap & `SECURITY DEFINER`
Querying `public.profiles` (or user role tables) from inside an RLS policy on that same table or child tables will trigger **infinite recursion** unless evaluated via a security definer helper:

```sql
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.profiles
    WHERE id = auth.uid()
      AND role IN ('admin', 'super_admin')
  );
$$;
```

**Mandatory Security Safeguards**:
1. Always set `SECURITY DEFINER` so the check runs with function creator privileges, bypassing caller RLS.
2. Always pin `SET search_path = public` to prevent search-path hijacking.
3. Grant execute permissions explicitly: `GRANT EXECUTE ON FUNCTION public.is_admin() TO authenticated;`.

### Role-Based Policies vs Hardcoded Identity Literals
Never hardcode specific email addresses (e.g. `auth.jwt() ->> 'email' = 'admin@example.com'`) in production policies. Use role helper functions:
```sql
CREATE POLICY "Admins or owners can access feedback"
  ON public.feedback
  FOR ALL
  TO authenticated
  USING (public.is_admin() OR auth.uid() = user_id)
  WITH CHECK (public.is_admin() OR auth.uid() = user_id);
```

## 3. Transaction-Scoped Empirical Testing Pattern
Validate RLS policies using real database transactions that rollback at test completion, verifying both positive access and negative denial without polluting test data:

```javascript
// Example in Jest / Vitest with pg client
describe('Postgres RLS Policy Enforcement', () => {
  let client;
  beforeAll(async () => { client = await pool.connect(); });
  afterAll(async () => { client.release(); });

  it('allows admin to read all rows but isolates student to owned rows', async () => {
    await client.query('BEGIN');
    try {
      // 1. Act as Student
      await client.query('SET LOCAL ROLE authenticated');
      await client.query(`SET LOCAL "request.jwt.claims" = '{"sub": "${studentId}", "role": "authenticated"}'`);
      
      const studentRows = await client.query('SELECT * FROM public.sensitive_data');
      expect(studentRows.rows.every(r => r.user_id === studentId)).toBe(true);

      // 2. Act as Admin
      await client.query(`SET LOCAL "request.jwt.claims" = '{"sub": "${adminId}", "role": "authenticated"}'`);
      const adminRows = await client.query('SELECT * FROM public.sensitive_data');
      expect(adminRows.rows.length).toBeGreaterThan(studentRows.rows.length);
    } finally {
      await client.query('ROLLBACK');
    }
  });
});
```
