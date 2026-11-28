---
name: amlhive-weekly-security-scan
description: "Use when running the AML Hive Friday security scan."
version: 1.0.0
author: Pluto / Haris
tags: [pluto, amlhive, security, cron, read-only]
---

# AML Hive weekly security scan (read-only code audit)

Friday 17:00 Australia/Sydney, Hermes cron `aa2d2c4aef66`. The authoritative procedure is the
"Weekly Security Scan" section of the `pluto-amlhive-operating-contract` skill — this skill records
the execution mechanics and the traps that cost re-discovery time.

## Preconditions

- **Run step 1 in the dev worktree, not the shared checkout.** `dev` lives at `~/code/amlhive1-dev`;
  `~/code/amlhive1` is on the `pluto_pr` lane. Running the contract's
  `git fetch origin dev && git checkout dev && git reset --hard origin/dev` in the shared checkout
  prints `fatal: 'dev' is already used by worktree` for the checkout — and because that command is
  piped through `tail`, the `&&` chain still runs `git reset --hard origin/dev` **on `pluto_pr`**,
  moving the lane branch. Correct form:

  ```bash
  cd ~/code/amlhive1-dev && git fetch origin dev && git reset --hard origin/dev
  ```

  Check `git status --porcelain` first; a dirty dev worktree means another agent is mid-task.
- **The dev worktree has no `backend/.venv`** (only `~/code/amlhive1` has one, and it does not contain
  skillspector). Run skillspector from `~/.local/bin/skillspector`.
- **AWS: AML Hive is account `560205084533`** (`AWS_ACCESS_KEY_ID_AMLHIVE` /
  `AWS_SECRET_ACCESS_KEY_AMLHIVE` in `/mnt/c/Users/habib/.hermes/.env`). The ambient `~/.aws` default
  profile is **Tapease** (`707843605914`). An IAM question answered under ambient creds silently
  answers about the wrong account — `get-user amlhive-github-actions` returns `NoSuchEntity` there
  while the user is alive and keyed in the AML Hive account. Exporting the creds in a shell is blocked
  by the terminal scanner and `boto3` is not installed in the system python, so have a python helper
  read the env file, write a temp credentials file (`0600`, deleted at the end) and point the CLI at it:
  `AWS_SHARED_CREDENTIALS_FILE=<scratch>/amlhive_creds AWS_PROFILE=amlhive aws …` — values are never
  printed, only the command output is.
- **GitHub API:** use `Bearer <token>` (see the `github-auth` skill — bare `oauth2:` is 401). `gh`
  CLI is not logged in on this host, so drive the REST API directly with
  `GITHUB_PAT_CLASSIC_AMLHIVE_AGENT` (only that PAT can read `amlhive-tech/amlhive1`).

## Running the three steps

```bash
# 1. dev checkout — see precondition above
# 2. skillspector over every skill (v2.11+ is ~4s/skill; 56 skills ~4 min)
for d in .claude/skills/*/; do
  n=$(basename "$d"); skillspector scan "$d" --no-llm > "/tmp/ssp/$n.txt" 2>/dev/null
done
# 3. the 7-day window
git log --since="7 days ago" --oneline -- backend/app frontend/app frontend/lib infra .github | cat
```

For the diff review, grep the window's patch for the rule classes instead of reading every commit:
swallowed exceptions (`except[^:]*:\s*$` followed by `pass`), new `@router` decorators, `f"SELECT`,
`os.system|eval(|exec(|pickle.loads`, `agency_id` not sourced from `current_user`, and hardcoded
current-state literals (`docs/agent_rules/no-hardcoded-current-state-literals.md`). Every hit must be
opened in context before it is reported — the f-string SQL that looks alarming is usually built from
a closed literal map, and the `except: pass` is usually around a best-effort side effect — but a
`pass` in a *security* path (GUC reset, forensic writer, audit insert) is a real finding.

