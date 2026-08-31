---
name: pluto-portfolio-ideation
description: Pluto's portfolio ideation engine — generates new startup/project ideas from research signals by mapping market gaps against existing portfolio. Use when Haris asks for new ideas, wants to expand the project portfolio, or needs structured PRD/MVP/success criteria for a new venture.
allowed-tools: [delegate_task, read_file, search_files, write_file, terminal, memory, skill_manage, session_search]
---

# Pluto Portfolio Ideation

## When to Use
- Haris asks "what new ideas do you recommend?" or "what should I build next?"
- Haris says "push to the build queue" or wants to queue the task for async execution
- Expanding the project portfolio beyond existing repos
- Validating ideas against current market signals
- Haris says "engage Brainy" or wants a strategic code review of an existing project
- After completing any major build phase — run Brainy review before presenting to Haris
- **New project intake** (2026-08-29 pattern): Haris sends a voice note naming a new
  engagement (e.g. Simplifii, Step Up) then shares a GitHub repo. Workflow: transcribe
  voice (audio-transcription-wsl skill) → resolve the repo (exact URL may 404 if
  private/renamed — fall back to `https://api.github.com/search/repositories?q=user:<owner>`
  to find the public repo, and read the landing page/README for the real pitch) →
  file a condensed intel doc to `~/.hermes/mempalace-inputs/` tagged for a NEW chamber
  (per Haris: prefer a fresh chamber over cramming) → offer to create the chamber
  once the palace is healthy. Also check the owner's OTHER public repos — a project
  often has a sibling repo (landing page vs OS/frameworks) that contains the fuller
  story.
- **Champion backlog intake** (2026-08-29, Simplifii): when a new project has a
  named contact/person (e.g. Suruchi at UNSW Founders), reference sites from them,
  and pitch/judge feedback, record all of it — do NOT just file intel. The champion
  backlog lives in Gumby's workspace:
  1. Create `startup-ideas/<Name>-build-backlog.md` (see `VerifyLink-build-backlog.md`
     for the house format: idea, reference sites w/ one-line relevance each, pitch
     feedback quoted verbatim + action items, contact person, next actions).
  2. Add a row to `BUILD_BACKLOG.md` under the **"Champion / Pipeline Ideas"** section
     (Contact column = the named person, Status = 📋 Backlog — champion idea).
  3. Add a relationship entry in the CoS workspace
     `~/code/amlhive1/workspace/relationships/current.md` (Contact, Context, Status,
     Notes incl. feedback action items + next actions).
  Pitch feedback is a MAJOR driver — capture it verbatim with per-item action items
  (business model clarity, NFP vs for-profit, partners, differentiation, community
  build via manual matching, team capabilities, global/local scope, presentation).

For the **build queue pattern** (cron job wrapping Codex CLI), see `references/build-queue-pattern.md`. This is the preferred approach when Haris wants the ideation run as a queued/async task rather than inline.

For the **CONTEXT.md template** (proven with Codex 5.5, 97K tokens, 3 strong ideas), see `references/codex-context-template.md`. Use this structure every time — the portfolio table, explicit exclusion list, and cross-domain signals are what drive quality output.

For the Brainy strategic review pattern (subagent-based code review with star ratings and prioritized roadmap), see `references/brainy-strategic-review.md`. Use when Haris says "engage Brainy" or after completing a build phase.

For the **local build queue registry** (filesystem-based project tracker at `~/.hermes/mempalace-inputs/.build-queue/`), see `references/local-build-queue.md`. Use this when Haris asks "what's in the queue?" or when you need to move projects between active/staged/completed/archived.

For the **Ideas→Development pipeline** (automated cron job that elevates an idea repo from MVP to production-ready with Open Spec + TDD + extraction + commits), see `references/ideas-to-development-pipeline.md`. Use this when Haris says "make it ideas-to-development flow" or asks you to add proper dev infrastructure to an existing idea repo.

## Pipeline

### Phase 1: Load Research Signals
1. Read today's research JSONs from `~/.hermes/research_outputs/`
2. Check for external intelligence reports in `~/.hermes/mempalace-inputs/` (e.g., GenSparks weekly reports)
3. Query ChromaDB mempalace for recent findings across chambers:
   ```bash
   python3 ~/.hermes/scripts/pluto_mempalace_feeder.py --status
   python3 ~/.hermes/scripts/pluto_mempalace_feeder.py --query "compliance platform" --n-results 5
   ```
4. Extract key signals: trends with hard numbers, regulatory changes with deadlines, emerging gaps
5. Mark confidence levels: high (official source/multiple surveys), medium (credible analysis), low (speculation)
6. If GenSparks validates or kills an idea, treat that as a weighted signal (A-grade = strong validation, KILLED = definitive rejection)

### Phase 2: Audit Existing Portfolio
1. Find all `ideas-*` repos:
   ```bash
   # CORRECT location — C:\Code\gitlab\, NOT C:\Users\habib\
   find /mnt/c/Code/gitlab -maxdepth 1 -type d -name "ideas-*"
   # Also check old location for any migrated repos
   find /mnt/c/Users/habib -maxdepth 2 -type d -name "ideas-*" 2>/dev/null
   ```
