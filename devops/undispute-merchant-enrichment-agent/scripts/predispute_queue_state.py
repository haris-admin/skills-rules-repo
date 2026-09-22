#!/usr/bin/env python3
"""Pre-Dispute worker — deterministic queue signature (cron `monitor` gate).

Prints ONE of three stable strings so an agent-run cron wakes only when there is
something to do (Hermes skips the agent entirely when a tick's output matches the
previous tick's):

  idle                  — nothing claimed
  working:<job_id>      — a claim is live (heartbeat within the lease)
  stuck:<job_id>        — a claim exists with no heartbeat for >12 min (lease dead)

No timestamps, no counters: output is a pure function of the state file so a tick
with no state change never looks "changed". The claim itself is made by
predispute_enrich_poll.py (the no_agent tick), never by this script.
"""
from __future__ import annotations

import json
import pathlib
from datetime import datetime, timedelta, timezone

STATE_FILE = pathlib.Path("/home/habib/.hermes/cache/scratch/predispute_worker_state.json")
STALE_AFTER = timedelta(minutes=12)


def main() -> None:
    if not STATE_FILE.exists():
        print("idle")
        return
    try:
        rec = json.loads(STATE_FILE.read_text())
    except Exception:
        print("idle")
        return
    if rec.get("status") != "job_claimed":
        print("idle")
        return
    job_id = (rec.get("job") or {}).get("job_id", "unknown")
    stamp = rec.get("last_heartbeat_at") or rec.get("claimed_at")
    try:
        age = datetime.now(timezone.utc) - datetime.fromisoformat(stamp)
    except Exception:
        print(f"stuck:{job_id}")
        return
    print(f"stuck:{job_id}" if age > STALE_AFTER else f"working:{job_id}")


if __name__ == "__main__":
    main()
