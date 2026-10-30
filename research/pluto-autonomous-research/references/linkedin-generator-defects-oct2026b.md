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

## Rule 78 — fix the classification on EVERY surface the string reaches (Oct 29 2026)

**Symptom.** Idea #4's hook was correctly capitalised ("The record A$4.2bn quarter decomposes to
93%…") while the display title directly above it — the H3 Haris copies as the post headline — read
"the record A$4.2bn quarter decomposes to…". The finding's raw title began `UPDATE to the 13
October feed - the record…`; `_strip_leading_feed_ref()` (Rule 48/56/73) removed the pointer and
left a lowercase residue, and the Rule 68 capitalisation fix runs on the HOOK builder only.

**Fix.** After the feed-ref strip, capitalise the title when its first token is a leading FUNCTION
word (`the/a/an/and/but/this/that/what/why/how/…`, the bounded `_LOWERCASE_LEAD_WORDS` set). The
set is deliberately small so brand-cased tokens ("iOS", "eBay", "macOS") are never rewritten —
a blanket `title[0].upper()` is the wrong fix.

**Rule.** Rule 73 said it for feed refs: when a rule classifies a string as unreadable, apply that
classification everywhere the string is delivered. Rule 78 is the same lesson for CLEANUP — a fix
that runs on the hook does not run on the title unless you put it there.

## Rule 78b — a CTA must not assert a date the corpus cannot support (Oct 29 2026)

`CTA_BY_PILLAR["Startup & ESOP"]` shipped "Modelling this for a cap table or an ESOP **before the
28 Sep deadline**?" on 29 October — six weeks stale, on the day's top two posts, because the
deadline was typed into the constant when it was true. **Rule:** keep dates out of static copy.
A template constant outlives every deadline it names, and nothing in the pipeline can tell that it
has expired.

## Rule 79 — a name initial is not a sentence end (Oct 29 2026)

**Symptom.** The NonPublic angle ended "…ARK Invest, Citadel, Fidelity, Morgan Stanley, T." — the
`[.!?](?=\s)` sentence-end scan matched the "." in "T. Rowe Price", so `_trim_angle` cut there and
silently discarded the rest of the sentence.

**Fix.** Reject a candidate cut whose segment ends on a bare single capital + "." (`(?:^|\s)[A-Z]\.$`).
A genuine sentence ending in initials ("the U.S.") has a different shape and is untouched.

**Replay.** All 48 angles across the 8 retained research days: **1 changed (intended), 0
regressions**. The class is general: any truncator that treats "." as a boundary must exclude
initials, abbreviations and decimals.

## Rule 80 — a passing regime mention must not out-vote the vocabulary the finding is written in (Oct 29 2026)

**Symptom.** The NonPublic/Tenstorrent finding (Australian wholesale capital into a US$1.5bn
Series E, Anthropic's listing, CBA's stake) was pillared **Australian Fintech Regulation** and
closed with TokenPilot AU's digital-asset CTA, because `reg_strong` matched `afsl` twice in the
body while the story carried no digital-asset content at all. Rule 66/76's defect class, one
branch lower: presence, not dominance.

**Fix.** Before `reg_strong`, count private-markets vocabulary (`pre-ipo`, `wholesale investors`,
`series a-e`, `private markets`, `valuation`, `cap table`, `esop`, `venture round`, `deal count`,
`first round`, `ipo`) against licensed-activity vocabulary (`digital asset`, `token*`, `stablecoin*`,
`crypto*`, `dlt`, `custody`, `afsl`, `psp`, `aml`, `cft`, `austrac`, `licen[cs]*`); if
`vc_n >= 3 and vc_n > da_n`, return Startup & ESOP.

**Replay.** 8 retained research days, every finding: **1 changed (today's #6), 0 regressions.**

## Rule 45 recurrence #6 + practice note (Oct 29 2026)

Startup & VC's own-pillar pool was **empty of fresh grounded candidates**: `vc-barbell-missing-middle`
RETIRED (3 hits), `asx-escrow-composition` (1) and `datacentre-firb-screening` (2) both inside the
10-day window, every other Startup & ESOP candidate at 0. The slate therefore padded ONE Cloud
candidate — `datacentre-permitting-risk` — whose only hit was the context word `withdrawn` (from
"Firmus had already withdrawn its ASX float"), whose gap asserted an A$1.2bn/90MW project absent
from the corpus (Rule 34/58), and whose title had shipped on 11 Oct (`The Project That Walked`)
before the ledger's retention window, so neither the file scan nor the ledger could see the repeat.

Two subject-bound candidates were ADDED (`pre-ipo-access-distribution` 6 hits, `mark-divergence-valuation`
3 hits; 0 on the seven prior retained days). The slate went 1 ungrounded repeat → 2 grounded ideas.
The superseded ledger entry was pruned (Rule 72) so a never-delivered repeat is not suppressed for
10 days.

**Deliberate non-proposal.** The day's #3 signal (FIRB + ACCC suspensory merger regime) had no
Startup candidate, and adding one would have duplicated the same morning's AMLHive content idea
"Two Gates, Two Answers: A Foreign Investment Clearance Is Not an AML/CTF Clearance". Check
`content-ideas-<date>.md` before adding a candidate for a regulatory signal that another lane
already owns, and say so in the curated section instead of shipping the duplicate.

## Rule 77 — a 10-day repeat window cannot see a 15-day cycle, and a stale repeat outranks nothing when the pool is thin (Oct 30 2026)

**Symptom.** The 30 Oct 2026 slate — same `date % 5` slot as 15 Oct — shipped **both** blog ideas
as word-for-word repeats of the 15 Oct pair (`The AI Incident Register…`, `One Product, Three
Rulebooks…`). `_repeat()` answered "not a repeat" for both, correctly: the ledger held them at
15 Oct, 15 days back, outside `_ledger_titles(days=10)`. A 5-day topic cycle plus a 10-day window
means every third visit to the same slot re-serves the same slate, and nothing in the pipeline
ranks *verbatim* staleness below a fresh idea.

**Why it happened (the pool, not the gate).** Filtering `BLOG_CANDIDATES` to the day's pillars and
`_fresh` left exactly two grounded AI-governance candidates — the two 15 Oct repeats. The day's
#2 (TGA digital scribe review), #3 (EN 18286 first harmonised standard) and #5 (board-level agent
accountability) signals had **no candidate at all**, so the slate had nothing fresh to prefer.

**Fix — add candidates, never widen the window.** Three subject-bound candidates were ADDED:
`tga-scribe-device-function` (6 hits), `en-18286-qms-conformity` (6), `board-agent-accountability`
(6); **0 on the seven prior retained days**, verified by replaying each against the retained
research JSONs, and each keyword's firing sentence printed before acceptance. Slate went 2 stale
repeats → 3 fresh grounded ideas. The 30 Oct ledger lines for the two never-delivered repeats were
pruned (Rule 72), keeping the 15 Oct originals.

**Rule 49 recurrence, same run.** `agent-incident-register` fired on a single term, `marking`,
taken from "you can't have OpenAI **marking** its own homework" — a board-accountability quote on a
corpus where `incident`/`reportable`/`serious incident` were all ZERO. Its list carried bare
`marking`, `notification`, `regulator`, `reportable`, `article 50`, `transparency`: all context
vocabulary on any AI-regulation day. Re-bound to reporting mechanics (`incident report`,
`incident register`, `incident log`, `serious incident`, `reportable incident`, `unreported
incident`, `article 73`, `incident notification`): today 1 → 0, 15 Oct record still grounds it.

**Two-way check performed.** Today fires for all three new candidates; the seven prior retained
days return 0 for all three. And confirm a new candidate's gap does not silently duplicate an
existing one: `board-agent-accountability` is distinct from `scorer-independent-verification`
(self-grading mechanism) and from `agent-oversight-monitor-integrity` (whether oversight can be
switched off) — it asks *who is named*, on what evidence. State that boundary in the gap text.


---

## Rule 81 (Oct 31 2026) — a twin pair registered ONE way leaves the OLDER title alive after the window

**Defect.** The 31 Oct Cloud slate (same `date % 5` slot as 16 Oct and 26 Oct) shipped blog ideas that
were **verbatim title repeats from 16 Oct** — `Power, Not Land: The Data Centre Constraint That Will
Re-Price Your Cloud` and `The Missing Substitutability Test` — 15 days old, i.e. outside
`_ledger_titles(days=10)`. Eleven days into the same cycle, 26 Oct had shipped
`The Connection Agreement: Why a Grid Contract, Not a GPU, Now Prices an AI Data Centre`
(`grid-connection-financing`) for **the same gap**: power/grid availability as the binding constraint.
`grid-connection-financing` was registered as a twin of `datacentre-permitting-risk` but **not** of
`datacentre-energy-grid`, so the pair covering one gap was invisible to each other. When
`grid-connection-financing` aged out at 10 days its sibling — five days OLDER in delivery terms — was
only just becoming "fresh" again and re-took the slot.

**Rule.** Whenever two candidates assert the same gap, register the pair **both ways and against every
member of the family**, not just the one you were fixing that day. A one-way or partial twin map does
not fail at the moment you write it; it fails an ageing window later, which is why it survives review.

**Fix.** `datacentre-energy-grid` ↔ `grid-connection-financing` registered both ways.
**Two-way verification.** Live direction: `datacentre-energy-grid` absent from today's slate while its
keywords still fire (1 hit — `aemo`) → deduped, not killed. Counterfactual: with the pair unregistered
(prior run this morning) it took the slot, which is the failing case reproduced.

## Rule 82 (Oct 31 2026) — a bare phrase that is *analysis*, not subject, can be the only thing grounding a candidate

**Defect.** `cloud-concentration-resilience` fired today on **one** keyword, `concentration risk`,
taken from a sentence of commentary inside the London-outage finding ("concentration risk has moved
from a theoretical board paper to a supervisory conversation"). Every one of its own anchors —
`substitutability`, `cloud concentration`, `financial stability review`, `portability`, `exit plan` —
was **zero** in today's corpus, and its gap asserted the RBA Financial Stability Review and BoE
SIMEX26 evidence that only existed on 16 Oct (Rule 34/58 class: a gap may not assert sources absent
from the corpus that fired it). The title was also a 16 Oct delivery.

**Rule.** Keyword grounding must be satisfied by *subject* vocabulary, and a candidate whose gap cannot
be re-grounded in today's sentences should be demoted, not padded into the third slot. Two fixes were
applied together: dropped bare `concentration risk` (it is the vocabulary of any post-hoc analysis),
added `critical third-party regime` (the phrase the story is actually reported in — note the hyphen,
`critical third party` returns nothing), and **rewrote the gap** around the 20 Oct europe-west2-b event,
the FCA/PRA vendor contact and the first-test-of-the-UK-regime framing, all of which are in today's
corpus.

**Practice note (Rule 45 recurrence, third consecutive Cloud slot).** Two fresh subject-bound candidates
were ADDED rather than loosening any gate: `hyperscaler-capex-cashflow` (revenue backlog, `$567.7b`,
`azure crossed`, `free cash flow`, `$45.98b`; **9 hits today / 0 on eight prior retained days**) and
`repatriation-unit-economics` (`37signals`, `cast ai`, `idle capacity`, `provisioned cpu`; **6 / 0**).
The second excludes `unit economics`/`cost optimisation` deliberately so it cannot fire off
`cloud-waste-finops` (delivered 26 Oct) — two cost candidates must not share keywords. And check the
same morning's `content-ideas-<date>.md`: that lane already owned the DRAM-renewal and data-centre-levy
angles, which is why **no** Pocock candidate was added despite the signal being in the day's top four.

**Ledger.** The two never-delivered 31 Oct lines (the verbatim 16 Oct repeats) were pruned per Rule 72,
keeping a `.bak` copy; the 16 Oct originals remain, and the twin rule — not a ledger artifact — is what
keeps them off the same cycle.
