# Figure Verification Protocol

## Status tags (use exactly these)

| Tag | Meaning |
|---|---|
| VERIFIED | Primary or authoritative source found, number and period match, URL and retrieval date recorded |
| PARTLY VERIFIED | Source supports part of the claim, or only a secondary source, or number is close but period or definition differs. State the gap |
| CONTRADICTED | A source shows a different figure. State the right figure and source |
| UNVERIFIED | Plausible, not checked this session |
| UNMAPPABLE | Cannot be mapped to any source: internal projection, invented title, aspirational target, unnamed person |

## Rules

1. Assume wrong until proven. "Verified" in a prior document counts for nothing.
2. Prefer primary: regulator, statute, ASX filing, company report, standards body, registry. Then reputable press. Then vendor blogs.
3. Check definitions: connectors vs plugs vs sites; vehicles under management vs leases; orders vs deliveries; GTV vs revenue; financial year vs calendar year.
4. Check the period. A figure from two years ago is not a 2026 figure.
5. Check ownership and status of named companies (acquired, delisted, renamed, divested).
6. Recompute every derived number from the plan's own inputs in a script. Mark inconsistencies as CONTRADICTED (internal).
7. Cross-reconcile: do parts sum to the whole (market share lists, plug counts, TAM inputs)?
8. Job titles, named mentors, and "active conversations" are UNMAPPABLE unless a dated public source or log exists.
9. Record every claim in a register table with source URL and date. Keep UNMAPPABLE as its own section.
10. Law and tax items are information only, not advice; flag for a professional.

## Who checked (add a column)

`Claude` first-hand this session. `Sub-P` subagent that read a primary document. `Sub-S` subagent on secondary sources only. Treat `Sub-S` as one notch weaker than its tag. Spot-check the highest-stakes subagent findings yourself before relying on them.

## Source access limits

State plainly which primary sources could not be opened (for example a regulator site returning HTTP 403). Do not tag a rate or rule VERIFIED from secondary sources alone; use PARTLY VERIFIED.

## Register columns

ID | Claim | File | Type | Finding | Tag | Checked by | Source URL | Date checked
