---
name: notion-cmdb-operations
description: "Use when reading or updating the fleet Notion CMDB."
platforms: [linux, macos, windows]
---

# Notion CMDB operations (fleet)

The AMLHive fleet uses **Notion as its CMDB** — the system of record for IT assets, SaaS
subscriptions, cloud accounts, domains and API-key *references* — and increasingly as its **CRM**.
Haris will periodically ask for this data to be fetched and reported; this skill is how.

## Connection

All values live in `/mnt/c/Users/habib/.hermes/.env` (**strip CRLF and BOM** when reading).
Never print a secret value — key *names* only.

| Var | Use |
|---|---|
| **`NOTION_TOKEN_WS`** | ✅ **the working token** (integration `My-Token1`). Use this. |
| `NOTION_TOKEN` | integration `connecting_openclaw` — authenticates but sees **0 objects**. Do not use. |
| **`NOTION_DATABASE_ID`** | the CMDB database id (`2bc88cf0-af52-45…`) |

Base `https://api.notion.com`, header `Notion-Version: 2025-09-03`.

**ID gotcha (2025-09-03 API):** a database has *two* ids. `NOTION_DATABASE_ID` works on
`GET /v1/databases/{id}` but **404s** on `/v1/data_sources/{id}`. To query rows, first resolve the
data source:

```bash
# database -> its data_sources[] -> use data_source id for queries
GET /v1/databases/{NOTION_DATABASE_ID}          # returns data_sources[0].id
POST /v1/data_sources/{data_source_id}/query    # the actual row query
```

CMDB data source id (verified 2026-09-13): **`40638825-121a-48f6-8f95-d2bf11fffb15`**
("IT Assets / Configuration Items").

## Fast path — use the bundled probe

```bash
S=~/.hermes/skills/productivity/notion/scripts/notion_probe.py
python3 $S NOTION_TOKEN_WS --map       # databases + task-like pages
python3 $S NOTION_TOKEN_WS --recent    # newest pages by last_edited_time
```

For a full CMDB dump (all rows + every property), page through
`POST /v1/data_sources/40638825-121a-48f6-8f95-d2bf11fffb15/query` with `page_size: 100` and
`start_cursor`. Rate limit is ~3 req/s — sleep ~0.35 s between calls.

## CMDB schema (19 properties)

`Name` (title) · `CI Type` (Hardware / Software / SaaS Subscription / Cloud Account / Domain /
API Key / Service / System) · `Environment` (Personal / Business / Production / Staging /
Development / Home / Office) · `Status` (Active / Trial / To assess / Missing details / Retired /
Cancelled) · `Criticality` (Critical / High / Medium / Low) · `Owner` (people) · `Vendor` ·
`Version` · `Monthly Cost` (number) · `Renewal Date` (date) · `Purchase Date` (date) ·
`Warranty Expiry` (date) · `Serial Number` · `Asset Tag` · `Admin URL` (url) · `Location` ·
`Notes` (rich_text) · `Created` · `Last Updated`.

## Known state (verified 2026-09-13 — re-verify before relying on it)

- **38 rows.** All `Owner = Haris Habib`.
- **`Renewal Date`, `Warranty Expiry` and `Monthly Cost` are EMPTY on every row.** No renewal can be
  alerted and spend cannot be totalled. The page bodies are **TODO stubs** ("Add renewal date,
  billing date, payment method…"), not data.
- Approximate facts recorded in page bodies (NOT exact dates — do not promote to `Renewal Date`
  without a source): Azure credits ~$5,000, *"probably expiring December 2026"*; AWS credits
  ~$9,200 remaining, no date; Perplexity Pro — cancellation decision due before **November**;
  Cursor 1-year free — converts to paid around **April/May**; Claude Code (AMLHive) ~**A$32/month**.
- **Do NOT invent or infer renewal dates.** If a date is not stated by a source, **leave the field
  empty** — Haris's explicit instruction (2026-09-13): *"If you know the renewal dates, start filling
  them in. Otherwise leave them open."*

## Writing rules

1. **Only write what a source states.** No inferred dates, no guessed costs.
2. **Never store secret VALUES.** The `API Key` CI type holds a *reference* — key name, where it
   lives, owner, rotation date. If a value ever appears in a page, rotate the key and replace it with
   a pointer, then say so.
3. **Set properties explicitly** on every write; never rely on defaults.
4. **Verify by reading back** after any write — a 200 is not proof the value landed.
5. **Idempotent updates**: match rows on `Name`, not on a timestamp, so a re-run doesn't duplicate.
6. Keep `Status` honest — `To assess` / `Missing details` are real states, don't silently normalise.

## Reporting pattern

When asked to "fetch the CMDB data", report: total rows · counts by `CI Type` and `Status` ·
items renewing in 30/60/90 days (once dates exist) · rows with `Missing details`/`To assess` ·
monthly cost total. Persist anything durable to Alexandria, not just the chat reply.

## Related

- `productivity/notion` — the general Notion API skill (+ `references/fleet-notion-workspace.md`)
- `devops/plane-issues` — the issue tracker that mirrors into Notion
- Rule: `rules/fleet-records-system-of-record.md`
