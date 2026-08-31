# Engaging Profile Agents for Real Work (2026-08-22 worked transcript)

After creating the Mercury fleet (Sol, Vulcan, Aurora, Lumen, Vigil, Caduceus),
we ran two profile agents on REAL tasks from the WSL orchestrator. This is the
invocation recipe that worked, including the two failures that must be avoided.

## Working invocation (Windows install, from WSL orchestrator)

```bash
powershell.exe -NoProfile -Command "cd C:\Users\<user>\AppData\Local\hermes\hermes-agent; .\venv\Scripts\python.exe hermes -p <name> chat -q \"<self-contained task>\"" 2>&1
```

Run it with `background=true` + `notify_on_complete=true`. The agent takes
1–6 min and makes REAL tool calls (Sol fetched amlhive.com.au, tapease.com.au,
pexaclear.com.au live; Lumen wrote and ran 8 ChromaDB audit scripts, dumped all
2,209 records).

## Two failures that MUST be avoided

1. **Bare `python hermes` fails on Windows** — `No module named
   'concurrent_log_handler'`. The MSI's venv has it; the system python does
   not. ALWAYS use `.\venv\Scripts\python.exe hermes`.
2. **Running from WSL bash resolves the WRONG HERMES_HOME** — `cd /mnt/c/...
   && python hermes` uses `~/.hermes` (WSL) so `-p sol` says "Profile 'sol'
   does not exist". The PowerShell wrapper is what makes it use the Windows
   profile store. (This bit us twice before the fix.)
3. **Manually-created profiles have NO `.env` of their own** — a profile
   created by hand (write_file into `profiles/<name>/`) does not inherit the
   install's root `.env`. First `chat -q` fails with
   `No usable credentials found for provider 'deepseek'. Set DEEPSEEK_API_KEY.`
   Fix: copy the root `.env` into every profile dir BEFORE first run:
   ```bash
   cp /mnt/c/Users/<user>/AppData/Local/hermes/.env \
      /mnt/c/Users/<user>/AppData/Local/hermes/profiles/<name>/.env
   ```
   (Done for all 6 fleet profiles 2026-08-22; symptom appears as a clean
   "Goodbye" after the query echo — easy to mistake for a model error.)

## Getting the FULL output

- `process(action='wait')` / `process(action='poll')` show only the TAIL of
  the report.
- Pull the complete report with:
  `process(action='log', session_id=..., offset=...)` — Sol's full analysis
  was ~250 lines deeper in the log than the visible tail.

## Fleet-agent memory ops can CLOBBER their own MEMORY.md (Caduceus incident, 2026-08-30)

A profile agent running `memory` with a `replace` whose `old_text` is a short
substring can wipe the ENTIRE memory block — if the store is one big entry,
replace swaps the whole entry for the new content. Caduceus's competitor-line
update dropped its memory from 1,695 → 744 chars (standing facts + working
notes gone). The agent detected it (usage collapse) and self-restored by
replacing the damaged entry with the full reconstructed block. Lessons:

- **Tell profile agents to use `add` for new facts, or `replace` with a LONG
  unique `old_text` (the full entry), never a short substring** — or accept
  they may need to rebuild their memory after a bad replace.
- If a profile agent's output mentions memory usage dropping suspiciously,
  that's the clobber; the restore pattern is: one batch replace of the
  damaged entry with the full reconstructed content (under the store's char
  limit).
- This is NOT a WSL-orchestrator problem — it's the profile's own memory
  store. The WSL memory tool is unaffected.

## Subagent interruption in fleet runs

Profile agents can spawn subagents (`delegate_task`); when the Windows-side
run is long, a child may be interrupted mid-API-call and the process returns
an orphan-recovery note (\"interrupted side-effecting tool may have executed;
its effect is UNKNOWN\"). Treat that run as PARTIAL: pull the log, use the
partial findings, and re-run the specific track if the deliverable is
incomplete. Do not assume the interrupted side-effect landed (verify any
claimed write).

## Self-contained prompts only

The profile agent has NO memory of your conversation. The prompt must include:
- full context (domain, key dates, constraints)
- the deliverable shape (report sections, framing like ACTION/DECISION/FYI,
  evidence labels)
- explicit instruction: report EMPTY results honestly, never fabricate query
  outcomes

## Worked examples

- Sol (strategist): website content analysis → ranked Gumby-gated options +
  ONE recommended move. 1m36s, 14 messages, 12 tool calls.
- Lumen (librarian): Mempalace blind-spot audit → wrote lumen_audit_stage1-3.py
  + probe scripts, dumped all 2,209 records, 16 vector queries, delivered
  5-section blind-spot report. 5m34s, 50 messages, 48 tool calls.

## Resuming a profile session

Each run prints a resume handle, e.g.
`hermes -p <name> -c "<task title>"` (or `--resume <session_id> -p <name>`).
Use it to continue a long strategy/library task from the Windows side.
