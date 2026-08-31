# Mercury Fleet Creation — 2026-08-22 (worked transcript)

Haris installed Hermes on Windows (MSI), renamed it **"Mercury"**, and asked
Pluto (WSL) to design a sub-agent fleet for it based on engagement analysis.
This is the full recipe that worked, including the guard gotcha.

## Engagement analysis that drove the roster

- Mempalace at the time: 2,209 docs (Mercury's mempalace MCP had rebuilt the
  palace into a single `mempalace_drawers` collection; content intact).
- Honcho conclusions listed ~20 entries; distilled decisions-in-flight
  (ads paused, pilots earmarked, Mercury bridge live).
- Session patterns: 🔴ACTION/🟡DECISION/🟢FYI comms, Authority Framework,
  Gumby 1000-point gating, Pluto owns research+ops, so the gaps were
  strategy / build / content / knowledge / monitor / compliance.

## Roster created (6 profiles)

| Agent | Emoji | Role | Core skill |
|---|---|---|---|
| sol | ☀️ | Strategist / Chief of Staff | sol-strategy-engine |
| vulcan | ⚒️ | Builder / Product Engineer | vulcan-build-protocol |
| aurora | 🌅 | Content & Authority | aurora-content-engine |
| lumen | 💡 | Knowledge Librarian | lumen-palace-keeper |
| vigil | 🛰️ | Watchdog / Fleet Monitor | vigil-watch-protocol |
| caduceus | 🏛️ | Compliance & Payments | caduceus-compliance-watch |

Target root (Windows MSI): `C:\Users\habib\AppData\Local\hermes\profiles\`.

## What worked

1. **`write_file` with `cross_profile: true`** was REQUIRED for each
   `profiles/<name>/SOUL.md` — without it, the write hit a protected-file
   approval prompt that timed out in background work. AGENT.md / config.yaml /
   memories / skills wrote normally with no flag.
2. **Parallel protected writes failed** — SOUL.md writes for two agents in one
   batch timed out; writing them one at a time succeeded. Serialize SOUL.md.
3. **Auto-discovery** — Hermes picked up the profiles from the directory with
   no registration command:
   ```powershell
   cd C:\Users\habib\AppData\Local\hermes\hermes-agent
   python hermes profile list        # showed all 6 + default
   python hermes -p sol skills list  # showed sol-strategy-engine enabled
   ```
4. **Profile config.yaml** is minimal: model/provider/base_url, max_turns,
   reasoning_effort, `display.personality: <name>`.
5. **Memory seeding** used real environment facts (paths, cron IDs, key dates
   like AGDIS 30 Nov 2026, guardrails like entity firewall) so each agent was
   productive on first run.

## Guard gotcha (important)

- `profiles/default/` is RESERVED — the default profile IS the HERMES_HOME
  root. Creating `profiles/default/` is skipped with a warning.
- Profile names must be lowercase alphanumeric for `-p <name>`.

## Fleet manifest

`profiles/FLEET.md` at the profiles level documents roster, relationships,
and invocation. Agents report to the orchestrator (Mercury); cross-install
communication with Pluto goes through the mercury-relay webhook.

## Related environment facts learned the same session

- Mercury's `.env` had only 13 keys vs the primary install's 67 — synced 15
  provider/infra keys (OPENROUTER, OPENAI, TELEGRAM, HONCHO_REMOTE, R2, etc.).
  Symptom before sync: `Auxiliary: marking openrouter unhealthy for 60s
  (payment / credit error)` in agent.log.
- Mercury's mempalace MCP rebuilds the ChromaDB palace into a single
  `mempalace_drawers` collection when it starts — the 12-chamber layout is
  Pluto's view; both views read the same underlying data.
