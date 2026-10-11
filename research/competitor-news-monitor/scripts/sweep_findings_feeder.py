#!/usr/bin/env python3
"""File AMLHive weekly competitor-sweep findings into the MemPalace `fintech-aml` chamber.

Usage:
    env -u PYTHONPATH ~/.hermes/venv/bin/python3 \
        ~/.hermes/scripts/amlhive_competitor_sweep_feed.py <findings.json>

The findings JSON is produced by the sweep run and carries:
    {"id_prefix": "compl_sweep_YYYYMMDD", "topic": "...", "findings": [ {title, content, confidence, url}, ... ]}

Why this exists (see skill competitor-news-monitor, pitfall 1 & 2):
  * The markdown/file leg and the vector leg are INDEPENDENT pipelines — a sweep that
    only writes a report feeds nothing to retrieval.
  * chromadb 1.5.9 lives in ~/.hermes/venv (py3.13); the Hermes install venv (3.14) has
    no chromadb and the cron scheduler deliberately sets no PYTHONPATH, so run this with
    `env -u PYTHONPATH ~/.hermes/venv/bin/python3` (the `-u` matters: a foreign PYTHONPATH
    shadows the venv's compiled pydantic_core and import chromadb dies).
  * A bare timestamp id collides when several findings land in the same second and Chroma
    SILENTLY overwrites — always pass a stable per-batch id_prefix.
The chamber count is read back before -> after and the delta asserted, so a silent
no-op or partial clobber fails loudly instead of reporting success.
"""
import json
import os
import sys
from pathlib import Path

# ── env guard (mirror of sc_watch_to_mempalace.py) ───────────────────────────
_ver = f"python{sys.version_info.major}.{sys.version_info.minor}"
_pp = os.environ.get("PYTHONPATH")
if _pp and "site-packages" in _pp:
    os.environ["PYTHONPATH"] = os.pathsep.join(
        p for p in _pp.split(os.pathsep) if p and "site-packages" not in p)
sys.path[:] = [p for p in sys.path if not ("site-packages" in p and _ver not in p)]
_vpy = "/home/habib/.hermes/venv/bin/python3"
if os.path.exists(_vpy) and os.path.realpath(sys.executable) != os.path.realpath(_vpy):
    os.execv(_vpy, [_vpy, os.path.abspath(__file__), *sys.argv[1:]])

sys.path.insert(0, os.path.expanduser("~/.hermes/scripts"))
import chromadb  # noqa: E402
from chromadb.config import Settings  # noqa: E402
from pluto_mempalace_feeder import CHROMA_DB_PATH, feed_research  # noqa: E402

CHAMBER = "fintech-aml"


def chamber_count():
    client = chromadb.PersistentClient(
        path=CHROMA_DB_PATH, settings=Settings(anonymized_telemetry=False))
    return client.get_collection(CHAMBER).count()


def main():
    if len(sys.argv) < 2:
        print("usage: amlhive_competitor_sweep_feed.py <findings.json>", file=sys.stderr)
        return 2
    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    findings = payload.get("findings") or []
    prefix = payload.get("id_prefix")
    if not findings:
        print("nothing to feed (empty findings list)")
        return 0
    if not prefix:
        raise SystemExit("id_prefix is required — a bare timestamp id silently collides")

    before = chamber_count()
    r = feed_research(
        topic=payload.get("topic", "AMLHive weekly competitor sweep"),
        findings=findings,
        source=payload.get("source", "amlhive_competitor_sweep"),
        tags=payload.get("tags", ["amlhive", "competitor-sweep", "aml", "fintech"]),
        chamber=CHAMBER,
        id_prefix=prefix,
    )
    after = chamber_count()
    delta = after - before
    print(f"feed_research -> {r}")
    print(f"chamber '{CHAMBER}': {before} -> {after} (delta {delta}, expected {len(findings)})")
    if delta != len(findings):
        print(f"WARN: expected +{len(findings)}, got +{delta} — check id_prefix collisions",
              file=sys.stderr)
        return 1
    print(f"OK — {delta} finding(s) stored in MemPalace chamber \"{CHAMBER}\" (id prefix {prefix})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
