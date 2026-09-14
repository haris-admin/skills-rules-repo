#!/usr/bin/env python3
"""Probe the fleet Notion token from the Windows .env.

Usage:
  notion_probe.py [ENV_VAR] [--map|--recent]

  ENV_VAR default NOTION_TOKEN_WS (the working integration in this fleet).
  --map     also list data sources (databases) and task-like pages
  --recent  also list the most recently edited pages

Reads the token from /mnt/c/Users/habib/.hermes/.env and NEVER prints its value.
"""
import json
import sys
import urllib.request
import urllib.error

ENV = "/mnt/c/Users/habib/.hermes/.env"
VER = "2025-09-03"

args = [a for a in sys.argv[1:] if not a.startswith("--")]
flags = {a for a in sys.argv[1:] if a.startswith("--")}
WANT = args[0] if args else "NOTION_TOKEN_WS"

tok = None
for line in open(ENV, "rb").read().decode("utf-8", "replace").splitlines():
    line = line.strip().lstrip("\ufeff")
    if line.startswith(WANT + "="):
        tok = line.split("=", 1)[1].strip().strip('"').strip("'")
        break
print(f"var: {WANT} | present: {bool(tok)} | length: {len(tok) if tok else 0}")
if not tok:
    raise SystemExit(1)


def call(path, method="GET", body=None):
    req = urllib.request.Request("https://api.notion.com" + path, method=method)
    req.add_header("Authorization", "Bearer " + str(tok))
    req.add_header("Notion-Version", VER)
    if body is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(body).encode()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:250]
    except Exception as e:
        return None, str(e)[:250]


def title_of(o):
    try:
        if o.get("object") == "page":
            for v in (o.get("properties") or {}).values():
                if v.get("type") == "title":
                    return "".join(x.get("plain_text", "") for x in (v.get("title") or []))
            return (o.get("child_page") or {}).get("title", "")
        return "".join(x.get("plain_text", "") for x in (o.get("title") or []))
    except Exception:
        return ""


st, me = call("/v1/users/me")
print("users/me -> HTTP", st)
if isinstance(me, dict):
    print("  name:", me.get("name"), "| type:", me.get("type"),
          "| workspace:", me.get("bot", {}).get("workspace_name"))


def search_all(sort=None):
    items, cursor = [], None
    for _ in range(10):
        body = {"page_size": 100}
        if sort:
            body["sort"] = sort
        if cursor:
            body["start_cursor"] = cursor
        st, res = call("/v1/search", "POST", body)
        if not isinstance(res, dict) or "results" not in res:
            print("search failed:", st, res)
            break
        items += res["results"]
        if not res.get("has_more"):
            break
        cursor = res.get("next_cursor")
    return items


items = search_all()
print("search -> objects visible:", len(items))

dss = [o for o in items if o.get("object") == "data_source"]
pages = [o for o in items if o.get("object") == "page"]
print(f"  data_sources: {len(dss)} | pages: {len(pages)}")

if "--map" in flags:
    print("\n=== DATA SOURCES (databases) ===")
    for o in dss:
        print(f"  {o.get('id')} :: {title_of(o)}")
    kw = ("task", "todo", "action", "backlog", "kanban", "checklist", "follow")
    print("\n=== TASK-LIKE PAGES ===")
    for o in pages:
        t = title_of(o)
        if any(k in t.lower() for k in kw):
            print(f"  {o.get('id')} :: {t[:90]}")

if "--recent" in flags:
    recent = search_all({"direction": "descending", "timestamp": "last_edited_time"})
    rp = sorted([o for o in recent if o.get("object") == "page"],
                key=lambda o: o.get("last_edited_time") or "", reverse=True)
    print("\n=== 20 MOST RECENTLY EDITED PAGES ===")
    for o in rp[:20]:
        print(f"  {(o.get('last_edited_time') or '')[:16]}  {o.get('id')}  {title_of(o)[:80]}")
