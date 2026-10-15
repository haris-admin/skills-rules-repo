---
name: date-gated-crons
description: "Use when a cron must fire only on a calendar condition."
version: 1.0.0
---

# Date-Gated Crons (monitor-gated scheduling)

## When to Use
- A cron must fire only on a calendar condition cron syntax can't express directly: **last day of the month**, first/last weekday, Nth Monday, etc.
- Example: Month-End Review (`09d6d950544f`, fires only on the last calendar day at 12:00).

## The Pattern: deterministic monitor script + daily schedule
Cron can express `1-7` day-of-month ranges but not "last day of month". Instead of hand-computing dates or running wasted agent ticks, use the cron **monitor** feature:

1. **Daily schedule** (`0 12 * * *`) — the job checks every day at the target time.
2. **Monitor script** (`monitor: <name>.py`, relative to `~/.hermes/scripts/`) — prints STABLE output every tick EXCEPT on the real trigger date, where it prints a DIFFERENT stable string.
3. The scheduler hashes the monitor output: unchanged → silent skip (no agent run); changed → agent runs with a `MONITOR CHANGE DETECTED` diff injected.
4. **First tick always runs as baseline** — for an already-past trigger, use `cronjob(action='run')` to fire manually.

## The month-end detector (reference implementation)
`~/.hermes/scripts/month_end_check.py` (created 2026-08-31):

```python
import datetime
today = datetime.date.today()
if today.month == 12:
    last = datetime.date(today.year, 12, 31)
else:
    last = datetime.date(today.year, today.month + 1, 1) - datetime.timedelta(days=1)
print(f"MONTH_END {today.isoformat()}" if today == last else "NOT_MONTH_END")
```

Handles Dec 31 and Feb 28/29 via next-month-minus-one-day arithmetic. No timestamps → deterministic (critical: the monitor output MUST be byte-stable or every tick looks changed and the agent fires daily).

## Completion-gated chain (Month-End → Start-of-Month, 31 Aug 2026)

For "run B once A finishes, whatever time it takes" — schedule B every 15 min in a
window and gate it on a completion file the agent writes at the end of A:

- **Job A — Month-End Review** (`09d6d950544f`): `1 0 1 * *` (1st 00:01, no monitor
  needed — day-of-month 1 is expressible). Reviews the just-ended month and MUST
  save a dated copy to `~/.hermes/research_outputs/month-end-YYYY-MM.md` (YYYY-MM =
  the ended month) so downstream jobs can detect completion.
- **Job B — Start-of-Month Rule Refresh** (`2f4e89762abb`): `*/15 0-3 1 * *` +
  `monitor: month_end_complete_check.py` + `context_from: [09d6d950544f]`.
  The monitor prints `NOT_FIRST_DAY` (not the 1st), `NOT_COMPLETE` (1st, output
  file missing), or `MONTH_END_COMPLETE YYYY-MM` (1st, file present). B fires only
  when that string changes → within 15 min of A finishing. `context_from` injects
  A's output into B's prompt.

Reference monitor: `~/.hermes/scripts/month_end_complete_check.py`.

```python
today = datetime.date.today()
if today.day != 1: print("NOT_FIRST_DAY"); raise SystemExit(0)
ym = f"{today.year}-{today.month-1:02d}" if today.month > 1 else f"{today.year-1}-12"
out = Path.home() / ".hermes" / "research_outputs" / f"month-end-{ym}.md"
print(f"MONTH_END_COMPLETE {ym}" if out.is_file() else "NOT_COMPLETE")
```

Pitfall: the first monitor tick always runs as baseline (agent fires once even if
not complete) — the Start-of-Month prompt must handle a missing/stale input by
deferring honestly, never fabricating.

## Creating one
```
cronjob(action='create', schedule='0 12 * * *', monitor='month_end_check.py',
        prompt='<full self-contained brief; final response is delivered>',
        deliver='telegram:<chat_id>', skills=[...])
```
- `monitor` takes a bare filename (script lives in `~/.hermes/scripts/`); absolute/home-relative paths are rejected.
- The prompt must be SELF-CONTAINED (fresh session, no chat context). It should open with "The monitor confirms today is the last calendar day of the month (or this is a manual fire)."
- Skills array loads the operating contract so the run behaves like the fleet's other crons.

