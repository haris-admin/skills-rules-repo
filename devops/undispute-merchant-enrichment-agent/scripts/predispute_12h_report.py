#!/usr/bin/env python3
"""Pre-Dispute — rolling 12-hour worker report (delivers verbatim to the group).

Cron: `55 9,21 * * *` as a no_agent job, so this stdout IS the message. Sources:
  ~/.hermes/state/predispute_worker_log.jsonl            (claims, heartbeats, outcomes)
  ~/.hermes/cron/executions.db                           (ticks of the two crons)
  ~/.hermes/cache/scratch/predispute_worker_state.json   (any claim still open = leak)
  http://localhost:8008/health + :8009/health            (endpoints)
Secrets are never printed: only the presence of the agent key is checked.

Always exits 0 (a non-zero exit makes the scheduler send its own error alert).
"""
from __future__ import annotations

import json
import pathlib
import sqlite3
import urllib.request
from datetime import datetime, timedelta, timezone

LOG_FILE = pathlib.Path("/home/habib/.hermes/state/predispute_worker_log.jsonl")
STATE_FILE = pathlib.Path("/home/habib/.hermes/cache/scratch/predispute_worker_state.json")
EXEC_DB = pathlib.Path("/home/habib/.hermes/cron/executions.db")
ENV_FILE = pathlib.Path("/mnt/c/Users/habib/.hermes/.env")
CLAIM_JOB = "e3cc72366dd7"
WORKER_JOB = "ff18d93e2d10"
TICK_LIMIT = 400
AEST = timezone(timedelta(hours=10))


def ts_of(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        d = datetime.fromisoformat(str(value))
    except Exception:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def health(port: int) -> str:
    try:
        with urllib.request.urlopen(f"http://localhost:{port}/health", timeout=4) as r:
            return "ok" if r.status == 200 else f"http {r.status}"
    except Exception:
        return "DOWN"


def main() -> int:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=12)
    win_from = cutoff.astimezone(AEST).strftime("%d %b %H:%M")
    win_to = now.astimezone(AEST).strftime("%d %b %H:%M")

    events: list[dict] = []
    if LOG_FILE.exists():
        for line in LOG_FILE.read_text(errors="replace").splitlines():
            try:
                ev = json.loads(line)
            except Exception:
                continue
            ts = ts_of(ev.get("ts"))
            if ts and ts >= cutoff:
                events.append(ev)

    claimed = [e for e in events if e.get("event") == "claimed"]
    completed = [e for e in events if e.get("event") == "completed"]
    failed = [e for e in events if e.get("event") == "failed"]
    rejected = [e for e in events if e.get("event") in ("claim_failed", "complete_rejected", "fail_rejected")]
    heartbeats = [e for e in events if e.get("event") == "heartbeat"]

    ticks = {}
    errors = {}
    try:
        con = sqlite3.connect(f"file:{EXEC_DB}?mode=ro", uri=True)
        for jid in (CLAIM_JOB, WORKER_JOB):
            rows = con.execute("select finished_at, status, error from executions where job_id=? order by rowid desc limit ?", (jid, TICK_LIMIT)).fetchall()
            in_win = [r for r in rows if (t := ts_of(r[0])) and t >= cutoff]
            ticks[jid] = len(in_win)
            errors[jid] = sum(1 for r in in_win if r[1] != "completed" or r[2])
        con.close()
    except Exception as exc:
        ticks = {"err": str(exc)[:60]}
        errors = {}

    state = {}
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
        except Exception:
            state = {}
    status = state.get("status", "none")
    if status == "job_claimed":
        age = ts_of(state.get("last_heartbeat_at") or state.get("claimed_at"))
        mins = int((now - age).total_seconds() // 60) if age else None
        queue = "busy: **a claim is still OPEN** " + (f"({mins} min since the last heartbeat — LEAK)" if mins is not None and mins > 12 else f"({mins} min since the last heartbeat)")
    elif status == "closed":
        queue = f"idle (last job {state.get('outcome')})"
    else:
        queue = f"idle (state={status})"

    key_present = False
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(errors="replace").splitlines():
            if line.strip().startswith("PLUTO_HERMES_PREDISPUTE_AGENT_API_KEY=") and line.split("=", 1)[1].strip():
                key_present = True

    problems = []
    if status == "job_claimed" and (age := ts_of(state.get("last_heartbeat_at") or state.get("claimed_at"))) and (now - age) > timedelta(minutes=12):
        problems.append("open claim past its lease")
    if rejected:
        problems.append(f"{len(rejected)} rejected call(s): " + ", ".join(sorted({str(e.get("event")) + ":" + str(e.get("http_status")) for e in rejected})))
    if errors.get(WORKER_JOB):
        problems.append(f"{errors[WORKER_JOB]} worker tick error(s)")
    if errors.get(CLAIM_JOB):
        problems.append(f"{errors[CLAIM_JOB]} claim tick error(s)")
    if not key_present:
        problems.append("PLUTO_HERMES_PREDISPUTE_AGENT_API_KEY missing")
    b, a = health(8008), health(8009)
    if b != "ok" or a != "ok":
        problems.append(f"endpoint health backend={b} acma={a}")

    lines = [
        "☿ Pre-Dispute — 12h worker report",
        f"   window: {win_from} → {win_to} AEST",
        f"   ticks: claim {ticks.get(CLAIM_JOB, '?')} · worker {ticks.get(WORKER_JOB, '?')}   (60s interval)",
        f"   jobs: claimed {len(claimed)} · completed {len(completed)} · failed {len(failed)}"
        + (f" · heartbeats {len(heartbeats)}" if heartbeats else ""),
        f"   queue: {queue}",
        f"   endpoints: backend {b} · acma {a}",
    ]
    for e in claimed:
        lines.append(f"   • {e.get('merchant_name')} (ABN {e.get('abn')}) — job {str(e.get('job_id'))[:8]}")
    for e in failed:
        lines.append(f"   • FAILED {str(e.get('job_id'))[:8]} — {e.get('error_code')}")
    for e in rejected:
        lines.append(f"   • {e.get('event')} — http {e.get('http_status')} {str(e.get('detail'))[:90]}")
    if not claimed and not failed and not rejected:
        lines.append("   (no queue activity in the window — nothing was waiting)")
    lines.append(("🔴 " + "; ".join(problems) + " — needs attention") if problems else "🟢 no anomalies — worker idle and healthy")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # never let a report bug become a scheduler error alert
        print(f"☿ Pre-Dispute — 12h report unavailable: {type(exc).__name__}: {exc}")
        raise SystemExit(0)
