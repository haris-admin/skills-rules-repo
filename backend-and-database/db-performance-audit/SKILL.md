---
name: db-performance-audit
description: Inspect query execution plans, missing indexes, connection pooling health, and cache hit ratios.
---

# Database Performance Audit

## Checklist
1. **EXPLAIN ANALYZE**: Profile slow queries for sequential scans on large tables.
2. **Index Hygiene**: Ensure all foreign keys and frequently filtered columns have appropriate B-tree or GiST indexes.
3. **N+1 Query Elimination**: Use joined loading (`selectinload`, `joinedload`) in async ORMs.
4. **Cache Offloading**: Maintain a high cache hit ratio (Redis/ElastiCache) for immutable reference datasets.