## One-shot relative jobs ('in 30m', 'tomorrow at 11:30')

A one-shot resolved into the past never fires and never errors — the human just waits for a reminder
that does not exist, and finds out hours later. Three steps prevent that:

1. **Read the clock immediately before creating the job**: `date '+%Y-%m-%d %H:%M:%S %Z (%A)'`. In a
   long-running session the "today" carried in context goes stale between turns — it can be a day or
   more behind — so "tomorrow"/"next Monday" computed from it lands on the wrong date. When the date
   matters, corroborate against an independent clock: other jobs' `next_run_at` values, the mtimes of
   files the fleet is actively writing, or `git log --format='%ci'` on a commit made in the same
   working session. Two clocks disagreeing means the context date is the wrong one.
2. **Prefer an absolute ISO timestamp over a phrase** (`schedule='<YYYY-MM-DD>T11:30:00'`) when the
   target is a specific wall-clock moment. 'in 2h' is fine for "soon"; a named moment should not
   depend on the scheduler re-deriving your intent.
3. **Verify `next_run_at` on the created job is in the FUTURE.** That one field is the proof the
   schedule resolved as intended; a past value (or null) means it will not fire, whatever the
   schedule string looked like.

**To answer "did it fire?", read the job record — never your own memory of creating it.** A finished
one-shot shows `last_run_at` set, `last_status: ok`, `repeat.completed == repeat.times`,
`state: completed` and `enabled: false`; `last_error` / `last_delivery_error` show the opposite case.
That is also how you distinguish "the reminder fired and delivery failed" from "the job never ran".

## Reminders for a dated external event (invite, booking, deadline)

The clock-read and absolute-ISO rules above cover the *mechanics*. Anchoring a reminder to a real event
adds five things:

- **Choose the lead time for the JOB it does.** ~30 minutes before is the right warning for *attending*;
  it is too late to *prepare*, and a fresh-session reminder carries no context to fall back on. A reminder
  that only says "you have a meeting today" 30 minutes ahead leaves no room to get ready, so offer (or
  add) an earlier prep nudge rather than assuming one reminder covers both jobs.
- **Resolve the event's timezone explicitly and write it into the prompt**, converting to the scheduler's
  local time and naming the zone — never assume the host's zone matches the event's. State which check you
  ran: a zone with no daylight saving needs no conversion, one that switches does.
