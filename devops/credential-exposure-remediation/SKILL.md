---
name: credential-exposure-remediation
description: Use when a script or config holds a hardcoded secret.
---

# Credential Exposure Remediation

Getting a live secret OUT of code and onto the environment store, so the human can rotate it. Applies
to any exposure site: fleet scripts, cron job prompts, config files, an inline connection URL.

## The handshake — say who does what, up front

- **Yours: containment.** Move the value out of the artefact and make the code read it from the
  store. Nothing more — you cannot rotate a credential on the owner's behalf, and reporting the find
  as fixed without rotation is the failure this skill exists to prevent.
- **Theirs: rotation.** The only real remediation. Report it as a distinct, named next step: *the
  safety is in place, here is what to rotate*.
- **Treat every exposed value as compromised.** It has been sitting in plain text, and if it lives in
  a cron prompt it has also passed through whatever delivers, logs and renders that prompt.

## Procedure

### 1. Back up first — these targets usually have no version control

Fleet scripts, cron registries and dotfiles are commonly outside git, so an edit has **no undo**. Copy
the whole script directory plus the job registry to a timestamped backup before the first edit, and
tell the human where it is. Do this even when the fix looks like a one-liner; it is the cheapest
insurance in the procedure and the step that gets skipped when someone is in a hurry.

### 2. Find every exposure site, and prove the detector works

Two shapes — and check the registry, not only the scripts, because credentials also hide in **cron
job prompts** and inside shell lines within them:

```bash
# literal assignment (the length floor avoids matching flags and paths)
grep -rnE '(KEY1|KEY2|PASSWORD|TOKEN)\s*=\s*["'"'][^"'"']{8,}["'"']' <dir>
# credentials embedded in a URL:  postgres(ql)://user:pass@host
```

Name the keys you are hunting (an audit or the report supplies them). **A detector's zero result is
only trustworthy once you have watched it fire**: a pattern written narrowly for one assignment style
returns "none" on the real file and therefore reads as clean. Run the pattern against a known-dirty
sample first, then against the tree, and report hits as `file:line` plus the KEY NAME — never the
value.

### 3. Reuse the store's existing convention — do not invent one

Find scripts that already load secrets correctly and copy their mechanism exactly:

```bash
grep -rnE 'dotenv|os\.environ|getenv|\.env' <dir>/*.py | head
```

In this fleet the convention is an ordered candidate list read into the process environment —
`/mnt/c/Users/habib/.hermes/.env` (Windows-host copy) then `~/.hermes/.env` — followed by plain
`os.environ["KEY"]` lookups. A second loader, a new secrets library, or a per-script store all create
drift; adopt what already works.

### 4. Fail loudly, and never keep a fallback

Replace the literal with a required lookup that raises naming the key when it is absent. **No default
value, no empty-string fallback, no `or "<old value>"`** — a fallback silently resurrects the insecure
path and makes the missing key invisible in exactly the environment that needs the fix.

Preserve the consuming context's form: shell reads want `${KEY:?KEY is required}`; an agent prompt
that used to carry the value inline needs the variable reference plus an explicit *never print this
value* instruction.

### 5. Verify without needing the real values

Four checks, all runnable before the human rotates anything:

- `python3 -m py_compile <script>` for every edited script.
- **Load path with dummies**: export obvious dummy values and show the script resolves them
  (`KEY=loaded`) — proves the lookup is wired, not merely present.
- **Missing-key path**: unset one and show the diagnostic names the key — proves the loud failure
  works and no fallback survived.
- **Literal sweep**: re-run the step-2 pattern; the required result is **zero matches**, reported as a
  count and line numbers only. A registry edited for prompts must still parse — validate the JSON.

### 6. Hand over the rotation list

Per exposed key: the KEY NAME, every file it appeared in, and the old line → the new lookup line. State
plainly that the new values must land in the store before the affected job next runs, or it will fail
loudly — that is the design, not a regression, and it is what makes the rotation verifiable.

### 7. Do not ship a required lookup for a key that does not exist anywhere

Step 6's "it will fail loudly" is only acceptable when the value is *reachable somewhere the script can
already get it*. Before choosing the required-lookup form, run one command per key against the store
the loader reads:

```bash
for f in /mnt/c/Users/habib/.hermes/.env ~/.hermes/.env; do grep -oE '^[A-Za-z_][A-Za-z0-9_]*' "$f"; done | sort -u | grep -x 'RDS_PW' || echo "KEY ABSENT"
```

If the key is ABSENT, a required lookup is **not** remediation — it is a guaranteed outage, and the
reward for removing a secret from the page is a dead production job. Two valid resolutions, in order:

1. **Prefer the dynamic fetch the fleet already uses.** If a sibling script resolves the same kind of
   credential from AWS Secrets Manager (or SSM), reuse that exact call and delete the env requirement
   entirely — see `tapease_payout_email.py :: fetch_db_password()`. This removes the secret AND keeps
   the job working, and needs no owner action at all.
2. **Only if no dynamic path exists**, leave the required lookup and escalate the key as a hard
   blocker on the owner's next-run path — never as a routine rotation item.

A credential value that must be *typed into a dotfile by hand* is a worse outcome than no change: it
trades a code exposure for a silent operational dependency nobody can discover later.

## Pitfalls

- **Never print, echo, diff or log a value** — not in the report, not in a pasted diff, not by quoting
  an error message. Refer to secrets by key name and line number; when a check would otherwise print
  matching lines, print `file:line` and a boolean instead.
- **One key is usually several sites.** A sweep that fixes the script and stops leaves the same value
  live in a second script or in a cron prompt. Enumerate the set, fix the set, then re-sweep.
- **A secret that was committed and later removed is still exposed** — history keeps it. Flag the value
  as compromised on the strength of having been written down at all, not on where it now sits.
- **`os.environ.get("KEY")` returning `None` at a call site is not the fix.** The fix is the required
  form at the boundary plus the diagnostic; a silent `None` propagates into connection errors that read
  as an outage.
- **Do not rotate for the human, and do not paste a suggested new value.** Generation and rotation
  belong to the credential's owner.
- **Verify the patched script one step further than "fails loudly": prove it RUNS.** A required-lookup
  rewrite that raises on a missing key compiles clean and passes every dummy-probe, so the whole
  verification block above can be green while the job is dead. After the rewrite, execute the real code
  path end-to-end (the credential fetch + one live read-only call) and show actual output. The failure
  mode this catches is invisible to `py_compile`: `tapease_daily_transactions.py` shipped a
  `_required_env("RDS_PW")` for a key present in neither `.env`, and the 21:30 settlement report died at
  import with `RuntimeError: Missing required environment variable: RDS_PW` — the verification at the
  time reported `RDS_PW=loaded` because it fed a dummy value in the subprocess, which is exactly the
  case production would never have.

## Related

- `monitoring-alert-verification` — the fleet audit that usually surfaces these findings, and the
  truthfulness rules the surrounding monitors must meet.
- `aws-cloudwatch-agent` — the same `.env` loading convention on the AWS-observability side.