2. For portfolios under ~10 projects, use a **single `delegate_task`** with the full pipeline context. Parallel subagents are overkill — one subagent can review all repos in a single pass. Reserve parallel subagents for 15+ project portfolios.
3. For each repo determine: what's the idea, stage of completion, tech stack, next step
4. Cross-reference with any existing portfolio review documents (e.g., `ideas-portfolio-review/`)
5. Also check active projects from memory: amlhive.com.au, Tapease, NDIS BillBot, n8n workflows
6. If GenSparks has already graded an idea (A/B/C/KILLED), treat that as an authoritative validation signal — don't re-litigate

### Phase 3: Identify Gaps
1. Map each research signal to existing portfolio coverage
2. A gap exists when: the signal is strong AND no existing project addresses it
3. Also consider: does the signal suggest a complementary product to an existing one? (e.g., AgentGate governs → AgentRed tests)
4. Score gaps by: signal strength × market timing × portfolio synergy

### Phase 4: Generate Ideas
For each serious candidate, produce:

**PRD section:**
- Problem (grounded in a specific research signal)
- Solution (one-sentence value prop)
- Target user (specific persona, not "enterprises")
- Value proposition (quantified if possible)
- Revenue model (Phase 1 free/cheap → Phase 2 SaaS path)
- Competitive moat (why defensible)

**Gap assessment (optional — see `references/gap-assessment-framework.md`):**
When productizing existing infrastructure, run the 88-point framework across 7 domains to quantify readiness. High Research + near-zero Business = the hard part is done.

**MVP scope (AUD $250 budget constraint):**
- List concrete deliverables with formats and effort estimates
- Phase 1 is content/framework unless code is essential
- Prefer: Markdown → Sheets → Static site → React/Next.js → Full SaaS (increasing effort)
- **Tech stack preference (HARD RULE):** Frontend MUST be JavaScript — React/Next.js with Tailwind CSS. Backend is Python/FastAPI. NEVER propose Streamlit or Python-only frontends. User explicitly rejected Streamlit.

**Success criteria:**
- Specific, measurable targets with month-1/month-2/month-3 timelines
- Include: downloads, industry recognition, paid conversions, enterprise inquiries
- Include "ultimate success" — what winning looks like at scale

### Phase 5: Score with Gumby 1000-Point Assessment
Score every candidate idea against the 7-dimension framework. See `references/gumby-1000-point-assessment.md` for the full scoring rubric.

1. Score each idea across all 7 dimensions with rationale
2. Assign a letter grade: A (800+), A-/B+ (700-799), B (600-699), C/KILLED (<600)
3. Produce decision matrix: all ideas side by side
4. Rank and recommend build order
5. Write `1000_POINT_ASSESSMENT.md` to the ideas workspace

### Build Standard (Mandatory — Enforced by Haris)

Every idea repo in GitLab follows this exact standard. The naming convention is `ideas-XXXXX` (hyphenated slug, e.g., `ideas-agentred`).

**Phase 0: Open Spec (before any code)**
1. Write `docs/OPEN_SPEC.md` documenting all questions, scenarios, decisions
2. Define the component breakdown + dependency graph + TDD build order
3. Get Haris's sign-off before writing any code

**Phase 1: TDD Infrastructure**
1. Write failing tests first (RED phase — watch them fail)
2. Write minimal code to pass (GREEN phase)
3. Refactor while keeping tests green
4. Commit after EVERY completed phase

**Commit Cadence**
- Multiple commits per day — every milestone checked in
- Commit messages follow conventional commits: `feat(area): description`
- Every `git push` goes to GitLab with `GITLAB_PAT_OPENCLAW` token
- Never let a day end without pushing progress

**Phase 2: Extract → Integrate → Cron → Push**
See `references/ideas-to-development-pipeline.md` for the full pipeline.

**Voiceover Delivery**
Every major recommendation or build proposal should include a TTS voiceover alongside text. Use `text_to_speech` for the key pitch — Haris consumes voice as a primary medium.
For ideas scoring 700+ (Grade A or A-/B+), follow the full Ideas→Development pipeline. See `references/dev-queue-push-pattern.md` for the complete 6-phase workflow (Design → TDD → Extract → Integrate → Cron → Push).
### Phase 7: Push to Development Queue
For ideas scoring 700+ (Grade A or A-/B+), follow the dev queue push pattern. See `references/dev-queue-push-pattern.md` for the full 6-step workflow (create repo → write docs → commit → cron job → MemPalace → GitLab push).

1. Create `ideas-<slug>` repo on `/mnt/c/Code/gitlab/`
2. Write README.md + PRD.md + ASSESSMENT.md
3. Git commit
4. Create cron build job (`cronjob action=create`) for Phase 1 MVP
5. Feed to MemPalace via `pluto_mempalace_feeder.py`
6. Push to GitLab with `GITLAB_PAT_OPENCLAW` token
7. Update Gumby brief input if needed

