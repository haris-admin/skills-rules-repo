#!/usr/bin/env python3
"""Push cost (and optionally renewal/entity) updates into the Notion CMDB — idempotent, verified.

Usage:
  cmdb_cost_write.py updates.json [--dry-run]

updates.json:
  { "AWS environment — AMLHive": {"monthlyCost": 0},
    "Xero accounting subscription — AMLHive": {"monthlyCost": 45, "renewalDate": "2027-03-01"} }

Rules honoured:
  * Only writes fields present in the input — never invents a value.
  * Matches rows on the asset NAME (stable business key), never a timestamp.
  * Skips rows already at the target value (idempotent — safe to re-run).
  * Reads every change back and reports the persisted value.
  * Never writes secret VALUES — only numbers/dates.
"""
import json
import sys
import time
import urllib.request
import urllib.error

ENV = "/mnt/c/Users/habib/.hermes/.env"
DSI = "40638825-121a-48f6-8f95-d2bf11fffb15"


def load_token():
    for line in open(ENV, "rb").read().decode("utf-8", "replace").splitlines():
        line = line.strip().lstrip("\ufeff")
        if line.startswith("NOTION_TOKEN_WS") and "=" in line:
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("NOTION_TOKEN_WS not found")


TOK = load_token()


def call(path, method="GET", body=None):
    req = urllib.request.Request("https://api.notion.com" + path, method=method)
    req.add_header("Authorization", "Bearer " + TOK)
    req.add_header("Notion-Version", "2025-09-03")
    if body is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(body).encode()
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(1.5); continue
            return e.code, e.read().decode()[:300]
        except Exception as e:
            return None, str(e)[:300]
    return None, "retries exhausted"


def fetch_rows():
    rows, cursor = [], None
    while True:
        b = {"page_size": 100}
        if cursor:
            b["start_cursor"] = cursor
        st, r = call(f"/v1/data_sources/{DSI}/query", "POST", b)
        if not isinstance(r, dict) or "results" not in r:
            raise SystemExit(f"query failed: {st} {r}")
        rows += r["results"]
        if not r.get("has_more"):
            break
        cursor = r.get("next_cursor")
    return rows


def title_of(p):
    for v in (p.get("properties") or {}).values():
        if v.get("type") == "title":
            return "".join(x.get("plain_text", "") for x in (v.get("title") or []))
    return ""


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    updates = json.load(open(sys.argv[1]))
    dry = "--dry-run" in sys.argv

    rows = {title_of(p): p for p in fetch_rows()}
    print(f"CMDB rows loaded: {len(rows)}   |   updates supplied: {len(updates)}"
          f"{'   [DRY RUN]' if dry else ''}\n")

    changed = skipped = missing = failed = 0
    for name, fields in updates.items():
        p = rows.get(name)
        if not p:
            print(f"  ⚠️  NO ROW  {name[:64]}")
            missing += 1
            continue
        props = p.get("properties") or {}
        payload = {}
        unchanged = []
        for f, val in fields.items():
            if f == "monthlyCost":
                cur = (props.get("Monthly Cost") or {}).get("number")
                if cur == val:
                    unchanged.append(f); continue
                payload["Monthly Cost"] = {"number": val}
            elif f == "renewalDate":
                cur = ((props.get("Renewal Date") or {}).get("date") or {}).get("start")
                if cur == val:
                    unchanged.append(f); continue
                payload["Renewal Date"] = {"date": {"start": val}} if val else {"date": None}
            else:
                print(f"  ⚠️  unknown field '{f}' for {name[:50]} — ignored")
        if not payload:
            print(f"  =  no change  {name[:60]}  ({', '.join(unchanged) or 'nothing to do'})")
            skipped += 1
            continue
        if dry:
            print(f"  →  WOULD SET  {name[:58]}  {payload}")
            changed += 1
            continue
        st, r = call(f"/v1/pages/{p['id']}", "PATCH", {"properties": payload})
        if st != 200:
            print(f"  🔴 FAILED    {name[:58]}  HTTP {st} {str(r)[:110]}")
            failed += 1
            continue
        # read back
        st2, rb = call(f"/v1/pages/{p['id']}")
        got = {}
        rp = (rb or {}).get("properties") or {}
        if "Monthly Cost" in payload:
            got["monthlyCost"] = (rp.get("Monthly Cost") or {}).get("number")
        if "Renewal Date" in payload:
            got["renewalDate"] = ((rp.get("Renewal Date") or {}).get("date") or {}).get("start")
        ok = all(got.get(k) == fields[k] for k in got)
        print(f"  {'✅' if ok else '⚠️ '} SET        {name[:58]}  {got}")
        changed += 1 if ok else 0
        failed += 0 if ok else 1
        time.sleep(0.35)

    print(f"\nchanged={changed}  unchanged={skipped}  missing_row={missing}  failed={failed}")


if __name__ == "__main__":
    main()
