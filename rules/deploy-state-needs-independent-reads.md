# Deploy and remote state need fresh independent reads, not notes

Any status line that says which commit, image or version is running, pushed or merged. Applies to agents writing shared handover notes and to anyone relying on them.

**Scope:** all agents working from shared plan, context or handoff files (Simplifii-OS, 5 Oct 2026).

---

## Why this exists

On 5 Oct 2026 an agent reported that staging "still only has the recorded `.70.26` image" and that the push to `b5d5d09` was "not a fresh independent remote read". Both statements were honest, and both were stale: its terminal could not resolve `github.com` or reach Docker, so it carried forward its own earlier note. Staging had been on `0.70.29-obs2` for hours. A fresh read of the live health endpoint and the remote took seconds.

## Core Directives

1. **Say where a fact came from.** Tag each status as an independent read (`git ls-remote`, the live `/api/health`, the registry, the served bundle), a reflog or local ref, or a recorded note. Only the first is proof of current state.
2. **Refresh before you contradict a teammate.** If a note says "deployed" and you cannot confirm it, say "cannot verify from here" and ask for a read from a machine that can. Do not restate an older note as current.
3. **If your terminal cannot reach a system, say so and stop short of claiming.** DNS failure, no Docker daemon and no token are blockers to report, not facts about the system.
4. **Prove a deploy with three reads.** The live health `sha` equals the intended full sha; the served bundle filename or hash changed; a smoke test against the host passes. A build log or a push log is not a deploy.
5. **Stamp every status block** with the date, time and timezone, the host or remote read, and what it superseded. Keep the older text below it, marked superseded, so progression stays visible.
6. **CI that fails in seconds with no logs is infrastructure.** A job that ends in 2 to 3 seconds with runner id 0 and zero steps never ran (no runner, billing or minutes). Do not report it as a test failure. Look at a repo or runner where CI actually executes.

---

## Patterns to Follow

```bash
git ls-remote origin refs/heads/<branch>            # independent remote head
curl -sS https://host/api/health                    # live sha and flags
gh api repos/<o>/<r>/actions/runs/<id>/jobs -q '.jobs[]|"\(.name) runner_id=\(.runner_id) steps=\(.steps|length)"'
```

## Patterns to Avoid

- "Staging is on X" copied from last hour's notes.
- Treating `.git/logs/refs/remotes/...` as a remote read.
- Reading a red check with zero steps as a failing test.
