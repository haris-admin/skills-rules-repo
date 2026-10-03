#!/usr/bin/env python3
"""Pre-Dispute — rolling 12-hour worker report (delivers verbatim to the group).

Cron: `55 9,21 * * *` as a no_agent job, so this stdout IS the message. Sources:
  ~/.hermes/state/predispute_worker_log.jsonl            (claims, heartbeats, outcomes)
  ~/.hermes/cron/executions.db                           (ticks of the two crons)
  ~/.hermes/cron/jobs.json                               (are the worker crons paused?)
  ~/.hermes/cache/scratch/predispute_worker_state.json   (any claim still open = leak)
  http://localhost:8008/health + :8009/health            (endpoints)
Secrets are never printed: only the presence of the agent key is checked.

PAUSED-AWARE: while the claim tick + worker are paused there are no ticks to count
and nothing is meant to run, so the report says STANDBY (🟡) rather than blaming a
dead backend for work that was never scheduled (❌). The ❌ verdict is reserved for
a pipeline that is supposed to be running.

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
JOBS_FILE = pathlib.Path("/home/habib/.hermes/cron/jobs.json")
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


def worker_states() -> dict[str, dict]:
    """enabled/state/paused_at for the two worker crons (so a paused worker is not
    reported as a broken pipeline)."""
    out: dict[str, dict] = {}
    try:
        data = json.loads(JOBS_FILE.read_text())
        jobs = data.get("jobs", data)
        jobs = list(jobs.values()) if isinstance(jobs, dict) else jobs
        for j in jobs:
            jid = j.get("id")
            if jid in (CLAIM_JOB, WORKER_JOB):
                out[jid] = {
                    "enabled": bool(j.get("enabled")),
                    "state": j.get("state"),
                    "paused_at": j.get("paused_at"),
                    "last_run_at": j.get("last_run_at"),
                }
    except Exception:
        pass
    return out


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
    refused = [e for e in events if e.get("event") == "refused"]

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
    base_url = ""
    insecure_optin = False
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(errors="replace").splitlines():
            if line.strip().startswith("PLUTO_HERMES_PREDISPUTE_AGENT_API_KEY=") and line.split("=", 1)[1].strip():
                key_present = True
            if line.strip().startswith("PLUTO_HERMES_PREDISPUTE_BASE_URL="):
                base_url = line.split("=", 1)[1].strip()
            if line.strip().startswith("PLUTO_HERMES_PREDISPUTE_ALLOW_INSECURE_LOCAL=") and line.split("=", 1)[1].strip().lower() in ("1", "true", "yes", "on"):
                insecure_optin = True

    workers = worker_states()
    paused = bool(workers) and all(not w["enabled"] for w in workers.values())
    paused_note = ""
    if paused:
        stamps = sorted(w.get("paused_at") or w.get("last_run_at") or "" for w in workers.values())
        since = stamps[0] if stamps and stamps[0] else ""
        paused_note = "worker crons PAUSED" + (f" since {since[:16].replace('T', ' ')}" if since else "")
    elif workers:
        paused_note = "worker crons " + (" · ".join(f"{k[:4]}:{'on' if w['enabled'] else 'off'}" for k, w in workers.items()))

    problems, fyi = [], []
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
    if base_url and not base_url.lower().startswith("https://"):
        host = base_url.split("://", 1)[1].split("/", 1)[0].split(":")[0].lower() if "://" in base_url else ""
        if insecure_optin and host in ("127.0.0.1", "localhost", "::1"):
            fyi.append(f"non-prod loopback override ACTIVE (http://{host}) - unset PLUTO_HERMES_PREDISPUTE_ALLOW_INSECURE_LOCAL for production")
        else:
            problems.append(f"PLUTO_HERMES_PREDISPUTE_BASE_URL is not HTTPS ({base_url.split('://', 1)[0]}://) - the worker refuses to start")
    if refused:
        reasons = sorted({str(e.get("reason", "")).split(" (or set")[0].strip() for e in refused})
        problems.append(f"worker REFUSED TO START {len(refused)}x: " + " | ".join(reasons[:3]) + (" | …" if len(reasons) > 3 else ""))
    b, a = health(8008), health(8009)
    pipeline_down = b != "ok"  # backend is the pipeline's dependency
    if (b != "ok" or a != "ok") and not paused:
        problems.append(f"endpoint health backend={b} acma={a}")

    lines = []
    if paused:
        lines.append(
            f"⏸️ STANDBY — {paused_note}: no claim ticks are scheduled, so the zeros below are EXPECTED, not a failure."
            + (f" The dev stack is also down (backend {b}, acma {a})." if (b != "ok" or a != "ok") else "")
        )
    elif pipeline_down:
        lines.append(
            f"❌ PIPELINE DOWN — backend unreachable ({b}) for the whole window: NO work could have run. "
            "The counts below are UNMEASURED, not evidence of idleness."
        )
    lines += [
        "☿ Pre-Dispute — 12h worker report",
        f"   window: {win_from} → {win_to} AEST",
        f"   workers: {paused_note or 'state unknown'}",
        f"   ticks: claim {ticks.get(CLAIM_JOB, '?')} · worker {ticks.get(WORKER_JOB, '?')}   (60s interval)",
        f"   jobs: claimed {len(claimed)} · completed {len(completed)} · failed {len(failed)}"
        + (f" · heartbeats {len(heartbeats)}" if heartbeats else ""),
        f"   queue: {queue}",
        f"   endpoints: backend {b} · acma {a}",
    ]
    if fyi:
        lines.append("🟡 " + "; ".join(fyi))
    for e in claimed:
        lines.append(f"   • {e.get('merchant_name')} (ABN {e.get('abn')}) — job {str(e.get('job_id'))[:8]}")
    for e in failed:
        lines.append(f"   • FAILED {str(e.get('job_id'))[:8]} — {e.get('error_code')}")
    for e in rejected:
        lines.append(f"   • {e.get('event')} — http {e.get('http_status')} {(e.get('category') or '')}")
    if not claimed and not failed and not rejected:
        if paused:
            lines.append("   (no queue activity in the window — the worker is paused, nothing was claimed)")
        elif pipeline_down:
            lines.append("   (counts UNMEASURED — the pipeline was down, so this is not evidence that nothing was waiting)")
        else:
            lines.append("   (no queue activity in the window — nothing was waiting)")
    if paused:
        lines.append("🟡 STANDBY — worker crons are paused; resume both to start claiming again" + (f" (endpoints backend={b} acma={a})" if (b != "ok" or a != "ok") else ""))
        if problems:
            lines.append("   outstanding while paused: " + "; ".join(problems))
    elif pipeline_down:
        lines.append("❌ FAILED — reporting over a dead dependency: " + "; ".join(problems))
    else:
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
