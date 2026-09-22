#!/usr/bin/env python3
"""Pre-Dispute worker — lease operations for the claimed job in the state file.

Companion to predispute_enrich_poll.py: the poll script claims, this one keeps the
lease alive and closes the job. It never invents data — `complete` posts the
payload you hand it, `fail` posts a bounded error code — and it keeps the state
file truthful so the cron monitor gate (predispute_queue_state.py) reads the real
job status.

Usage
  ./predispute_agent_ops.py state                       # job_id / lease / expiry
  ./predispute_agent_ops.py heartbeat                   # extend the lease by 10 min
  ./predispute_agent_ops.py fail UNVERIFIABLE_MERCHANT_IDENTITY
  ./predispute_agent_ops.py complete --payload result.json

Env: PLUTO_HERMES_PREDISPUTE_AGENT_API_KEY (fallbacks: PREDISPUTE_AGENT_API_KEY,
HERMES_AGENT_API_KEY) from /mnt/c/Users/habib/.hermes/.env.
Exit codes: 0 = ok, 1 = error (printed as JSON on stdout).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

ENV_FILE = pathlib.Path("/mnt/c/Users/habib/.hermes/.env")
STATE_FILE = pathlib.Path("/home/habib/.hermes/cache/scratch/predispute_worker_state.json")
BASE_PATH = "/api/v1/agent/merchant-enrichment"
KEY_NAMES = ("PLUTO_HERMES_PREDISPUTE_AGENT_API_KEY", "PREDISPUTE_AGENT_API_KEY", "HERMES_AGENT_API_KEY")


def load_env() -> dict[str, str]:
    out: dict[str, str] = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(errors="replace").splitlines():
            s = line.strip()
            if s and not s.startswith("#") and "=" in s:
                k, v = s.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def agent_key(env: dict[str, str]) -> str:
    return next((env[n] for n in KEY_NAMES if env.get(n)), "")


def load_state(require_open: bool = True) -> dict:
    if not STATE_FILE.exists():
        sys.exit(json.dumps({"status": "error", "reason": f"no state file at {STATE_FILE} — run the poll first"}))
    rec = json.loads(STATE_FILE.read_text())
    if require_open and rec.get("status") != "job_claimed":
        sys.exit(json.dumps({"status": "error", "reason": f"state is '{rec.get('status')}', not job_claimed"}))
    return rec


def call(rec: dict, path: str, payload: dict | None) -> tuple[int | str, str]:
    key = agent_key(load_env())
    if not key:
        sys.exit(json.dumps({"status": "error", "reason": f"{KEY_NAMES[0]} missing from Hermes env"}))
    url = rec["backend_base"].rstrip("/") + path
    data = json.dumps(payload).encode() if payload is not None else b""
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "X-Hermes-Agent-Key": key}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:500]
    except Exception as e:
        return "ERR", repr(e)


def write_state(rec: dict) -> None:
    STATE_FILE.write_text(json.dumps(rec, indent=2))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["state", "heartbeat", "fail", "complete"])
    ap.add_argument("arg", nargs="?", help="error code for `fail`")
    ap.add_argument("--payload", help="JSON file for `complete`")
    a = ap.parse_args()

    rec = load_state(require_open=(a.action != "state"))
    job = rec["job"]
    job_id, lease = job["job_id"], job["lease_token"]

    if a.action == "state":
        print(json.dumps({"job_id": job_id, "merchant_name": job.get("merchant_name"), "abn": job.get("abn"), "origin_case_id": job.get("origin_case_id"), "lease_expires_at": job.get("lease_expires_at"), "claimed_at": rec.get("claimed_at"), "last_heartbeat_at": rec.get("last_heartbeat_at"), "acma_base_usable": rec.get("acma_base_usable")}, indent=2))
        return 0

    if a.action == "heartbeat":
        q = urllib.parse.urlencode({"lease_token": lease})
        status, body = call(rec, f"{BASE_PATH}/{job_id}/heartbeat?{q}", {})
        if status == 200:
            now = datetime.now(timezone.utc)
            rec["last_heartbeat_at"] = now.isoformat()
            rec["lease_expires_at"] = (now + timedelta(minutes=10)).isoformat()
            write_state(rec)
    elif a.action == "fail":
        if not a.arg:
            sys.exit(json.dumps({"status": "error", "reason": "fail requires an error code"}))
        q = urllib.parse.urlencode({"lease_token": lease, "error_code": a.arg})
        status, body = call(rec, f"{BASE_PATH}/{job_id}/fail?{q}", {})
        if status == 200:
            rec.update({"status": "closed", "outcome": f"FAILED({a.arg})", "closed_at": datetime.now(timezone.utc).isoformat()})
            write_state(rec)
    else:
        if not a.payload:
            sys.exit(json.dumps({"status": "error", "reason": "complete requires --payload <json file>"}))
        payload = json.loads(pathlib.Path(a.payload).read_text())
        payload["lease_token"] = lease
        status, body = call(rec, f"{BASE_PATH}/{job_id}/complete", payload)
        if status == 200:
            rec.update({"status": "closed", "outcome": "SUCCEEDED", "completed_at": datetime.now(timezone.utc).isoformat(), "completion_response": body[:500]})
            write_state(rec)

    print(json.dumps({"action": a.action, "job_id": job_id, "http_status": status, "response": body}))
    return 0 if status in (200, 204) else 1


if __name__ == "__main__":
    sys.exit(main())