**The auth census must resolve dependencies transitively, not by whitelist.** A regex over
`@router` decorators plus signature lines reports ~265 of 268 routes as unauthenticated, because
most handlers put `Depends(...)` on multi-line signatures and use local wrappers
(`c531_admin_reader`, `require_copy_admin`, `verify_internal_key`, `get_current_partner`). Parse with
`ast`, collect every `Depends(x)` per handler, then close over locally defined dependency functions
until they reach a real primitive (`get_current_user`, `get_current_admin`, `verify_internal_key`,
`get_current_partner`). That gives ~26 remaining, of which the public/token-authenticated ones are
all documented in the module docstring — open each before reporting.

**Decorator-level and router-level `dependencies=[...]` are invisible to a signature-only parse — and
that is the biggest false-positive trap in this step.** `@router.post("/sync/{dataset}",
 dependencies=[Depends(verify_internal_key)])` declares auth in the *decorator*, and
`APIRouter(dependencies=[Depends(require_plan("starter"))])` declares it at *router* construction.
A parser that reads only function parameters reported **55** "unauthenticated" routes on 13 Nov 2026
with four of them being the bearer-protected internal endpoints. Also add the wrapper primitives that
live outside `app/api/` (so no local `def` exists to close over): `require_admin_only`,
`require_agent_or_principal`, `require_principal_or_auditor`, `require_plan`, `log_auditor_read`,
`require_blog_read_access`, `get_current_admin`, `get_current_partner`. With decorator + router deps
and the full primitive set the true count is ~29 on 419 routes. Always state the number you got and
open every remainder; do not report a count you have not classified.

**Release branches are a CHAIN, not forks of dev — `dev...branch` badly overstates the diff.**
`git diff dev...origin/release/be-v0-50-209` showed 288 files / 53,567 insertions, but almost none of
that is new code: each release branch is cut from the *previous release*, so the merge-base with dev
is ancient. Diff **consecutive releases** instead (`be-208...be-209`), which gave the true figures
(14 files / 3,347 lines, 0 new routes). Report the cumulative `be-20X→be-20Y` app-code delta rather
than a `dev...` number, or the weekly log will look like 50k unreviewed lines every week.

**A renamed security helper is not a removed one.** On 13 Nov 2026 a name-only grep for `_is_ssrf_url`
in `webhook_worker.py` returned nothing and looked like the delivery-time SSRF re-check had been
deleted; it had been refactored to `get_vetted_public_ip` / `_post_pinned`. Before recording a
"regression" in a control, grep the *behaviour* (the comment, the private-IP check, the call site),
not just the old symbol name.

**Check for unredacted third-party documents, not just secrets.** Secret scanning does not catch a
counterparty's Letter of Intent committed as an image. On 13 Nov 2026 `docs/startmate-output/` held
three fully legible LOI PNGs (company, ABN, address, direct phone/email, officer signature) sitting
beside `loi_blurred_*` twins — proof the need to redact was known and did not stop the commit. Scan
for it: `git ls-files | grep -iE 'loi|startmate|contract|agreement'` and compare against blurred
variants. Visually confirm with vision before reporting; the repo being private lowers but does not
remove the severity, because git history is permanent.

**Email-HTML escaping has two template families, not one.** `email_template_service` escaped by
`html.escape` in C491 (issue-344, Resolved) — but `cdd_email_service` has its own `_wrapper` and
`_info_row`, imports no `html`, and is a live Postmark send path from `calendar_worker`. After any
claimed escaping fix, grep for the *other* row/wrapper helpers (`_info_row`, `<td …>{value}</td>`),
not just for callers of `render_email_template`; an issue marked Resolved is not proof the class is
closed.

**When `dev` is idle, the code that ships lives on `release/*` branches.** Releases are cut on isolated
branches (`origin/release/be-*`, `origin/release/fe-*`) and both deploy workflows are `workflow_dispatch`
that build from the dispatched ref's HEAD, so `dev` can sit for a week with **zero** commits while
production advances several versions. A zero-commit window is therefore not "nothing shipped":
`git for-each-ref --sort=-committerdate --format='%(committerdate:short) %(refname:short)' refs/remotes/origin | head`,
then run the same rule-class greps over `git diff dev...<branch> | grep -E '^\+'` for every branch whose
head falls inside the window, and record the zero-commit dev window explicitly instead of reading it as
clean. Report the resulting coverage gap as a finding about the scan's own diff base.

