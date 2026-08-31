# Parallel Fleet Research — Multi-Track Sovereign-AI Deep Dive (2026-08-22)

The proven pattern for a deep-research question: fan out to Codex (deep web)
AND multiple profile agents (domain angles) in ONE parallel batch, then
synthesize. Ran 5 tracks simultaneously on "sovereign AI opportunities for a
small AU RegTech team" — all completed in ~7 minutes.

## Track roster (one question, five lenses)

| Track | Runner | Angle | Result |
|---|---|---|---|
| Codex gpt-5.6-terra | WSL background (`codex exec --json -m gpt-5.6-terra` from ~/code/amlhive1) | Deep web research, Gumby-gated opportunity map, source register | 34KB report: 7 ranked plays, skip list, 90-day plan, 18 sources |
| Sol | `hermes -p sol chat -q` | Strategy synthesis | Top play: Sovereign UBO Evidence Agent pilot; Gumby ~900 |
| Caduceus | `hermes -p caduceus chat -q` | Regulatory/compliance | 29 evidence items; KEY CORRECTION: AU walked back mandatory AI guardrails (Dec 2025) |
| Lumen | `hermes -p lumen chat -q` | Mempalace mining | Wrote 5 mine scripts, full corpus dump, gap analysis |
| Aurora | `hermes -p aurora chat -q` | Content/positioning | Content calendar + flagged dead angle ("mandatory guardrails coming" is stale) |

## Key lessons

1. **All 5 in ONE response, each `background=true` + `notify_on_complete=true`.**
   They run concurrently — total wall time ~7 min for 100+ tool calls across
   the fleet. Do NOT serialize.
2. **Codex writes its report to /tmp** (workspace policy: repo + /tmp only);
   copy to `~/.hermes/research_outputs/` after. Check `/tmp/codex_*.md` for
   the file, not just the process tail.
3. **Each agent loads its OWN skill automatically** (sol-strategy-engine,
   caduceus-compliance-watch, etc.) and does REAL web research — Caduceus made
   25 tool calls, Lumen 47. Give them a self-contained prompt; they don't know
   your conversation.
4. **Cross-validate contradictions across tracks.** Aurora's "dead angle"
   correction matched Caduceus's regulatory finding (AI guardrails walked back)
   — when two independent tracks converge on a correction, it's trustworthy.
5. **The prompt pack file pattern:** write a `codex_<topic>_prompt.md` brief
   with role, context, research questions, deliverable, constraints; then the
   Codex call is just "read the brief and execute". Reuse the brief as the
   profile-agent prompt seed (same context block).
6. **Check the ideas/portfolio repos before proposing NEW work.** Out-of-band
   user steer ("check the repos we prepared in gitlab") surfaced `ideas-verifylink`
   (AGDIS-ready onboarding) and `ideas-sovereign-intelligence` (Capability
   Intelligence Engine PRD) — Haris ALREADY had PRDs for the exact territory.
   Inventory `~/ideas-*` + GitLab group first; anchor recommendations to what
   exists.

## Report destinations

- Codex: `~/.hermes/research_outputs/codex_sovereign_ai_report.md` (34KB)
- Aurora content plan: `profiles/aurora/reports/sovereign-ai-content-plan-2026-08-22.md`
- Each agent saves to its own `profiles/<name>/reports/` on the Windows side.

---

## Second worked example — competitive / pricing / positioning research (2026-08-22/23)

Same fan-out pattern, applied to "what can we offer / how do we price it" questions.
Ran 2-4 tracks concurrently per question; all completed in 2-7 min.

| Question | Tracks | Outcome |
|---|---|---|
| Is the Evidence Pack a core feature or add-on? (competitor audit) | Caduceus (competitor matrix: PEXA Clear/First AML/Reapit/GBG/Mitek/Ignition) + Sol (tiering strategy + Gumby gate on add-on vs core) | Verdict: evidence/records = CORE (AUSTRAC retrievability obligation), Pro = output layer. Audit trail is table stakes — PEXA bundles it. |
| What justifies a $299 Pro tier? | Caduceus (AUSTRAC-grounded Pro anchors: Evaluation Readiness, CO Workbench, ACR autofill, reporting groups) + Sol (market tiering data) | Pro = governance/scale/efficiency, never gating a mandatory obligation. |
| AML Partners vs AMLHive pricing | Direct web research (amlpartners.com.au/pricing + rate-card) | AML Partners = $60/mo sub + $25-29/scan + $3,000 program setup; AMLHive $149 flat unlimited wins from ~30-40 deals/yr. |

Key lessons added to the pattern:

1. **Fetch the competitor's LIVE pricing page before asking the fleet.** `curl`/`web_extract` on `/pricing` + `/rate-card` beats the agent's recollection — and the pricing page may be JS-rendered (extract returned only nav), so also grep the search-result snippet cache for plan numbers. AML Partners' numbers came from the search description when the page itself didn't render.
2. **Cross-check "does the product ALREADY have this?" before proposing.** The $299 Professional tier already existed on the live pricing page with audit-trail export included — the whole "add-on vs core" debate was half-resolved by reading the existing site. Check current product state first.
3. **File decisions to the right homes:** strategy decisions → `BUILD_BACKLOG.md`/`startup-ideas/` (Gumby champion backlog) + CoS `relationships/current.md` when a human contact is involved (e.g. Suruchi/UNSW Founders for Simplifii); research → `mempalace-inputs/` queue when the palace is unreadable (see SKILL.md pitfall #7). Do not leave a decision only in the chat.
4. **"Champion" backlog filing pattern:** Haris says "add it to the champion" = create `startup-ideas/<Idea>-build-backlog.md` (full doc: what/contact/reference sites/feedback/next actions) + add a row to the Champion/Pipeline section of `BUILD_BACKLOG.md` + add the contact to the CoS relationships file. This is the canonical home for partner-sourced ideas (UNSW Founders, etc.).
