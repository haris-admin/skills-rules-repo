# Pre-check-in definition of done

**Scope:** every agent. Two gates, not one: an **incremental** restore-point commit at milestone
points (per phase / component, not one per task — `incremental-local-commits.md`, human
clarification 28 Aug 2026), and a **closeout** gate when the change is ready to ship or a push was
requested. See `docs/agent_rules/incremental-local-commits.md` (human decisions 22 Aug + 28 Aug
2026).

**This closeout gate is the implementing agent's own production-readiness self-check** — not a
reviewer's job, not a later pass, and it applies whichever agent you are (Claude Code, Gemini
Antigravity, Cursor, or any other). Human instruction, the project lead, 28 Aug 2026: after every logical
change, when closing it out, every agent checks production readiness *from its own point of view*
against the rules we already have — audit trail correctly updated, UI in order, design tokens/CSS
used, reusable code reused, no new one-off fonts or artifact types introduced — and applies these
as part of the final check. Before you declare the change done or set `status: implemented`, run
every applicable line below and **report the outcome of each to the user**: satisfied (with the
evidence), N/A (with the one-clause reason), or not satisfied (with why). A line you did not run
is not a line you may report as passing.

## Why this exists

Added 12 Aug 2026 (C405). Every item below already existed somewhere — the OpenSpec/TDD mandate,
the observability rule, commit hygiene, the coverage floors in `AGENTS.md`. None of them stated it
as *one list you run before committing*, so in practice items got remembered individually and
skipped individually. C330 shipped with its `EXPLAIN` verification left as an unchecked "optional
residual" and it was never done. That is the failure mode this closes.

**This full list is the closeout / pre-push gate.** Requiring it before every small restore-point
commit is why agents skip committing. For the milestone restore-point commits during a change
(per phase / component — `incremental-local-commits.md`, 28 Aug 2026), use the lighter
incremental gate in that file instead.

For a closeout or requested-push commit: run this list. Do not commit that class of change until
every applicable line is either satisfied or explicitly reported to the user as not satisfied
and why.

## The closeout gate

### 1. Tests
- [ ] Backend: `cd backend && poetry run pytest` — **full, unfiltered**, not just your files.
      Record the pass/skip/fail counts.
- [ ] Frontend: `cd frontend && npm test` (jest **and** vitest both report) and
      `npx tsc --noEmit` clean.
- [ ] Every new test cites its task ID, and its Red was confirmed for the right reason
      (`red-for-the-right-reason.md`).
- [ ] Any guard/invariant test was proven non-vacuous by making it fail on purpose.
- [ ] **Failures are reported honestly with their output.** "Pre-existing" is a fact about timing,
      never a reason to skip investigating — see `immediate-error-investigation.md`.

### 2. Lint and schema
- [ ] `poetry run ruff check <your changed files>` clean. Scope it to your files; the repo-wide run
      returns pre-existing findings that are not yours and will drown the real one.
- [ ] `poetry run alembic heads` returns a **single** head if you touched migrations.
- [ ] No swallowed exceptions introduced — no bare `except: pass`, no empty `catch {}`, no
      `catch { return null }` (`observability-and-error-management.md` §2).

### 3. Evidence
- [ ] `tasks.md` completion log records **real commands and real counts**, not "verified" or
      "done". An acceptance criterion is met when there is reproducible evidence, not when the code
      runs.
- [ ] Anything you could not verify locally is listed explicitly as not verified, with the reason
      (needs deploy, needs prod data, needs a human gate).
- [ ] Any deliberately-deferred work is logged to `docs/technical_debt.md` with its reasoning —
      not dropped silently.

### 4. Scope and status
- [ ] You did only the approved work. Deviation from an approved `implementation_plan.md` reopens
      the plan gate.
- [ ] `status: implemented` is set **only after** confirming the commit exists —
      `git log --oneline -- <paths the change touches>`. Zero commits means `status: partial`.
      (Got wrong once already, 76a, 10 Jul 2026.)

### 5. The working tree
- [ ] `git status --short` reviewed; every path you are about to commit is one you actually edited
      this session (`git-commit-hygiene-shared-worktree.md`).
- [ ] Any file shared with another session is handled per
      `shared-file-commit-resolution.md` — edited, left uncommitted, and reported.
- [ ] Staged with exact paths; committing with a pathspec on the `commit` itself; never bare,
      never `-A`, never `.`.
- [ ] Commit subject satisfies `commit-message-quality.md`.
- [ ] After committing, re-run `git status --short` and confirm other sessions' files moved exactly
      as expected.