Before Phase 1 code, also run the pre-build security audit. See `references/security-audit-template.md`.

### Phase 7: Pre-Build Design Review (before coding)
For the top-ranked idea, produce architecture + Open Spec + mockups before any code:
- Architecture doc with PlantUML C4 diagrams (Container, Frontend, Backend, ERD)
- Open Spec component breakdown with TDD build order
- UI mockups as self-contained HTML (Tailwind CDN)
- Security audit against OWASP + ASD E8 + AU Privacy Act

### Phase 8: Ideas→Development (post-MVP upgrade)
Once the MVP is built, elevate it to production-ready using the full Ideas→Development pipeline. See `references/ideas-to-development-flow.md` for the complete 7-phase workflow:

1. **Open Spec** — component breakdown + dependency graph + TDD build order
2. **Architecture** — C4 diagrams + data flow + ERD + deployment
3. **TDD Infrastructure** — pytest + vitest + 15-20 unit tests
4. **Extract Core Logic** — data dicts → standalone modules, inline logic → lib/
5. **Integration Tests** — FastAPI TestClient for all endpoints
6. **Brainy Review R1** — star rating + P0/P1/P2 issues + architecture/test/production scores
7. **Fix & Re-Review** — implement fixes, re-engage Brainy, compare ratings

Each phase commits after completion. Target: 8+/10 after fixes.

## Output Format

Write the full analysis to a markdown file and deliver it. If the file can be pushed to the `ideas-portfolio-review` repo, do so. Otherwise deliver to Haris via the chat or save to Desktop as fallback.

File naming: `YYYY-MM-DD-new-ideas-pluto.md`

## Pitfalls
- Do NOT propose ideas that overlap with existing active projects (check memory + repos first)
- Do NOT propose ideas that require more than AUD $250 for Phase 1 MVP
- Do NOT skip the portfolio audit — you'll miss synergies or propose duplicates
- Web search via subagents may return incomplete results — validate against your own research pipeline as primary source
- Git push from WSL may fail (no auth) — fall back to Desktop delivery
- Ideas should be AUSTRALIAN-first: local regulations, local market, local buyers. Global ambition is Phase 2.
- The AUD $250 budget is real — Phase 1 deliverables must be achievable within that constraint
- Each idea must trace back to at least one specific, high-confidence research signal
- **Brand separation is non-negotiable.** AML Hive and Haris Habib personal brand are completely separate entities. Zero cross-references. AML Hive content goes on amlhive.com.au with LinkedIn through Alvina's account. Haris Habib content goes on harishabib.au with LinkedIn on his personal profile. Every recommendation must state which brand it belongs to.
- **Include TTS voiceover with major recommendations.** Every build proposal, score report, or significant recommendation needs a `text_to_speech` call alongside the text. Haris consumes voice as primary medium.
- **Git identity must be configured before first commit.** `git config --global user.email "pluto@harishabib.au" && git config --global user.name "Pluto Agent"`. Without this, `git commit` fails with "Author identity unknown."" (i.e. `C:\\Code\\gitlab\\`), NOT `/mnt/c/Users/habib/`. The user corrected this — old repos may still be at Users, but new ones go to gitlab.
- **Frontend tech:** NEVER propose Streamlit. User explicitly rejected it. Frontend = React/Next.js, backend = Python/FastAPI.
- **GitLab token:** Read from `/mnt/c/Users/habib/.hermes/.env` → `GITLAB_PAT_OPENCLAW`. Push with `https://oauth2:TOKEN@gitlab.com/hhsiddiqui/ideas-<slug>.git`.
- **Stagger cron build jobs:** When pushing 3+ ideas to the build queue, stagger their cron jobs by 1-minute intervals (1m, 2m, 3m) to prevent concurrent workspace collisions. Each build job runs in its repo's workdir — they don't share state, but staggering avoids WSL/Codex resource contention.
- **False "FAILED" cron status:** The cron scheduler flags output containing "Error", "RuntimeError", or "Traceback" as FAILED even when all builds succeeded. CloudProof AU's build report contained `RuntimeError: ---` (as part of the output structure, not an actual error) and was flagged FAILED despite all 8 commits succeeding. Always verify by checking `git log --oneline` and `find . -type f` in the repo — don't trust the status label alone.
- **Build report wording:** When the cron build agent writes `docs/BUILD_REPORT.md`, avoid leading the report with "Error", "RuntimeError", or "Traceback" in any context — these trigger false-positive failure detection. Use "## Status: Complete ✅" or similar as the first header.
- **Honcho inbound limitation:** The Pluto↔Honcho bridge is currently outbound-only (Pluto pushes findings → Honcho). There is no automated mechanism for Haris or Gumby to push documents TO Pluto via Honcho. If the user mentions a "honcho push document", check standard file locations (Desktop, Downloads, mempalace-inputs) and ask for the path directly — don't spend cycles searching Honcho peers for inbound documents.
