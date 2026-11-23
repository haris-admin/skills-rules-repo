# Every handover to an implementer has a ticket, and the orchestrator moves it from Backlog to Todo when its gate is met

When a different tool or agent will build the work, the board is the contract: no ticket, no handover.

**Scope:** an orchestrating agent that specifies work and a named implementer that builds it.

---

## Core Directives

1. **One ticket per phase or slice**, created in Backlog with its gate, its card and the paths to the brief inside it, assigned to the owner.
2. **Move to Todo only when the gate is met** (approved plan hash, the owner's approval of the handover) and the card is final. Say so on the ticket in a comment.
3. **Gate lines are the only text the orchestrator edits** in the brief after approval; any other change needs a fresh approval.
4. **One entry page** (`START_HERE.md`) maps every stream to its ticket, gate and whether it may start today; keep it current as work merges.
5. **Check the ticket parser.** Parse the ticket files by their real heading level and compare the created count with the expected one; a skipped stream is easy to miss.

## Why this exists

**23 Nov 2026 (SonoVantage):** the owner handed all development to Antigravity. Six phase tickets, ten legal tickets and twenty shared-services tickets were created in Backlog; only the ungated first phase moved to Todo. The first run created 10 of 30 tickets because one file used a different heading level.
