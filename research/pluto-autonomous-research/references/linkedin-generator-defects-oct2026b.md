# LinkedIn generator defects — Rules 76, 76b (Oct 2026)

Continuation of `references/linkedin-generator-defects.md` (Rules 1–75). That file is at the
100K ceiling and cannot take further patches — record new defects HERE from Rule 76 onward.

## Rule 76 — the pillar must follow the vocabulary the finding is written in, and a portfolio hit must not outrank it (Oct 27 2026)

**Symptom.** Finding #5 of the 27 Oct 2026 FinTech corpus — the Tranche 2 cost-burden
counter-signal — was pillared **AI Agents & Governance** with a governance CTA. Its
`portfolio_hit` was `FinAI File AU`, and the Rule 69 title check missed because the title
(`The counter-signal: quantified cost, a privacy honeypot, and practitioners who carry the
liability without the power to refuse the client`) contains **no domain noun at all**: the only
AML/CTF vocabulary, "Tranche 2", sits in `content`. Rule 69's exception is deliberately
title-scoped (a title naming AI must keep the AI pillar), so a subjectless title falls straight
through to the `FinAI File AU` early return.

**Why the obvious fixes fail.** Two heuristics were tested and rejected before shipping:

1. *Subjectless-title fallback* — "if the title names no subject, use the content". The title
   contained `privacy`, which the proposed subject regex listed, so the branch never fired. Any
   subject list long enough to cover a real corpus will match these synthesis titles.
2. *Content-side AML regex on presence alone* — re-opens Rule 66's defect (a cloud story that
   mentions APRA in passing is not an AML story). It must be a **dominance** test, not a
   presence test.

**Fix.** Inside the `FinAI File AU` branch only: count AML/CTF subject terms against AI terms
over `title + content`; if `aml_n >= 2 and aml_n > ai_n`, return `Australian Fintech Regulation`.
The product records who is AFFECTED, the pillar records what the post is ABOUT (Rule 67), and
the vocabulary a finding is *written in* is the best available proxy for its subject.

**Replay.** 9 retained research days: **1 finding changed** (today's #5, intended), **0
regressions** — every AI- and cloud-titled finding keeps its pillar, and the 22 Oct AMLA case
that Rule 69 fixed stays Fintech. Verify by printing `pillar_for(finding)` for every finding of
every retained day and diffing, never by checking only the failing case.

## Rule 76b — OPEN DEFECT: synthesis-label titles produce fact-free hooks (Oct 27 2026)

Finding #5's hook shipped as `The counter-signal: quantified cost, a privacy honeypot` — a label
plus the first item of a comma-list of abstractions. Every existing gate passes it: it is a
complete clause, it does not end on a verb, and there is no dangling comparative. The truncator
prefers the pre-colon clause, and **neither branch of `_prefer_figure_clause()` fires** because
the remainder carries no digit and the label tail (`counter-signal`) is not a
`_META_LABEL_TAILS` member. Adding the tail to that set does **not** fix it: the remainder is
still `quantified cost, a privacy honeypot, and practitioners…`, so `_short_title` then cuts at
the next comma and ships `Quantified cost, a privacy honeypot` — the same fact-free hook with a
capital.

**The class is a title with no claim in it at all**, so the fix is not another truncation tweak.
It needs a fallback to the finding's `stat` clause (the `stat: title` join, bounded as in Rule
46) or to a constructed claim, plus a harness containing synthesis-style titles. Until then:
rewrite these hooks by hand in the curated section and flag the defect, rather than shipping the
generator's output.

## Rule 49 recurrence + practice note (Oct 27 2026)

