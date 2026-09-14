#!/usr/bin/env python3
"""AWS Cost → Notion CMDB sync.

Pulls AWS Cost Explorer for BOTH fleet accounts and writes the cost into the Notion CMDB.

Accounts:
  AMLHive  560205084533  creds AWS_*_AMLHIVE   (IAM_MONITOR)
  Tapease  707843605914  creds AWS_*_TAPEASE   (IAM_GRAFANA)

CRITICAL: AMLHive's usage is 100% offset by an AWS credits pool. UnblendedCost therefore
reads ~$0.00 — a false zero. This script filters RECORD_TYPE (Credit/Refund/Tax) OUT so it
records the GROSS usage cost, i.e. what the account actually consumes, and notes the offset.

Writes Monthly Cost = gross usage for the last complete calendar month.
Idempotent: re-running with unchanged AWS data makes no writes.
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import date, timedelta

ENV = "/mnt/c/Users/habib/.hermes/.env"
DSI = "40638825-121a-48f6-8f95-d2bf11fffb15"

vals = {}
for line in open(ENV, "rb").read().decode("utf-8", "replace").splitlines():
    line = line.strip().lstrip("\ufeff")
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        vals[k.strip()] = v.strip().strip('"').strip("'")

TOK = vals.get("NOTION_TOKEN_WS")
NO_CREDIT = json.dumps({"Not": {"Dimensions": {"Key": "RECORD_TYPE",
                                               "Values": ["Credit", "Refund", "Tax"]}}})
BASE = {k: v for k, v in os.environ.items() if not k.startswith("AWS_")}
BASE["AWS_PAGER"] = ""
BASE["AWS_DEFAULT_REGION"] = "us-east-1"

ACCOUNTS = [
    {"label": "AMLHive", "prefix": "AMLHIVE", "row": "AWS environment — AMLHive",
     "credits": True},
    {"label": "Tapease", "prefix": "TAPEASE", "row": "AWS environment — Tapease",
     "credits": False},
]


def aws(args, e):
    r = subprocess.run(["aws"] + args, capture_output=True, text=True, env=e, timeout=120)
    return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()


def aws_env(prefix):
    e = dict(BASE)
    e["AWS_ACCESS_KEY_ID"] = vals.get(f"AWS_ACCESS_KEY_ID_{prefix}")
    e["AWS_SECRET_ACCESS_KEY"] = vals.get(f"AWS_SECRET_ACCESS_KEY_{prefix}")
    return e


def ce_total(e, start, end, extra=None):
    args = ["ce", "get-cost-and-usage", "--time-period", f"Start={start},End={end}",
            "--granularity", "MONTHLY", "--metrics", "UnblendedCost",
            "--filter", NO_CREDIT, "--output", "json"]
    rc, out, err = aws(args, e)
    if rc != 0:
        return None, err[:160]
    try:
        return float(json.loads(out)["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"]), None
    except Exception as ex:
        return None, str(ex)[:160]


def ce_services(e, start, end, n=6):
    rc, out, err = aws(["ce", "get-cost-and-usage", "--time-period", f"Start={start},End={end}",
                        "--granularity", "MONTHLY", "--metrics", "UnblendedCost",
                        "--filter", NO_CREDIT,
                        "--group-by", "Type=DIMENSION,Key=SERVICE", "--output", "json"], e)
    if rc != 0:
        return []
    gs = sorted(json.loads(out)["ResultsByTime"][0]["Groups"],
                key=lambda g: -float(g["Metrics"]["UnblendedCost"]["Amount"]))
    return [(float(g["Metrics"]["UnblendedCost"]["Amount"]), g["Keys"][0]) for g in gs[:n]
            if float(g["Metrics"]["UnblendedCost"]["Amount"]) > 0.005]


def credit_offset(e, start, end):
    """How much the credit pool absorbed in the window."""
    rc, out, err = aws(["ce", "get-cost-and-usage", "--time-period", f"Start={start},End={end}",
                        "--granularity", "MONTHLY", "--metrics", "UnblendedCost",
                        "--group-by", "Type=DIMENSION,Key=RECORD_TYPE", "--output", "json"], e)
    if rc != 0:
        return None
    for g in json.loads(out)["ResultsByTime"][0]["Groups"]:
        if g["Keys"][0] == "Credit":
            return abs(float(g["Metrics"]["UnblendedCost"]["Amount"]))
    return 0.0


# ---------- Notion helpers ----------
def ncall(path, method="GET", body=None):
    req = urllib.request.Request("https://api.notion.com" + path, method=method)
    req.add_header("Authorization", "Bearer " + str(TOK))
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
    return None, "retries"


def rows_by_name():
    rows, cursor = {}, None
    while True:
        b = {"page_size": 100}
        if cursor:
            b["start_cursor"] = cursor
        st, r = ncall(f"/v1/data_sources/{DSI}/query", "POST", b)
        if not isinstance(r, dict) or "results" not in r:
            raise SystemExit(f"notion query failed {st} {r}")
        for p in r["results"]:
            for v in (p.get("properties") or {}).values():
                if v.get("type") == "title":
                    rows["".join(x.get("plain_text", "") for x in (v.get("title") or []))] = p
                    break
        if not r.get("has_more"):
            break
        cursor = r.get("next_cursor")
    return rows


def main():
    apply = "--dry-run" not in sys.argv
    today = date.today()
    first_this = today.replace(day=1)
    lm_end = first_this - timedelta(days=1)
    lm_start = lm_end.replace(day=1)

    rows = rows_by_name()
    print(f"Notion CMDB rows: {len(rows)}   window(last full month): {lm_start}→{lm_end}")
    print(f"mode: {'APPLY' if apply else 'DRY RUN'}\n")

    for acc in ACCOUNTS:
        e = aws_env(acc["prefix"])
        print("=" * 76)
        print(f"{acc['label']}  account {vals.get('AWS_ACCOUNT_ID_' + acc['prefix'])}")

        rc, arn, err = aws(["sts", "get-caller-identity", "--query", "Arn", "--output", "text"], e)
        if rc != 0:
            print(f"  🔴 auth failed: {err[:140]}")
            continue
        print(f"  identity: {arn}")

        lm, e1 = ce_total(e, lm_start, first_this)
        mtd, e2 = ce_total(e, first_this, today + timedelta(days=1))
        if lm is None:
            print(f"  🔴 cost query failed: {e1}")
            continue
        svcs = ce_services(e, lm_start, first_this)
        print(f"  GROSS usage last month : ${lm:.2f}")
        print(f"  GROSS usage MTD        : ${mtd:.2f}" if mtd is not None else "  MTD: n/a")
        for a, s in svcs:
            print(f"      {a:8.2f}  {s}")

        offset = credit_offset(e, lm_start, first_this) if acc["credits"] else None
        if offset:
            print(f"  credit offset          : -${offset:.2f}  →  net cash ${lm - offset:.2f}")

        # notes
        note = (f"AWS {acc['label']} account {vals.get('AWS_ACCOUNT_ID_' + acc['prefix'])}. "
                f"Region ap-southeast-2 primary. GROSS usage last full month "
                f"({lm_start}→{lm_end}): ${lm:.2f}; month-to-date ${mtd:.2f}. "
                if mtd is not None else
                f"AWS {acc['label']} account. GROSS usage last full month: ${lm:.2f}. ")
        if svcs:
            note += "Top services: " + ", ".join(f"{s} ${a:.2f}" for a, s in svcs) + ". "
        if offset:
            note += (f"FULLY OFFSET by AWS credits: -${offset:.2f} in the same month, so the "
                     f"account's CASH cost is $0 while it consumes ${lm:.2f}/month. "
                     f"UnblendedCost reads ~$0 — a false zero; always read gross usage "
                     f"(RECORD_TYPE Credit/Refund/Tax filtered out). ")
        note += ("Monthly Cost field records the GROSS usage (true consumption). "
                 "Auto-maintained by aws_cost_sync.py.")

        p = rows.get(acc["row"])
        if not p:
            print(f"  ⚠️  no Notion row named '{acc['row']}' — create it first")
            continue
        props = p.get("properties") or {}
        cur = (props.get("Monthly Cost") or {}).get("number")
        target = round(lm, 2)
        if cur == target:
            print(f"  =  Notion already at ${target:.2f} — no change")
        elif not apply:
            print(f"  →  WOULD SET Monthly Cost ${cur} → ${target:.2f}")
        else:
            st, r = ncall(f"/v1/pages/{p['id']}", "PATCH",
                          {"properties": {"Monthly Cost": {"number": target},
                                          "Notes": {"rich_text": [{"text": {"content": note}}]}}})
            if st == 200:
                st2, rb = ncall(f"/v1/pages/{p['id']}")
                got = ((rb or {}).get("properties", {}).get("Monthly Cost") or {}).get("number")
                print(f"  ✅ SET Monthly Cost → ${got} (read back)")
            else:
                print(f"  🔴 PATCH failed HTTP {st} {str(r)[:140]}")
        time.sleep(0.4)


if __name__ == "__main__":
    main()
