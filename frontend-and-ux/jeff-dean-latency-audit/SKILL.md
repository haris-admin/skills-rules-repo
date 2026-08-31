---
name: jeff-dean-latency-audit
description: Audit web application performance across the full stack using latency-budget hierarchies (L1 cache -> Memory -> Redis -> DB -> Network).
---

# Jeff Dean Latency Audit

## Latency Numbers Every Engineer Should Know
- L1 cache reference: 0.5 ns
- Main memory reference: 100 ns
- Redis in-memory query: 0.5 ms
- SSD random read: 150 us
- PostgreSQL query: 2-10 ms
- Datacenter roundtrip: 0.5 ms
- Cross-region WAN roundtrip: 50-150 ms

## Audit Steps
1. Measure payload size and asset compression (Brotli/Gzip).
2. Measure 3rd-party script impact on main thread execution time.
3. Ensure server-side data fetching utilizes caching layers to minimize database roundtrips.

