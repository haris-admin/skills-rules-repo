---
name: db-performance-audit
description: Inspect query execution plans, missing indexes, connection pooling health, and cache hit ratios. Use when queries or endpoints are slow, before/after adding an index, or when auditing a Postgres/Redis-backed service for N+1 queries and cache efficiency.
---

# Database Performance Audit

## Checklist
1. **EXPLAIN ANALYZE**: Profile slow queries for sequential scans on large tables.
2. **Index Hygiene**: Ensure all foreign keys and frequently filtered columns have appropriate B-tree or GiST indexes.
3. **N+1 Query Elimination**: Use joined loading (`selectinload`, `joinedload`) in async ORMs.
4. **Cache Offloading**: Maintain a high cache hit ratio (Redis/ElastiCache) for immutable reference datasets.