**The `/cso` pass must audit the whole checkout, not only the 7-day window.** The diff review finds
what changed; `/cso` Phases 1–7 are what find the long-standing defect that nobody touched this week
(e.g. a tenant-facing route from months ago still guarded by a `# Placeholder for admin role`
dependency). Both passes are required, and a finding from the static pass is reported as "surfaced
this week", not "introduced this week" — check `git log -1 --format=%h %ad` on the offending file so
the log states which it is.

## Reading skillspector output honestly

All skillspector findings are labelled `<CODE> - <name>`; the codes, not the 0–100 score, are the
finding. **v2.11.0 scores `AE1 / reference_unresolved` (unresolvable local path references) into the
score**, so a skill can read `100/100 CRITICAL DO NOT INSTALL` on documentation hygiene alone. The
scores are therefore **not comparable to the v2.3.5 baseline** in
`.claude/skills/skill-audit/SKILL.md`, and the documented binary path there
(`./backend/.venv/bin/skillspector`) no longer exists.

- Treat `AE1/reference_unresolved` and `AS3/SkillEnumeration` as documentation noise, not
  vulnerabilities; report them once, as a hygiene count.
- Classify the rest by quoting the line: `PE3`/`TM1`/`AR3`/`MP3`/`RA1` hits in security checklists,
  runbooks and strategy docs are text false positives (a credential-scoping checklist item, a
  documented SSM command, a rhetorical question). `RA1` in `skill-creator` is accepted by design.
- Report the scanner version and the finding-code tally, so next week's run is comparable.
- `skillspector scan --recursive` enforces a **32-skill budget** ("54 recursive skill(s) omitted"), so
  the "scan all skills" command in `skill-audit/SKILL.md` cannot cover 87 skills. Use the plain
  per-skill loop — 87 skills took ~4 minutes and completed.
- **Budget ~1 min/skill, not 4 s, and cap every scan.** On 27 Nov 2026 a sequential 87-skill loop ran
  ~1 min per skill (an hour total) and stalled part-way through `building-an-exo`; a 4-worker parallel
  loop with `timeout 300` per skill finished the remaining 61 in ~15 min. Wrap each scan as
  `timeout 300 skillspector scan "$d" --no-llm`, run 4 in parallel, and **verify coverage by set
  difference** (`for d in */; do grep -q "^${d%/}\t" index.tsv || echo MISSING $d; done`) — one skill
  (`cloudflare-worker-deploy`) silently produced no index row in the parallel pass and had to be
  re-scanned. Never report "all skills scanned" from a line count alone.
- Two skills score CRITICAL every week on prose alone: `building-an-exo` (100) and
  `handling-sensitive-data` (81). Quote the exact lines again rather than asserting "same as last
  week" — the line numbers are stable (`<repo>/.claude/skills/building-an-exo/references/shape-form.md:123`
  rhetorical question,
  `<repo>/.claude/skills/building-an-exo/templates/agent-specification.md:68` scoping-checklist row,
  `<repo>/.claude/skills/handling-sensitive-data/SKILL.md:144` documented SSM runbook,
  `handling-sensitive-data/scripts/rotate_postgres_role_password.sh` `PE2` on the safe
  `PGPASSWORD="$(cat "$FILE")"` pattern).

## Order of work — write the log BEFORE optional depth

On 6 Nov 2026 the run hit its tool-call ceiling during step 3 (skillspector) and **never appended the
log**, so the log read "newest 30 Oct" while the scan had actually run. Nothing was lost only because
the cron output file survived at `cron/output/aa2d2c4aef66/<date>.md`. Sequence the run so the
irreplaceable steps finish first: refresh → diff + rule-class sweep → the three live rechecks →
**append the log** → then any optional widening (full 87-skill scan, release-branch deltas). If the
ceiling is hit after the log is written, the run is still recorded.

## Two standing cloud checks that are easy to mistake for "no data"

Both are one HTTP call each and both have produced real findings; neither appears in the provider UI
without looking for it.