- **Carry the event's own facts, and forbid additions.** Organiser and their role, join link, duration,
  what the other side explicitly asked for, and the stakes ("this is the first stage of the review
  process") all belong in the prompt, plus the literal instruction *"do not invent or add anything beyond
  these"* — a reminder running in a fresh session will otherwise embellish.
- **`attach_to_session: true` for anything the human will act on**, so the delivery is replyable and the
  brief stays in context; a fire-and-forget alert gives them nothing to reply to.
- **A rescheduled event supersedes the old slot: re-issue, don't add.** Record "was X, now Y" in the
  artefact the human reads, create the reminder against the NEW moment, and clear the reminder for the
  superseded slot so it cannot fire. File the event in the knowledge vault in the same pass — the vault
  note is what the reminder's prompt points at, and it outlives the reminder (`alexandria-vault-sync`).
- **Mine the event page for the ACTION WINDOW, not just the date.** When the event is application- or
  approval-based (hackathon, accelerator, invite-only), the reminder's real job is to surface the
  deadline the human does not know: the registration/application window, any price step ("standard
  ticket closes X, then jumps to Y"), and the fact that approval is required so applying early matters.
  Read those facts off the page when you create the job and put them in the prompt — a reminder that
  only names the event date fires too late to act on. If the page needs JavaScript, drive the browser to
  get the ticket table rather than settling for the server-rendered summary.
- **Never act for the owner.** A reminder may inform, prepare and draft; it must not RSVP, book, pay or
  contact the organiser on their behalf. State that limit in the prompt so the fresh session cannot
  decide to be helpful.

## Follow-up checkpoints for an open external process (application, partnership, sales thread)

When the owner says "add a checkpoint for us to reach out to <person> in <month>" about a process still
in flight, create a **draft-only checkpoint**, not a send job:

- **One-shot absolute ISO schedule per checkpoint** — the process has a stated timeline (an expected
  interview window, a promised notification month), so anchor each checkpoint on that date rather than
  a recurrence. `deliver` to the chat the owner reads, `attach_to_session: true` so their reply picks the
  thread back up instead of starting cold.
- **The prompt must classify the state from the record BEFORE producing anything** — it fires weeks later
  in a fresh session, so it has to reconstruct: read the vault folder (git pull first), the source page,
  and this job's own prior output, then branch on what it finds. Name the branches and their deliverables
  in the prompt: *invited* → prep brief for the next round; *declined* → the follow-up/thanks note the
  counterparty invited; *silent / no outcome yet* → a short no-pressure nudge. One branch, one deliverable.
- **Draft, never send.** A scheduled job contacting a third party on the owner's behalf is a boundary
  violation; state the rule literally in the prompt ("do NOT send any email or message — draft and remind
  only") and close by telling the owner the one word that dispatches it.
- **Absence of evidence is the SILENT branch — forbid inventing a status.** A fresh-session agent will
  otherwise narrate a plausible reply nobody sent; the prompt must say that no evidence reads as silent.
- **A later checkpoint is a FOLLOW-UP, not a duplicate: tell it the earlier one exists** and that its
  draft may or may not have been sent, so it verifies the record instead of assuming.
- **Record every job id plus its fire date in `~/.hermes/ops/environment.md`.** That file is the memory
  layer for scheduling — the "what is pending for this relationship?" question is answered there, not from
  the cron list.

## Pitfalls
- **The WSL2 clock can be DAYS behind — a calendar gate then fires on the wrong day, silently.**
  Verified 2026-10-16: a session read `date` as `2026-10-08` and every cron output, report and file
  mtime agreed with it, while the truth (three independent HTTP `Date` headers) was **16 October**.
  `systemd-timesyncd` was active but had only started at 06:03 that morning, after a host
  sleep/resume left the guest clock ~8 days behind; everything computed in between was mis-dated:
  date-based lookback windows collapsed (a podcast "last 3 days" window returned `None` and reported
  zero items), and outputs were written under the wrong day's name. `timedatectl` saying
  `System clock synchronized: yes` is NOT proof of correctness — it is proof of a *current* sync.
  Guard against it:
  ```bash
  # authoritative wall clock, independent of this host
  curl -sI --max-time 10 https://www.google.com | grep -i '^date:'   # compare with `date -u`
  ```
  Any cron whose logic depends on the calendar (or any diagnostic session reading dated artefacts)
  must compare against a network source before trusting local dates — and re-read the *newest*
  outputs rather than believing a report's own filename. If skew is found, expect date-stamped
  files from the skewed window to stay wrong forever (mtime is the clock at write time), so judge
  freshness by content, not name. Fix: reboot/resume the WSL VM (guest re-syncs at start) and keep
  the Windows host's `w32time` service running (it was **Stopped** on this host, which lets the host
  clock drift in the first place).
- **Stable output is mandatory** — never embed `datetime.now()` time in the monitor's common path. Only the trigger string varies.
- **Baseline first tick** fires the agent even if the date isn't the trigger — if that's wrong for the job, create it on the day BEFORE the trigger, or accept one baseline run.
- **Manual fire for backfill**: `cronjob(action='run', job_id=..., prompt='...')` runs immediately in background; outcome re-enters the conversation.
- **Delivery**: `deliver` without `:thread_id` lands in the main chat on thread platforms.
- Generalize the detector to other conditions (first weekday of month = `today.day <= 7 and today.weekday() < 5`; Nth Monday = `(today.day - 1) // 7 == N-1 and today.weekday() == 0`) — same pattern, new script.
