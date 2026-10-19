# Check existing contract id before specifying an audit row

Before a spec assigns an audit-contract id to a new entry point, grep the registry and the code for that id; a shared id with a different action is a requirement conflict.

**Scope:** every agent that writes or implements a spec containing an audit-contract row.

## Why this exists

Added 19 Oct 2026 (AMLHive C528 vs C434). C528 design 4.3 asked for `C314_V1_WORKERS_CRON_JOB_RUN_ARQ` with action `JOB_RUN`. Uncommitted C434 work had already registered that id for `CRON_CATCHUP_TRIGGERED`. A test written to the spec could not pass without breaking the other change.

## Core Directives

1. **Search before specifying.** Grep the registry file and every `*_CONTRACT_ID` constant for the id.
2. **Two actions on one id is a conflict, not a detail.** Stop and surface it with both sources. Do not rename or repoint either side.
3. **Check the uncommitted tree too.** `git diff` on the registry shows other sessions' unreleased rows.
4. **Let the owner decide** which change keeps the id or whether a new id is issued, then record it in both specs.

## Verification & Guardrails

- A Red test that cannot go Green without breaking a sibling change is a spec defect to raise, not a test to loosen.
