#!/usr/bin/env python3
"""Pre-Dispute merchant-enrichment — worker poll tick (claim only).

Spec: docs/hermes-agent-instructions.md (haris-admin/undispute-scheme-neutral-resolution)
+ skill `undispute-merchant-enrichment-agent` (platform rebranded to Pre-Dispute, v0.200.x).

This script performs ONLY the cheap, idempotent half of the loop: it claims at
most one job and reports it. It never researches, never completes, never fails a
job, and never contacts the merchant. The agent does that, guided by the skill.

Credential: PLUTO_HERMES_PREDISPUTE_AGENT_API_KEY (Hermes env file; the backend
holds the same secret as HERMES_AGENT_API_KEY). Older names are accepted as
fallbacks. The old *Hermes-side* name HERMES_AGENT_API_KEY was removed 2026-09-22.

Base URL: PLUTO_HERMES_PREDISPUTE_BASE_URL is the Windows host LAN IP, which WSL
cannot reach (a Windows-bound listener is mirrored on loopback only), so a
/health probe falls back to http://localhost:8008.

Flags
  --quiet   watchdog mode for a no_agent cron: print NOTHING when there is no
            work (or when a job is already in flight); still prints a claim or a
            claim failure. Empty stdout means the cron delivers nothing.

Exit codes:  0 = no work (HTTP 204) / busy / claim failed / transport error
            10 = a job was claimed (job + lease written to the state file)
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone

ENV_FILE = pathlib.Path("/mnt/c/Users/habib/.hermes/.env")
STATE_FILE = pathlib.Path("/home/habib/.hermes/cache/scratch/predispute_worker_state.json")

CLAIM_PATH = "/api/v1/agent/merchant-enrichment/claim"
KEY_NAMES = ("PLUTO_HERMES_PREDISPUTE_AGENT_API_KEY", "PREDISPUTE_AGENT_API_KEY", "HERMES_AGENT_API_KEY")
FALLBACK_BASE = "http://localhost:8008"
STALE_AFTER = timedelta(minutes=12)  # lease is 10 min; heartbeat every ~4 min


def load_env() -> dict[str, str]:
    out: dict[str, str] = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(errors="replace").splitlines():
            s = line.strip()
            if s and not s.startswith("#") and "=" in s:
                k, v = s.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def agent_key(env: dict[str, str]) -> tuple[str, str]:
    for name in KEY_NAMES:
        if env.get(name):
            return name, env[name]
    return KEY_NAMES[0], ""


def _healthy(base: str) -> bool:
    try:
        with urllib.request.urlopen(base.rstrip("/") + "/health", timeout=5) as r:
            return r.status == 200
    except Exception:
        return False


def resolve_backend(env: dict[str, str]) -> tuple[str, bool]:
    configured = (env.get("PLUTO_HERMES_PREDISPUTE_BASE_URL") or "").rstrip("/")
    for candidate in (configured, FALLBACK_BASE):
        if candidate and _healthy(candidate):
            return candidate, True
    return (configured or FALLBACK_BASE), False


def resolve_acma_base(env: dict[str, str]) -> tuple[str, bool]:
    configured = env.get("PLUTO_HERMES_ACMA_BASE_URL", "http://localhost:8009").rstrip("/")
    for candidate in (configured, "http://localhost:8009"):
        if _healthy(candidate):
            return candidate, True
    return configured, False


def open_claim() -> dict | None:
    """A claim still inside its lease blocks a new one: exactly one job in flight."""
    if not STATE_FILE.exists():
        return None
    try:
        rec = json.loads(STATE_FILE.read_text())
    except Exception:
        return None
    if rec.get("status") != "job_claimed":
        return None
    stamp = rec.get("last_heartbeat_at") or rec.get("claimed_at") or ""
    try:
        age = datetime.now(timezone.utc) - datetime.fromisoformat(stamp)
    except Exception:
        return None
    return None if age > STALE_AFTER else rec


def post(url: str, payload: dict, headers: dict) -> tuple[int | str, str]:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", **headers}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:400]
    except Exception as e:  # transport: never treated as success
        return "ERR", repr(e)


def human(obj: dict) -> str:
    """Telegram-ready rendering for the no_agent cron (stdout is delivered verbatim)."""
    s = obj.get("status")
    if s == "job_claimed":
        return ("\u263f Pre-Dispute queue \u2014 JOB CLAIMED\n"
                f"   merchant: {obj.get('merchant_name')} (ABN {obj.get('abn')})\n"
                f"   job: {obj.get('job_id')}\n"
                f"   lease expires: {obj.get('lease_expires_at')}\n"
                "   \u2192 enrichment worker is taking it now.")
    if s == "claim_failed":
        return ("\U0001f534 Pre-Dispute queue \u2014 CLAIM FAILED\n"
                f"   http {obj.get('http_status')} \u00b7 backend {obj.get('backend_base')} (reachable={obj.get('backend_base_reachable')})\n"
                f"   {str(obj.get('detail'))[:200]}")
    if s == "error":
        return f"\U0001f534 Pre-Dispute worker \u2014 {obj.get('reason')}"
    return ""


def main() -> int:
    quiet = "--quiet" in sys.argv
    force = "--force" in sys.argv

    def emit(obj: dict, always: bool = False) -> None:
        if quiet:
            line = human(obj)
            if line:
                print(line)
            return
        print(json.dumps(obj, indent=2))

    env = load_env()
    key_name, key = agent_key(env)
    if not key:
        emit({"status": "error", "reason": f"{KEY_NAMES[0]} missing from Hermes env"}, always=True)
        return 0

    held = open_claim()
    if held and not force:
        emit({"status": "busy", "job_id": held.get("job", {}).get("job_id"), "claimed_at": held.get("claimed_at")})
        return 0

    base, base_ok = resolve_backend(env)
    worker_run_id = "mercury-predispute-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    status, body = post(base + CLAIM_PATH, {"worker_run_id": worker_run_id}, {"X-Hermes-Agent-Key": key})

    if status == 204:
        emit({"status": "no_work", "checked_at": datetime.now(timezone.utc).isoformat(), "backend_base_usable": base})
        return 0
    if status != 200:
        # 401 / 5xx / unreachable: report and stop. Never research or complete on a bad claim.
        emit({"status": "claim_failed", "http_status": status, "detail": body, "backend_base": base, "backend_base_reachable": base_ok, "worker_run_id": worker_run_id}, always=True)
        return 0

    job = json.loads(body)
    acma_base, acma_ok = resolve_acma_base(env)
    now = datetime.now(timezone.utc)
    record = {
        "status": "job_claimed",
        "claimed_at": now.isoformat(),
        "last_heartbeat_at": now.isoformat(),
        "lease_expires_at": job.get("lease_expires_at"),
        "backend_base": base,
        "worker_run_id": worker_run_id,
        "key_name": key_name,
        "job": job,
        "acma_base_usable": acma_base,
        "acma_reachable_from_wsl": acma_ok,
        "note": "submit acma_expires_at as null; heartbeat every ~4 min (lease = 10 min)",
    }
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(record, indent=2))
    emit({"status": "job_claimed", "job_id": job.get("job_id"), "merchant_name": job.get("merchant_name"), "abn": job.get("abn"), "origin_case_id": job.get("origin_case_id"), "worker_run_id": worker_run_id, "lease_expires_at": job.get("lease_expires_at"), "state_file": str(STATE_FILE)}, always=True)
    return 10


if __name__ == "__main__":
    sys.exit(main())