- **Dependabot alerts may be disabled, which reads as an auth error.**
  `GET /repos/amlhive-tech/amlhive1/dependabot/alerts?state=open` returned **403 "Dependabot alerts are
  disabled for this repository"** on 27 Nov 2026 while the same PAT happily read environments and
  branch protection — so the 403 is a *configuration* fact, not a token-scope artifact. Confirm by
  making one other authenticated call with the same token before writing it off. Disabled alerts mean
  the only CVE signal is a human noticing; report it as a MEDIUM hygiene finding and say what it
  would have caught (that week: a hand-applied dnspython 2.9.0 → 2.9.2 fix for CVE-2026-128089).
- **Environment protection cannot be switched on at the current GitHub plan.**
  `GET /repos/{owner}/{repo}/branches/{main,dev}/protection` returns **403 "Upgrade to GitHub Pro or
  make this repository public to enable this feature"**. That is the *reason* all six deployment
  environments report `protection_rules: 0`, so the remediation is a plan decision or a written
  accepted-risk record plus fixing the Terraform assertion that claims the gate exists — never a
  "settings toggle" instruction.

## `dev` is not where the shipped code lives — verify findings against the release tree

A clean `dev` window proves nothing about production. On 27 Nov 2026 `dev` had **one** lockfile commit
while production served `0.50.224` and dev's manifests said `0.50.185`, with the two lines diverged at
`2560bf287` (23 Oct) — 2,787 commits on dev not in the release line. Consequences:

- `git diff dev origin/release/be-<N>` is **meaningless** once the lines diverge (it reported 3,883
  files / 279k deletions of dev-only work). Diff **consecutive releases** (`be-217 → be-224`) for the
  real weekly delta, and confirm the branch you reviewed is the one `/version` serves.
- Re-verify every carried finding against **both** trees, e.g.
  `git show origin/release/be-v0-50-224:backend/app/api/v1/kyc/asic.py | grep -n require_principal`.
  A finding can be fixed on the release line and still open on dev, or the reverse; report which.
- If a fix claims to have shipped (dnspython, presign wrapper), prove it in the release tree
  (`git show <branch>:backend/poetry.lock | grep -A2 'name = "dnspython"'`) rather than trusting the
  dev commit message.

## Output

- **Only two writes are permitted:** `docs/pluto_weekly_security_scan_log.md` (append the dated entry;
  untracked files survive the daily `reset --hard`) and an **uncommitted** `prod_issues/` draft.
  The `prod_issues/README.md` index row is outside that permission — say it is pending.
- Next global issue ID = highest `issue-NNN` across `prod_issues/`, `backend/prod_issues/`,
  `frontend/prod_issues/` + 1 (compute it; never trust a number written in a doc). Also grep
  `prod_issues/README.md` for the candidate ID before writing the draft: a filename-only check is not
  enough, because an earlier scan's draft can already occupy an ID that the tracked index has since
  given to a different (resolved) issue — a draft named `issue-375-*` sat beside the real, unrelated
  tracked issue-375 for two weeks. If a carried-forward draft collides, say so in the log and request
  the renumber; do not rename tracked-adjacent files. Do **not** open a
  second entry for a HIGH that already has an issue — reference the existing ID instead.
- **Re-run the collision check every week on carried-forward drafts, not just at creation.** The same
  two drafts have now been renumbered **three times** (411→430 and 375→431 on 9 Oct; 430/431→486/487 on
  20 Nov; 486/487→**493/494** on 27 Nov when a real tracked `issue-486-r2-presign-failures…` shipped in BE
  0.50.220 and the frontend line consumed 487): a renumber is only valid as of the week it was
  computed, because tracked issues keep consuming IDs. Each run: check the draft's number against
  `git ls-files` **and** `prod_issues/README.md` **and** commit messages / release branch names
  (`git log --all --oneline --grep='issue-4[89][0-9]'`), then `mv` the **untracked** draft to the next
  free ID and record the history inside the file. Renaming an untracked draft is inside the write
  permission; renaming a **tracked** file is not. The real fix is upstream: drafts must be committed
  with their README rows the week they are produced, or the IDs will keep being eaten.
- Outcome is `PASS` only with no HIGH/CRITICAL; otherwise `APPROVAL_REQUIRED`, with exactly one
  concrete question for Haris and the exact next action, owner and recheck date.
- Never fabricate a remediation: a check run against the wrong account/profile, or an auth 401 caused
  by your own header, is an artifact of the run — correct it and re-run before it reaches the report.