`autonomy-tiers` shipped as blog idea #2 on a **single** hit: `out of scope`, taken from the
commercial-finance-broking scope-limbo story ("residential mortgage broking appears to be out of
scope"); `autonomy` itself was ZERO in the corpus, and `gartner` had kept it alive on 21 Oct.
Re-bound to autonomy/oversight vocabulary (`autonomy level`, `agent autonomy`, `human-in-the-loop`,
`trust boundary`, `kill switch`, `approval gate`, `human oversight`): today 1 → 0, while it keeps
its two genuine prior hits (23 Oct "trust boundary", 25 Oct "human oversight") — bound, not
killed. Verify BOTH directions every time.

The day's own-pillar fresh pool after that fix was ONE genuine candidate
(`austrac-infringement-notices`; `aml-readiness-evidence-gap` was inside the 10-day window) while
finding #4 — commercial finance broking stuck in AUSTRAC's unresolved "debt financing" scope
question — had no candidate. Per Rule 40/45 practice, ADD subject-bound candidates, never loosen
a gate: `debt-financing-scope` (debt financing / asset finance / commercial finance broking /
document a reasonable position / table 6 — 5 hits today, 0 on the seven prior retained days).
The same run corrected `austrac-infringement-notices`' gap, which asserted "30 Sep 2026 across
real estate, accounting and jewellery" while the corpus carried only "late September 2026",
A$21,840/A$4,368, s167(3A), 14-day windows and the sector enrolment rates (Rule 34/58). The
superseded `Autonomy Tiers` title was pruned from the ledger (Rule 72).

**Lesson that generalises.** A candidate's keyword list is only as good as the sentence that
fires it. Print the sentence, not the count.

## Rule 77 (Oct 28 2026) — `control plane` is context vocabulary when the story is about governance

Rule 49 recurrence on the same candidate for the third time. `agent-runtime-consolidation` (gap:
agent-security M&A / assurance gap once platforms own runtime telemetry) held a bare `control
plane` keyword that survived the 14 Oct purge, and on 28 Oct the ONLY phrase it fired on was the
counter-signal finding's "the agent-control plane is being certified on self-report" — a
governance-layer metaphor, with `promptfoo`, every vendor name and `land grab` all ZERO and no
M&A story anywhere in the corpus. It reached blog slot #3 on a single hit.

Removing `control plane` took today 1 → 0 without killing the candidate: its genuine historical
evidence fires through `promptfoo` and the vendor names, which is what its gap actually asserts.
**Replay limitation, stated honestly:** the 14 Oct research JSON is no longer retained, so the
"prior day keeps its hits" direction could not be re-run this time — verify that direction on the
next day the same candidate fires, and never claim a two-way replay you did not run.

## Rule 76b recurrence + Rule 45 recurrence #5 (Oct 28 2026)

**The synthesis-label hook class is broader than `UPDATE`/`CONTINUATION`.** The research pipeline
also writes `Counter-signal: <claim> — <detail>`, and on 28 Oct the delivered hook was
"Counter-signal: the agent-control plane is being certified on self-report": pipeline taxonomy in
front of a reader-facing claim. Fix is the Rule 63 pattern — add the label, not a hook-builder
special case: `counter-signal`, `counter signal`, `counterpoint` joined `_META_LABEL_TAILS`, so
`_prefer_figure_clause()` takes the tail and the hook now ships as "The agent-control plane is
being certified on self-report". Bare `signal` was deliberately NOT added — it would rewrite the
accepted hook "Your Provider's Bond Price Is a Governance Signal: …". Blast radius checked by
grepping every retained research JSON for the label: two days carried it (27 and 28 Oct).

**Rule 45 recurrence #5, and the first time the padding loss was a TWIN-KEY repeat.** On an
Agentic-AI & Security day every grounded AI-governance candidate sat inside the 10-day window
(`nhi-agent-identity` 18 Oct, `scorer-independent-verification` 22 Oct, `agent-registry-supervision`
and `sector-regulator-ai-supervision` 25 Oct), so the Cloud slot padded with
`eval-egress-containment` — the 25 Oct containment gap under its other twin key. The twin map
cannot catch this: the 25 Oct delivery was the SIBLING key's title, so `_repeat()` did mark it a
repeat, but Rule 29d lets a repeat take a leftover slot when nothing fresh exists. Diagnostics
that found it: count the pool the matcher USES per pillar, then diff today's GAP lines against
`date - 5`, not the titles.

The day's top-two signals (ASD agent-swarm breach; METR/Redwood monitor integrity) had no
candidate at all, so two were ADDED, both replayed 0 hits across the seven prior retained research
days: `agent-oversight-monitor-integrity` (7 hits today) and `asd-agent-swarm-breach` (7 hits
today). Bare `metr`, `oversight` and `red-teamed` were kept OUT of the keyword lists — `metr`
appears on 21/22/26/27 Oct as a passing reference and `oversight` on 25/26 Oct, i.e. exactly the
context-vocabulary trap this log keeps recording. With two fresh candidates the repeat dropped
out and the slate went 3 ideas → 2 genuinely grounded ones. The never-delivered repeat title was
pruned from the ledger (Rule 72), twice — once for the first superseded slate and once for the
second — so a re-run that replaces the slate never suppresses a title Haris never saw.

**Identity cluster, deliberately not re-proposed.** The Frontegg/IBM agent-identity evidence was
the day's second cluster, but `nhi-agent-identity` shipped on 18 Oct and any new
`agent-credential-lifecycle` candidate would be its twin (Rule 74). Correct action is to say so in
the curated section and let the 10-day window hold, not to ship the same idea under a new title.
