# Fleet Notion workspace (amlhive)

Operational facts for the AMLHive fleet's Notion. Read this before any Notion work here — the
upstream skill's defaults do not match this workspace.

## Tokens (in `/mnt/c/Users/habib/.hermes/.env`)

| Var | Integration | Status |
|---|---|---|
| **`NOTION_TOKEN_WS`** | `My-Token1` | ✅ **USE THIS.** Workspace-wide: ~724 objects visible. |
| `NOTION_TOKEN` | `connecting_openclaw` | ⚠️ Authenticates (HTTP 200) but **sees 0 objects** — nothing is shared with this integration. |
| **`NOTION_DATABASE_ID`** | — | `2bc88cf0-af52-45…` = the **CMDB** ("IT Assets / Configuration Items"). Its **data_source_id** is `40638825-121a-48f6-8f95-d2bf11fffb15` — use THAT for `/v1/data_sources/{id}/query`; the raw id 404s on the data_source endpoint but works on `/v1/databases/{id}`. |

Workspace name: **Haris Habib's Notion**. Other bot users present: `connecting_to_monitoring`, two
`Notion Agent Computer Session` entries.

**A token only ever sees what *its own* integration was shared with** — a valid token + empty search
= "not shared", not "no access".

## Purpose (set 2026-09-13)

Notion is the fleet's **CRM + CMDB + growing business "brain"**. It is expected to accumulate
increasing business detail over time, and is the system of record for contacts, assets/configuration
items, subscriptions and goals.

## Known databases (query with `POST /v1/data_sources/{id}/query`)

| Database | data_source_id | Role |
|---|---|---|
| **People** | `a07ddaf9-b6bd-8364-9113-07ea21165718` | **CRM** — contacts/people |
| **IT Assets / Configuration Items** | `40638825-121a-48f6-8f95-d2bf11fffb15` | **CMDB** — assets, subscriptions, services |
| Goals Tracker | `1cfddaf9-b6bd-8085-90ea-000b5c28882c` | goals |
| AI Founder Learning Path | `1cfddaf9-b6bd-8047-9370-000be753bdc0` | learning |
| Plane Issues | `ad2c3422-abd7-45ad-ba3f-1066226fafe9` | issue mirror |
| Plane Projects | `9070d92c-09ad-4309-a093-cb2c3d160ac3` | project mirror |

## CMDB content as observed (2026-09-14)

38 rows. **Every row has `Owner = Haris Habib`, and `Renewal Date` + `Warranty Expiry` + `Monthly
Cost` are EMPTY on all of them** — so nothing can alert on renewals and spend cannot be totalled.
Highest-value CMDB gap to fix.

~40 subscription / service / credential ledger entries, each its own page, most recently edited
2026-09-14: Claude Code (Taalas, AMLHive), ChatGPT (AMLHive), Cloudflare DNS, Cloudflare R2, Brevo,
Supabase Auth, Canva, Verif/Verify, Delisense, Postmark, Airwallex, Xero, Azure credits, AWS credits
(AMLHive), OpenRouter, DeepSeek, OpenClaw (Habib), GenSpark Claw, GenSpark subscription, Perplexity
Pro, Gemini Pro (Tapease), Cursor, Microsoft 365 (Tapease), Purely Mail, CRM in transit, domains
(amlhive.com.au, tapease.com.au), hardware (Windows mini PC, Windows 11 laptops, MacBook Pro),
Notion subscription, Plane.so integration.

## Gotchas

- **`app.notion.com/chat?t=<32hex>` is a Notion AI chat thread — NOT API-accessible.** Verified: the
  token 404s both as `/v1/pages/{uuid}` and `/v1/data_sources/{uuid}`. Tasks must live as **pages or
  database rows** to be automatable. Never promise to read a `/chat` link.
- **API version 2025-09-03:** what users call "databases" are **data sources**. Query via
  `POST /v1/data_sources/{id}/query`; create rows with `parent: {"database_id": "..."}`.
- **Share before you can see.** For any NEW page/database, the user must do page `...` → *Connect to*
  → the integration, or the API returns **404** even though the page exists.
- Rate limit ~3 req/s. Pass `page_size`/`start_cursor` to page through search.
- Search returns only what is shared; on this workspace that is ~724 objects across 6 data sources.

## Probe scripts (in this skill's `scripts/`)

```bash
python3 scripts/notion_probe.py NOTION_TOKEN_WS   # users/me + search summary
python3 scripts/notion_probe.py NOTION_TOKEN_WS --map      # list databases + task-like pages
python3 scripts/notion_probe.py NOTION_TOKEN_WS --recent   # newest pages by last_edited_time
```

They read the token from the Windows `.env` and **never print its value**.
