#!/usr/bin/env python3
"""Free Alexandria discovery sweep — enumerate provider/capability contracts, spend nothing.

Alexandria discovery is free (`creditsUsed: 0`); only executing a provider tool bills. Use this
before any paid call so you query the catalogue instead of guessing at provider or option names.

Never prints the API key. Reports the credit balance before and after so the run's cost is provable.

Usage:
  python3 alexandria_discover.py                       # built-in vertical sweep
  python3 alexandria_discover.py "query" ["query2" ...] # your own queries
  python3 alexandria_discover.py --json out.json "query"
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys
import time
import urllib.error
import urllib.request

ENV_CANDIDATES = [
    "/mnt/c/Users/habib/.hermes/.env",
    "/home/habib/.hermes/.env",
]
SEARCH_URL = "https://api.firecrawl.dev/v2/search"
CREDITS_URL = "https://api.firecrawl.dev/v2/team/credit-usage"

DEFAULT_QUERIES = [
    "Australian company register ASIC business number ABN lookup",
    "business entity due diligence insolvency litigation records",
    "financial statements company filings data",
    "people enrichment contact finder email",
    "podcast transcripts and video transcripts",
    "government regulations legislation and compliance data",
    "real estate property listings",
]


def api_key() -> str:
    for cand in ENV_CANDIDATES:
        p = pathlib.Path(cand)
        if not p.exists():
            continue
        for line in p.read_bytes().decode("utf-8-sig", errors="replace").splitlines():
            s = line.strip()
            if s.startswith("FIRECRAWL_API_KEY="):
                return s.split("=", 1)[1].strip()
    return ""


def call(url: str, key: str, payload=None, timeout: int = 60):
    try:
        req = urllib.request.Request(
            url,
            method="POST" if payload is not None else "GET",
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode(errors="replace"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:300]
    except Exception as e:  # network/transport — report, do not crash the sweep
        return "ERR", f"{type(e).__name__}"


def credits(key: str) -> str:
    s, b = call(CREDITS_URL, key)
    if isinstance(b, dict):
        d = b.get("data", {}).get("remainingCredits", b.get("remaining_credits"))
        return str(d)
    return f"unavailable ({s})"


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out_json = None
    if "--json" in sys.argv:
        i = sys.argv.index("--json")
        if i + 1 < len(sys.argv):
            out_json = sys.argv[i + 1]
            args = [a for a in args if a != out_json]
    queries = args or DEFAULT_QUERIES

    key = api_key()
    if not key:
        print("FIRECRAWL_API_KEY is not set in either .env candidate — nothing to do.")
        return 2

    before = credits(key)
    print(f"FIRECRAWL_API_KEY: set ({len(key)} chars) | credits before: {before}")

    catalogue: dict[str, set[str]] = collections.defaultdict(set)
    descriptions: dict[str, str] = {}
    for q in queries:
        s, b = call(SEARCH_URL, key, {"query": q, "sources": ["alexandria"], "limit": 40})
        tools = ((b.get("data") or {}).get("tools") or []) if isinstance(b, dict) else []
        for t in tools:
            p, c = t.get("provider"), t.get("capability")
            if not p or not c:
                continue
            catalogue[p].add(c)
            descriptions.setdefault(f"{p}/{c}", t.get("description", ""))
        print(f"  [{s}] {q[:58]:58s} -> {len(tools)} tool contract(s)")
        if s == 403:
            print("  (403 = the team's Alexandria access is not enabled)")
        time.sleep(1.5)  # the plan's rate limit trips on fast back-to-back sweeps

    print(f"\n{len(catalogue)} provider(s), {sum(len(v) for v in catalogue.values())} capability(ies):")
    for p in sorted(catalogue):
        caps = sorted(catalogue[p])
        print(f"  {p:34s} ({len(caps)}): {', '.join(caps[:8])}{' ...' if len(caps) > 8 else ''}")

    print(f"\ncredits after: {credits(key)}  (discovery itself is free)")
    print("next: execute with POST /v2/scrape {\"alexandria\":{provider, capability, options}}")

    if out_json:
        payload = {
            "providers": {p: sorted(c) for p, c in catalogue.items()},
            "contracts": descriptions,
        }
        pathlib.Path(out_json).write_text(json.dumps(payload, indent=1))
        print(f"saved: {out_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