### 6. Route-specific gates (only if applicable)
- [ ] Touched a **public** route → the Lighthouse gate is blocking; a cited mobile **and** desktop
      run is required (`frontend-lighthouse-performance-gate.md`).
- [ ] Touched an **authenticated** `/dashboard/**` or `/admin/**` route's data fetching → no
      Lighthouse gate applies, but `/prod-db-perf-audit` Step 5b does.
- [ ] Added or changed a state-changing path → the audit-trail mandate's four requirements are
      satisfied (`data-retention-and-audit-trail-mandate.md`). Not "assumed" — for **every outcome
      path the change introduces or touches** (success, no-op/skip, failure, denial/4xx) a durable
      audit row is **actually written and proven by a test**, with actor / action / target /
      timestamp / outcome present. The C314 contract registry (`backend/audit_contracts.json`) has
      a row for every new mutating entrypoint with the correct `actor_type`
      (`HUMAN | SYSTEM | AI | EXTERNAL | MAINTENANCE`), and the contract guard test was re-run and
      recorded.
- [ ] Touched an agency-scoped path → `00e` Option B tenant-isolation tests exist and pass against
      **real Postgres**, not SQLite.

### 7. Frontend design system & UI (only if the change touches any FE code or rendered surface)

Drawn from `frontend-design-system.md` and the `yourapp-ui-consistency-audit` skill. If the change
touches no frontend code and renders nothing, mark this whole section **"N/A — no frontend surface
touched"** and move on.

- [ ] Colours, spacing and typography use the design tokens — no hardcoded hex / `rgb()` / named
      colours, no px font sizes, no ad-hoc spacing or radii where a token exists
      (`--c-*`, `--fs-*`, `--sp-*`, `--r-*`; light-surface tokens only — dark marketing surfaces
      use `landing.css` / `auth.css` tokens).
- [ ] Interactive elements use the shared primitives (`@/components/ui/Button` and its
      `primary | secondary | danger | ghost` variants, and the other `components/ui/` primitives) —
      no bespoke re-implementation of something that already exists, no `style` passthrough setting
      `background` / `color` / `fontSize` / `borderRadius` / `padding`.
- [ ] No new font family or weight introduced; no new one-off icon / image / asset added when an
      existing one covers the need; no new "artifact" type — a new component pattern, a new modal
      style, a new card treatment — that diverges from what is already in use. A new Button variant
      or token value is a **product decision** and goes through the plan gate, not in here.
- [ ] Reusable code was reused — shared helpers / hooks / components used rather than copy-pasted or
      re-derived; genuinely new shared logic is placed where it can be reused, not inlined into one
      caller.
- [ ] Contrast and interaction states meet the design-system rule — text/labels ≥ 4.5:1, non-text
      UI ≥ 3:1 (computed, not copied from a doc); hover / focus / disabled / loading states all
      present and correct.
- [ ] The change was checked **rendered**, not only in source — the actual page/component was
      viewed (or a cited screenshot / Storybook / running-app check is recorded), per
      `yourapp-ui-consistency-audit`.
- [ ] Public route → the Lighthouse gate in §6 applies (cross-reference, not a second run here).

## Do not

- **Do not push.** Pushing requires an explicit ask in the current message. A local commit is not a
  push and does not imply one.
- **Do not claim a line is satisfied without having run it.** An unrun check reported as passing is
  worse than an admitted gap — it is a false negative someone will rely on.
- **Do not treat an inapplicable line as a failure.** Mark it N/A with the one-clause reason.

## Related

- `.claude/skills/production-readiness-closeout/SKILL.md` (pointers
  `.agents/skills/production-readiness-closeout/SKILL.md`,
  `.cursor/rules/production-readiness-closeout.mdc`) — **the executable companion.** This rule
  states what must be true; run the `production-readiness-closeout` skill to verify it and produce
  the PASS / PASS-WITH-GAPS / NOT-READY report before declaring a change done or setting
  `status: implemented`. Complementary to `openspec-verify` Mode B, not a substitute.
- `docs/agent_rules/openspec-tdd-mandate.md` · `red-for-the-right-reason.md` ·
  `test-doubles-vs-assertions.md`
- `docs/agent_rules/git-commit-hygiene-shared-worktree.md` · `shared-file-commit-resolution.md` ·
  `commit-message-quality.md` · `incremental-local-commits.md`
- `docs/agent_rules/observability-and-error-management.md` ·
  `immediate-error-investigation.md`
- `docs/agent_rules/frontend-design-system.md` ·
  `docs/agent_rules/data-retention-and-audit-trail-mandate.md` ·
  `.claude/skills/yourapp-ui-consistency-audit/` (canonical
  `.agents/skills/yourapp-ui-consistency-audit/SKILL.md`)
