# Fleet records: one system of record per field

> Notion is the fleet's CMDB and CRM, Plane is the issue record, and Alexandria is the knowledge record. Each field has exactly one owner — write to that owner, and link to the others.

## Why

Two systems that both claim to own the same fact drift, and the drift is silent until
someone acts on a stale value. The fleet has already paid for this once: a venture
portfolio was hand-maintained in two places (`vault/chambers/startup-ventures.md` and the
environment fact sheet) and the copies disagreed, resolved in ADR-0001 §2 by deleting the
duplicate. The same failure mode is now available in three new places at once.

## The registers

| Register | Owns | Where |
|---|---|---|
| **Notion — CMDB** | IT assets, SaaS subscriptions, cloud accounts, domains, API-key *references*, costs, renewal dates | database "IT Assets / Configuration Items" |
| **Notion — CRM** | organisations, contacts, interactions, next actions | Notion databases (being built) |
| **Plane** | issues, tickets, project work items | `tapease` + `ai_ideas` workspaces → mirrored one-way into Notion |
| **Alexandria** | durable knowledge: chambers, ADRs, refined analysis | `haris-admin/alexandria` vault |

## Rules

- **One writer per field.** Decide which register owns a fact *before* syncing it anywhere. If two could plausibly own it, pick one and link to the other — never copy the value.
- **Mirrors are one-way.** Plane → Notion is a mirror. Never write back from Notion; that creates two masters and a reconciliation job nobody asked for.
- **Alexandria stays canonical for knowledge.** Notion and Plane *link* to Alexandria documents; they do not restate them.
- **Never store secret values in Notion.** The CMDB has an `API Key` CI type — it holds a *reference* (key name, location, owner, rotation date), never the key. A value found in a page is an incident: rotate, replace with a pointer, and report it.
- **Do not infer.** A field is written only from a stated source. Renewal dates with no stated source stay empty — an empty field is honest, an invented date is a liability. (Haris, 2026-09-13: *"If you know the renewal dates, start filling them in. Otherwise leave them open."*)
- **Verify by reading back** after any write to an external register; a 2xx is not proof the value landed.
- **Writes are idempotent** — match rows on a stable business key (e.g. asset `Name`), never on a timestamp, so a re-run cannot duplicate a record.
- **Report deltas, not dumps.** When asked to fetch a register, summarise counts and changes; persist anything durable to Alexandria rather than leaving it only in chat.

## Applies to

Any agent or script that reads or writes Notion, Plane, or the Alexandria vault — including the
CMDB fetch/report routine, the renewals watch, the CRM follow-up digest, and any future sync.
