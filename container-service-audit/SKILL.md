---
name: container-service-audit
description: Use when auditing or exposing a containerised service.
version: 1.0.0
author: mercury
license: MIT
metadata:
  hermes:
    tags: [docker, audit, security, exposure, orchestration]
    related_skills: [monitoring-alert-verification, native-mcp, vulnerability-watcher, wsl-windows-interop]
---

# Container service audit

For any long-lived container in the estate that was set up once and never revisited: prove what it is
for, measure whether anything uses it, price its risk surface, then adopt, expose or retire it
deliberately. "It is running" is not a finding.

## When to Use

- The user asks "is X running?", "can we use X?", or "what is X doing?" about a tool in the estate.
- You are about to wire a third-party tool into the agent stack and need to know if it earns its place.
- A container is found holding credentials, is many versions behind, or duplicates work another layer
  already does.
- You must make a headless service reachable without exposing it to the LAN.

## Rule 0: running is not the same as in use

A container can be `Up 2 weeks` with `restart=unless-stopped` and still have processed **nothing**.
Usage lives in the application's own datastore, not in `docker ps`. Count entities, executions and
credentials before forming any opinion:

```bash
docker exec <db-container> psql -U <user> -d <db> -tAc "select 'workflows='||count(*) from workflow_entity"
```

A dormant service holding live credentials is **negative value**: full risk surface, zero output. Say
that plainly instead of describing it as "available".

## Procedure

1. **Inventory the runtime.** `docker ps` shows the published-ports column, the fastest read on exposure.
   Then `docker inspect` for `Created`, `State.StartedAt`, `RestartCount`, `RestartPolicy`, network, mounts.
2. **Enumerate env var NAMES only** — never values:
   `docker inspect <c> --format '{{range .Config.Env}}{{println .}}{{end}}' | cut -d= -f1 | sort`.
   A tool handed dozens of production secrets inline carries a second copy of the estate's keys; that is
   the finding, and the names tell you exactly what it was built to touch.
3. **Read usage from the datastore** (Rule 0). Prefer row counts over a UI or a log line — an indexer
   message like `Processed 0 draft workflows` describes drafts, not the workflow table, and will talk
   you out of a real deployment.
4. **Price the version.** Compare the running image tag with the registry's current release, then ask OSV
   about the exact version rather than trusting a generic "no known vulns": POST
   `https://api.osv.dev/v1/query` with `{"package":{"name":<pkg>,"ecosystem":<eco>},"version":<v>}`.
   Tens of advisories including auth-bypass or sandbox-escape entries, on a host holding credentials, is
   an action item regardless of whether the port is open today.
5. **Build a reachability matrix**: published ports (`docker port`, `NetworkSettings.Ports`), container IP
   and network, a real connect from the host, a connect from a peer container. State explicitly that *not
   being published* is currently the only thing protecting the secrets.
6. **Check for self-referential config.** Any base-URL env var set to `localhost` inside a container
   (`*_BASE_URL`, `WEBHOOK_URL`, a callback URL) points at **the container itself** and is broken for
   every external caller — the same class of bug silently disables the tool's own webhooks.
7. **List the overlap.** Name which of the tool's jobs already run in the existing orchestrator. Running
   the same job in two schedulers is the real cost: it doubles the failure modes and halves trust in
   whichever one speaks.
8. **Recommend in one shape:** the code-first orchestrator stays the scheduler of record and the evidence
   trail; the containerised tool becomes an **adapter** invoked over its API or MCP. A visual builder is
   genuinely better for SaaS connectors you would otherwise hand-code — that is its lane, not scheduling,
   and not a second credential store.

## Before anything destructive

- **Back up the datastore first**, into `~/.hermes/backups/<service>-<stamp>/`: a targeted
  `pg_dump --data-only --column-inserts -t <app tables>` plus a JSON export per table. A destructive step
  proposed in the same breath as the audit is only safe because of this dump — take it before you talk
  about deleting or upgrading.
- **Never delete user-authored content** (workflows, dashboards, documents) while auditing. An inactive
  workflow is still someone's work; enumerate it and let the owner decide.
- **Prefer a reversible exposure change over recreating the container.** A sidecar proxy can publish a port
  without touching the service's env, volume or DB, and `docker rm -f <sidecar>` reverses it. Recipes:
  `references/docker-exposure-recipes.md`.

## Pitfalls

- **`5678/tcp` in `docker ps` is EXPOSE, not published.** `docker port <c>` prints `(none published)` and
  `NetworkSettings.Ports` prints `{"5678/tcp": []}`. Confirm with an actual connect, not from the listing.
- **The host port may already be someone else's.** Find the owner before mapping — on Windows
  `Get-NetTCPConnection -LocalPort <n> -State Listen` then `Get-Process -Id <pid>` — and map a different
  host port rather than taking a live service down.
- **Docker Desktop does not forward a loopback-only publish to Windows localhost.**
  `-p 127.0.0.1:PORT:PORT` is reachable from WSL and invisible to the Windows browser; `-p 0.0.0.0:PORT:PORT`
  is reachable from both, and from the LAN. Tell the user which one they are getting before they go looking.
- **Never guess the database role.** Take user/db/host from the app container's own env; a peer container
  probably has no `postgres` role, and the error reads as a broken database rather than a wrong user.
- **Quote camelCase column names in psql.** Unquoted identifiers fold to lowercase, so `updatedAt` fails
  with `column "updatedat" does not exist` even though the table is right.
- **Auth being enforced is a result worth reporting.** `200` on a health endpoint plus `401` on the app's API
  routes is a healthy, closed posture — distinguish it from "reachable".
- **Version currency is not "no CVE against us".** Query the specific installed version; an advisory fixed
  in the previous release says nothing about the one running.

## Verification

- One real request per claim: health endpoint status code, an unauthenticated route returning 401, a
  peer-container fetch. Exit codes are not evidence.
- After any exposure change, prove reachability from the exact side that will use it (host, peer container,
  Windows browser) and record which bind scope you chose.

## Reporting

State, in order: what it is and whether it is used (with counts), what risk it carries (version, CVE count,
secret concentration), how it is reachable and what protects it, what it duplicates, then the single
recommended shape. Ask for the one decision that unblocks the next step — do not hand over a five-step plan
whose first step needs a decision you have not surfaced.

## Related

- `references/docker-exposure-recipes.md` — sidecar publish, Windows reachability, host-port conflict, backups.
- `monitoring-alert-verification` — the watchdog/silence discipline once the service is worth watching.
- `native-mcp` — register an adapter's MCP endpoint rather than writing webhook glue.
- `vulnerability-watcher` — permanent CVE tracking once the version question is settled.
