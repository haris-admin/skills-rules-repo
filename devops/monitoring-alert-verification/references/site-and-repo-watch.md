# Watching a site AND the code behind it

A "monitor this product" request rarely means only uptime. It means four layers, and they
fail independently:

| layer | question | signal |
|---|---|---|
| DNS/edge | does the name resolve and answer? | status + IPs, Cloudflare colo |
| product | is the app really there, or a parked shell? | content marker / `<title>` |
| API | is the backend healthy, and which build is serving? | `/health` JSON |
| code | does the repo I can see match what is live? | version manifest vs deployed version |

A green edge with a dead origin, or a healthy API serving a build that is not in your
checkout, both render as "all fine" under a status-code-only monitor.

## Build ONE config-driven engine, not one script per site

Sites arrive in batches (two or three at a time, one of which is not launched yet). A script
per domain makes the third site a code change; a config entry makes it a one-line change and
keeps the report shape identical across products.

`~/.hermes/data/site_monitor.json` shape:

```json
{"reporting_hours_aest": [7, 19],
 "sites": [{"key": "product", "label": "Product", "repo": "repo-slug",
            "hosts": [
              {"host": "x.com.au", "role": "main app", "marker": "product-name"},
              {"host": "www.x.com.au", "role": "main app", "marker": "product-name"},
              {"host": "www.x.com.au", "role": "www -> apex", "expect_redirect": true},
              {"host": "api.x.com.au", "role": "production API", "health": "/health",
               "health_expect": {"status": "healthy", "database": "ok"}},
              {"host": "api.x.com.au", "role": "production API", "planned": true,
               "health": "/health"}]}]}
```

Per-host check types, in order of evidential strength:

- **`health` (best)** — when the product exposes a JSON health route, assert on FIELDS, not on
  200: `status == healthy`, `database == ok`. Then print the identifying fields
  (`service`, `version`, `environment`, `database`) — that one line proves which build and
  which environment answered, which no content marker can. `status`/`database` mismatches are
  the only P0s; missing auxiliary keys are P1.
- **`marker`** — required on every CDN-fronted host (see the Cloudflare section of SKILL.md):
  a lowercased product string that must be in the body. Also print `<title>` so a deploy that
  serves the wrong product is visible at a glance.
- **`expect_redirect`** — `www` -> apex is *correct* behaviour; assert the 3xx/target rather
  than treating it as a page to marker-check.
- **`planned`** — no DNS yet: print "not yet live", raise nothing, and let the normal probe
  take over automatically when the name resolves. Three hosts (apex, `www`, `api`) per product
  is the default set; check all three before declaring a domain absent.

## Reporting cadence: digest at set hours, alert always

Run the engine 4x/day (`30 5,11,17,23 * * *`) and gate DELIVERY, not the check:

```bash
out=$("$PY" scripts/site_monitor.py 2>&1); rc=$?
hour=$(date +%-H)
# healthy + not a reporting slot -> exit 0 with NO output (watchdog silence)
[ $rc -eq 0 ] && ! echo ",$hours," | grep -q ",$hour," && exit 0
echo "$out"
```

So a healthy estate speaks twice a day and stays silent the other ticks, while anything
needing action speaks on the tick it happens. Capture rc BEFORE any pipe, and never judge the
monitor's status through `| head`.

## Repo -> product mapping: folder names lie

Before writing any code checker, resolve which repo actually backs the site:

1. `gh repo list <org> --limit 100 --json name,pushedAt,isPrivate` — the repo that was pushed
   today is almost always the one you are being asked about. Sort by `pushedAt`.
2. The local folder name a human created may be an EMPTY placeholder
   (`ideas-<product>/` with nothing in it) while the real code lives under a different slug
   (`ideas-ev-charging`). An empty directory means *not cloned*, never *code absent*.
3. Confirm by structure, not by name: `backend/` + `frontend/` + `packages/`, `pyproject.toml`
   and `package.json`, plus the last few commit subjects naming the product's domain nouns.
4. Reuse the credential already embedded in an existing clone's remote instead of hunting for
   a token: `git -C <clone> remote get-url origin`, extract with
   `re.search(r'//oauth2:([^@]+)@', url)`, pass as `GH_TOKEN` for the session, and never print
   it. Clone with the token inside the URL and scrub the URL from any echo.

## The version-drift check (the highest-value thing here)

Compare the repo's declared version against what the deployed API reports:

- read manifests (`backend/pyproject.toml` `^version = "x"`, `frontend/package.json`
  `"version": "x"`);
- fetch the health route and take its `version`;
- **mismatch is a finding, and its direction is the diagnosis**: repo manifest OLDER than
  deployed ⇒ the checkout cannot build what is live. Check
  `git rev-list --count HEAD..origin/<branch>` before calling it a release bug — a local clone
  hundreds of commits behind reproduces exactly this. Repo manifest NEWER than deployed ⇒
  something was committed and never shipped.
- Only a repo whose HEAD equals origin and whose tree is clean can prove a release bug.

## Other standing signals worth printing

- **`behind` / `ahead` vs `origin/<branch>`** after `git fetch --all --prune`, plus the new
  commits since the last run (watermark per repo in a small JSON state file). This is what
  makes the job useful rather than a periodic `git status`.
- **Dirty-file count.** A live site whose repo carries hundreds of uncommitted files is running
  code that is not in git — say so in that sentence; it changes how a deploy is read.
- **Fetch failure** is its own line (`⚠️ git fetch failed — upstream state unknown`), never
  silence: an unverifiable watch is a finding.
- **Exit semantics:** exit 2 (speak) on new commits, drift or fetch failure; exit 0 with EMPTY
  stdout when nothing moved. Keep `--force` for manual runs.

## Never mutate the repo you are monitoring

A production checkout with a dirty tree must not be auto-pulled by a watcher. Fetch is safe;
pull can conflict and destroy uncommitted work. Report the lag and offer: (a) pull and report
conflicts, (b) a read-only mirror clone in WSL for analysis, (c) the user commits/stashes
first. If you need the real HEAD for analysis, clone a mirror elsewhere and leave the working
tree alone.
