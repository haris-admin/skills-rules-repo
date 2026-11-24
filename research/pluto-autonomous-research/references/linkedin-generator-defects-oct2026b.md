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

---

## Rule 83 (Nov 1 2026) — the feed-reference strip must CLOSE the parenthetical it opened

`_strip_leading_feed_ref` drops a bookkeeping head joined to the headline by `:` or a dash. When the
head OPENED a parenthetical — `UPDATE to the 31 October feed (what changed: the London outage was …
not an unavoidable utility fault)` — removing the head left the closing `)` behind, so two of five
delivered display titles (the H3 Haris copies) ended on an orphan bracket. The hooks read clean, which
is why every existing gate passed: Rule 50 resolved the OPENING side (`_balance_fragment` loops on
unbalanced parens) but nothing re-balanced the text after a head was removed, and the display title never
passes through `_balance_fragment` at all.

**Fix:** count the head's own paren deficit and remove that many unmatched `)` from the tail, scanning
with a depth counter so a balanced pair inside the tail (`(Article 50(2) date)`) is untouched. Applied
inside `_strip_leading_feed_ref`, i.e. for every surface the function feeds (display title and hook via
`_short_title`) — the Rule 73/78 lesson applied at the source instead of per surface.

**Replay:** 47 titles / 8 days → **2 changed (both today), 0 regressions, 0 unbalanced after**.

**Practice note (Rule 45 recurrence, Cloud slot).** Today's five findings were 4 × CloudProof AU on a
Cloud & Infrastructure day, and the engine shipped **3/3 blog ideas on AI Agents & Governance**. The
own-pillar pool was genuinely empty: the only Cloud candidate with real hits (`sovereign-cloud-procurement`,
4) is RETIRED against a published post, `cloud-concentration-resilience` sat inside the 10-day window,
and `eval-egress-containment`'s 3 "hits" were context vocabulary (`egress` from the ACM's data-EGRESS
fees, `sandbox` from GovAI's Sandbox tier) — the Rule 49 class again, caught only by printing the
sentences the keywords fired in. Fixed by ADDING three subject-bound candidates for today's own signals:
`datacentre-maintenance-posture` (single-feed / LOTO'd feeder / PLC sensing; **10 hits today, 0 on eight
prior days** once the location noun `europe-west2` was dropped), `data-act-switching-charges`
(`switching charge`, `leidraad`, `egress fee`, `12 january 2027`; **9 / 0**) and
`provider-control-plane-compromise` (`idcf`, `206 of 495`, `portal authentication`; **6 / 0**).
No gate was loosened. The `content-ideas-<date>.md` lane covered the same four signals for the AML/
real-estate audience, so the curated section names the sequencing rather than suppressing the post.

---

## Rule 84 (Nov 1 2026) — run the hook guards on the FINAL text, at every return path

Two of five hooks left `_short_title` mid-clause: `…gated by IRAP: GovAI Hosting runs` (88 chars, `runs`
IS in `_DANGLE_VERBS`) and `…had virtual servers encrypted — backup coverage` (a bare noun phrase after
an em-dash). The verb guard at the slice stage had already run by the time the later completion steps
(`_complete_tail`'s Rule-65 token restore, the scaffolding pops) rebuilt the clause, so the classification
was correct but stale — Rule 44's lesson, three rules later.

**Fix:** two final-text helpers applied via `_finalize_hook()` at **all four** return paths of
`_short_title` (the `len(head) <= limit` early return, both delimiter-cut returns, and the final
`_complete_tail` return):

- `_drop_dangling_verb_tail()` — if the finished hook ends on a `_DANGLE_VERBS` token, drop the subordinate
  clause or the verb, keeping the result only when it still stands alone (>=30 chars).
- `_drop_dash_fragment()` — drop a trailing `— <1-4 tokens>` that carries no finite verb; a complete
  dash-joined clause (`UPDATE — the argument graduated from opinion to causality`) is untouched.

**Replay:** 47 titles / 8 days → **2 changed, 0 regressions, 0 still ending on a verb or an unbalanced
bracket.** The fix is deliberately at the exit, not at the slice, because every earlier guard can be
undone by a step that runs after it.

---

## Rules 85–87 — Nov 3 2026 (final-text guards, single-token verb test, weak-regulator dominance)

### Rule 85 — a single token is not a tail: `_tail_has_verb`'s suffix heuristic misclassifies plural nouns

**Symptom:** the day's #1 hook shipped as `Banks block third-party AI agents: five US and four Canadian
banks shut agent access to customer` — truncated one token short of the noun phrase.

**Cause:** Rule 65's noun-phrase completion refuses to append a token when `_tail_has_verb(t)` is true.
That helper's heuristic (`len > 3 and ends es|ed|ing|s`) is correct for a multi-token tail and wrong for a
single token: `accounts` ends in `s`, so the completion was rejected and the hook ended on `customer`.

**Fix:** `_is_verb_token(tok)` — for ONE token, only a known finite form (`_FINITE_VERBS`) or an
`-ed`/`-ing` participle counts. Used at the Rule 65 extension only; `_tail_has_verb` keeps its suffix
heuristic everywhere it inspects a *tail*.

**General rule:** a heuristic tuned on multi-token text is not valid unchanged on a single token. When a
guard is reused at a different granularity, re-derive it for that granularity rather than reusing it.

### Rule 86 — guards that need tokens AFTER a conjunction cannot see a hook ENDING on one

**Symptom:** `A contractor's personal Claude Code agent ran on the Pentagon's NIPRNet for two months and`
delivered as a hook.

**Cause:** every subordinate-tail guard (`_SUBORD`, Rule 44's widened re-check) is written as
`\s(?:and|but|or|while|…)\s+(\S+\s*){1,N}$` — it requires at least one token after the conjunction. A
clause whose LAST token is the conjunction matches nothing, and `_ends_on_verb` does not list coordinators.

**Fix:** `_drop_trailing_coordinator()` in `_finalize_hook`, applied to the final text at every return
path (Rule 84's lesson): strip a trailing coordinator/preposition (≥30 chars must survive). `_finalize_hook`
is now `_drop_dangling_verb_tail(_drop_trailing_coordinator(_drop_dash_fragment(text)))`.

**General rule:** for every "dangling X" guard, ask what the text looks like when X is the LAST token, not
only when X is followed by something.

### Rule 87 — a WEAK regulator mention must lose to an AI/agent subject, not only to a cloud one

**Symptom:** the SailPoint agent-governance finding (85% of APAC enterprises run agents, 5% have
governance tooling) pillared **Australian Fintech Regulation** and closed with an AUSTRAC CTA.

**Cause:** `pillar_for()` ranked `reg_weak` (a passing "APRA CPS 234" mention) above the AI vocabulary
*because the weakness check only had a cloud branch to lose to* (`if cloud-subject: Cloud` came first).
Rules 66/76/80 had each added a dominance check on one branch; the `reg_weak` branch had none for AI.

**Fix:** before `if reg_weak: return Fintech`, count AI/agent terms vs regulatory terms in the blob and
return **AI Agents & Governance** when `ai_n >= 3 and ai_n > reg_n`.

**Replay:** 9 retained research days → **1 pillar change** (today's SailPoint finding, intended), 0 others.

**General rule:** every "X loses to Y" rule needs a branch for each subject class the generator can
recognise, or the class with no branch silently inherits the default. When adding a dominance check,
enumerate the classes rather than patching the one that failed today.

### Practice note — the day's slate had three separate grounding defects

Nov 3 2026 ran on an agent-security corpus with no AU regulatory news (see the AMLHive content-ideas lane:
whole inbox byte-identical to the prior day). All three auto blog ideas failed a ground check:

| Candidate | Defect | Fix |
|---|---|---|
| `nhi-agent-identity` | gap cited AppViewX, a CSA "82%", an AI Bill of Materials and an agent kill switch — **all zero occurrences** in the corpus (the `82%` rows in mempalace-inputs are RBA rate-hike odds) | restated onto NIST's tenets, which the corpus carries (nist 7, agent identity 3, tenets 3) |
| `agent-incident-register` | gap claimed "EU confirmed an unreported agent incident"; the `incident report` keyword had actually fired on the NIPRNet 72-hour sentence | restated onto that sentence |
| `psp-regulated-software` | keyword list carried bare `payments`, which fired on "agentic payments and CDD" inside the NIST finding | keywords rebound to PSP/payment-service-provider vocabulary; scores 0 today, which is the honest answer |

The day's Cloud signal had no candidate at all, so `agent-discovered-exploit` was ADDED (mptcp 2,
"53 minutes" 2, kernel exploit 1, cve-2026-98432 1, patched kernel 1, go 1.24 1 — 0 on the eight prior
retained days) and twinned BOTH WAYS with `php-version-window-evidence` as one patch-window gap family.
Never loosen a grounding gate to fill a slot: three grounded ideas from two pillars beat a fabricated
third. Also prune a never-delivered title from the ledger (Rule 72) — this run pruned *From PSP to
Regulated Software…* and collapsed duplicate same-day rows (the recorder appends once per run, so three
generator runs in one morning write nine rows; dedupe by title keeping the earliest date).

**Hook replay today:** 47 titles / 8 days → **2 changed, 0 regressions, 0 still broken** (both changes are
the two defects above).

---

## Rules 88–89 (Nov 4 2026)

**Rule 88 — a CTA is READER-FACING copy, so the content firewall applies to the static constants.**
Every close in `CTA_BY_PILLAR` and `CTA_BY_PORTFOLIO` ended in one of Haris's own product names, and on
4 Nov the day's #1 Startup post shipped *"Modelling this for a cap table or an ESOP? That's what ExitLens
AU exists for."* Under the Data Mesh Group policy that is a hard breach on a personal channel. The blog
gap strings legitimately carry `(ExitLens AU)` as INTERNAL routing annotation, which is exactly why nobody
noticed the CTAs: the same file mixes internal annotation with publishable copy, and the constants sat in
the publishable half. Portfolio CTAs stay KEYED by product (that is internal routing) — their TEXT must
be product-free. Verify by grepping the day's file for every firewalled name and reading where each hit
lands: `Gap filled:` lines are internal, `Hook:`/`Angle:`/`CTA:` lines are not.

**Rule 89 — a bounded WINDOW that trims the left edge can cut inside a proper noun, and no right-edge
guard sees it.** `_hook_clause` kept the last six words before the number, so *"The West Australian
reports a float size around A$142bn"* became *"Australian reports a float size around A$142bn"* — a
sentence whose subject does not exist, and it passed every gate because the clause reads as complete
(it ends on a noun, not a verb). Fix: walk the left edge back while the retained head token is
capitalised and the token before it is capitalised or a leading article; the existing `lead` pop then
strips the article, resolving "The West Australian" → "West Australian". General rule: for every window
or slice, the check is what the cut REMOVED at each edge — Rule 36 guards the right edge of the same
function and the left edge had no equivalent.

**Replay:** 47 hooks / 8 days → 1 changed (the broken one), 0 regressions. The repaired stat then failed
`_hook_stat_ok` on title overlap, so the hook correctly fell back to title-only.

**Rule 90 (Nov 5 2026) — a stop-list of FUNCTION WORDS is only as complete as the defects that built it.**
`_TRAIL_COORD` (Rule 86) held the coordinators and the prepositions earlier hooks happened to end on, so
`without` was absent and the ETSI/TTC/TTA hook shipped as *"…a 3GPP-style global AI standards body
without"*. A hook that ends on ANY preposition is broken, so the set must enumerate the class, not the
history: `without, within, between, against, through, during, per, via, upon, onto, toward(s), across,
beyond, among, about, under, over, into, despite, since, until, versus` were added alongside the
originals. Same discipline as Rule 63 (labels) and Rule 75 (`_META_LABEL_TAILS`): when the guard is a
word list over a closed grammatical class, complete the class.

**Rule 91 (Nov 5 2026) — a slice can end on a PARTICIPLE whose complement follows, and every existing
guard is blind to it.** *"…while 59% have AI embedded"* shipped for *"…embedded in core processes"*:
`_ends_on_verb` does not treat a participle as clause-final (so Rule 32's verb-tail cut never fires),
Rule 65's noun-phrase completion refuses to extend past a function word (`in`), and the subordinate-tail
guards only match conjunctions FOLLOWED by tokens. Fix: `_extend_participle_complement(head, sliced,
limit)` — when the slice ends on a verb token (`_is_verb_token`) and the next source token is a
preposition, append the preposition plus up to three lowercase content tokens, bounded by `limit + 30`.
It must run AFTER `_complete_tail` because that function can rebuild the tail. General rule: an
adjective/participle that takes a mandatory PP complement is a truncation risk a verb-based guard
cannot see — check what the SOURCE says next, not just whether the slice reads as a clause.

**Replay (Rules 90–91):** 151 titles / 9 days → 4 changed (the two defects, each appearing twice in the
corpus), 0 regressions.

**Rule 92 (Nov 6 2026) — the blog repeat window was NARROWER than the topic cycle, so every title
returned verbatim as soon as it lapsed.** `repeat_blob` / `_ledger_recent` were built with `days=10`,
which is only two turns of the `date % 5` slot. On the Cloud slot of 6 Nov the auto-slate emitted
*Power, Not Land: The Data Centre Constraint That Will Re-Price Your Cloud* (delivered **16 Oct**, 21
days earlier) and *FIRB Is Not the Last Hurdle* (delivered **21 Oct**), and the registered twin gate
could not save either: `_repeat()`'s twin branch reads `repeat_blob`, so a twin that is itself outside
the window is invisible (the Rule 81 failure, one layer down). Both titles were fresh by every gate and
took slots #1 and #3. **Fix:** the blog repeat window is now 21 days (`days=21` for both the file scan
and the ledger) — four turns of the cycle. This does not reintroduce Rule 18/29d starvation because a
repeat was never *suppressed*: it ranks last (`t[5]`) and pads only when fewer than two fresh grounded
candidates exist, and Rule 39 already prefers two unwritten ideas to three with one the reader has seen.
General rule: a repeat window must be at least as long as the rotation period of the thing being
repeated; at 2× a 5-day cycle you have built a 10-day amnesia, not a dedupe.

**Replay (6 Nov, same run):** the third pick, *When Compute Goes to Market* (`compute-securitisation-
lockin`), was ungrounded — its only hit was `bookbuild`, fired on the **NextDC raid**, a different
company entirely, while its gap asserted a Firmus float the 14 Oct record says was withdrawn (Rule 57/58
class: an entity keyword drifting onto a co-occurrence). Three subject-bound candidates were ADDED
(`datacentre-firming-obligation` 9 hits, `datacentre-committed-capacity` 8, `datacentre-ownership-change`
7; 0 on the seven prior retained days), each verified by printing the sentence its keywords fired in.
Slate 16/21-Oct-repeat ×2 + ungrounded ×1 → 9/8/7 genuine fresh. `datacentre-firming-obligation` was
registered one-way to `datacentre-energy-grid`: the twin map holds one value per key, so a three-member
family (firming / energy-grid / grid-connection-financing) can only be partially closed — Rule 92's
window is the general protection. **Also:** when the day's regulator story is already owned by the
AMLHive lane (that morning's `content-ideas-<date>.md` shortlisted CDD-for-infrastructure-buyers,
beneficial-ownership aggregation *and* firming-as-land-due-diligence off the same three findings),
frame the blog on the buyer-side contract question and say so in the slate — same research, two
audiences, no double-publish.

**Rule 93 (Nov 7 2026) — Rule 75 fixes the COLON; a dash-joined title loses its figure one layer
later.** `_prefer_figure_clause` correctly dropped the `Counter-signal:` label, leaving *"the
compliance bill arrives before the penalty — TAB WA's AML uplift is already about A$10.9m with the
assessment still open"*. The ` — ` cut in `_short_title` then kept the fact-free first half and
shipped a 45-char hook with no number in it. **Fix:** `_prefer_figure_segment()` after
`_prefer_figure_clause()` — when segment 1 carries no digit, segment 2 does, and segment 2 starts
capitalised at ≥25 chars, hook on segment 2. Must-KEEP counter-example: `UPDATE — Digital Duty of
Care Bill clears the House…` (no digit in either half) is untouched. General rule: after every
stage that SELECTS a clause, ask whether a later stage can still re-select a weaker one.

**Rule 94 (Nov 7 2026) — attributive adjectives pass the `-ed`/`-ing` verb heuristic.** The OCC hook
shipped as *"…as a separate risk category — delegated authority"*: `_drop_dash_fragment` asks
`_tail_has_verb("delegated authority")`, which matches `-ed$` on the first token and calls an
adjective a predicate (the Rule 85 failure in a different helper). **Fix:** in `_drop_dash_fragment`
only, a tail of exactly TWO tokens where token 1 ends `-ed`/`-ing` and token 2 does not look verbal
is treated as attributive and cut. The two-token bound is deliberate: a three-token real predicate
(*"examiners flagged risks"*) must survive. General rule: a suffix heuristic tuned on clause-final
tokens will fire on pre-nominal modifiers — bound the shape, don't widen the heuristic.

**Rule 95 (Nov 7 2026) — the third instance of context vocabulary on the SAME candidate.** Rule 27
had already stripped `austrac`/`tranche 2`/`real estate`/`aml` from `tranche2-property` and left
`remittance` in place. Block's DPA finding contains *"For an Australian payments, remittance or BNPL
business…"* — sector context in a story about an ineffective AML program — so the candidate fired,
and the generator produced **"AUSTRAC's Western Union Probe: What Property Businesses Should Read
Into It"**: a probe that exists in no corpus, no research finding and no inbox item. `western union`,
`money transfer operator` and `money laundering probe` were all ZERO. **Fix:** bare `remittance`
removed; the candidate may only fire on its actual subject. General rule: when a candidate is
re-bound for false positives, re-read the WHOLE list for sector nouns, not just the keyword that
fired last time. Symptom to watch: a candidate that produces a *named subject* ("X's Y probe") from
a day whose findings never name X.

**Rule 96 (Nov 7 2026) — a product lives inside a pillar, so a pillar match does not validate a
narrow product CTA.** Rule 67 gates `CTA_BY_PORTFOLIO` on `PORTFOLIO_PILLAR[pf] == pillar`; Tapease
maps to *Australian Fintech Regulation*, so Block's AML deferred-prosecution finding (`portfolio_hit:
Tapease`) closed with *"Building payment or marketplace flows? Dispute evidence is a design decision"*
on a story about AML program effectiveness. **Fix:** `CTA_PORTFOLIO_GATE` — a narrow product CTA must
find its own vocabulary in the finding (`Tapease`: dispute / chargeback / refund / merchant /
marketplace) or it yields to the pillar CTA. `_pick_cta()` now takes the finding blob. General rule:
`portfolio_hit` says which product is AFFECTED; a product CTA may only close a post about that
product's own surface.

**Replay (7 Nov 2026):** 47 finding titles from the last 10 research days → **2 changed, 0
regressions** (both intended: the OCC enumeration cut and the TAB WA figure segment). Blog slate
went 3 → 2 after Rule 95, and the never-delivered Western Union title was pruned from
`.blog_title_history.jsonl` (Rule 72), keeping the two delivered titles. Third blog idea was added
by hand at curation (penalty arithmetic: US$964m gross → US$764m net), not by loosening a gate.

**Data-integrity note (7 Nov 2026):** the `austrac-infringement-notices` gap text quoted *"a
supervised population estimated near 100,000"* plus a per-industry enrolment split (accounting ~50%,
real estate ~40%, law firms 12-14%, jewellers ~10%). Those percentages are RETIRED — the denominator
was never AUSTRAC-published — and the standing rule is roll counts only (62,710 enrolled at 20 Oct
2026). Gap text rewritten to counts-only with an explicit "do not quote a %" instruction. The same
day's `morning-briefing-<date>.md` still printed 40,630/100,000 = 40.6% with a parse-failed warning:
briefing-lane defect, flagged in the day's ideas file, not fixed here.

## Rule 97 (Nov 8 2026) — a regulator's list of the SECTORS IT SUPERVISES is context vocabulary, and so is a market attribute used as a differentiator

Two candidates grounded the whole blog slate on a single term each, and both terms were
vocabulary from *another* domain:

- `insurer-as-regulator` fired on bare `insurer` from APRA's supervisory **scope** sentence —
  *"after reviewing large banks, insurers and superannuation trustees"*. APRA naming the sectors
  it supervises is exactly like a byline: it says nothing about insurance underwriting as a
  private enforcement channel. Re-bound to the channel itself
  (`underwriting, cyber insurance, insurance policy, insurability, policy wording, premium
  loading, insurance market`); today 1 → 0, and all seven prior retained days were 0 on both
  lists, so nothing genuine was lost.
- `aml-data-residency-cloud` fired on `data residency` from a **venture-trend** sentence —
  *"vertical ai, deep tech, data residency, and unit-economics-driven growth emerging as key
  differentiators"* — i.e. an investor story about positioning, not about where AML records sit.
  `data residency` dropped; the candidate keeps its genuine 2 Nov grounding (`record-keeping`,
  `aml/ctf record`) and correctly does not fire today. This is the *fourth* re-binding of this
  one candidate (Rules 27, 29e, 53) — the list had already lost `cloud`, `record`, `vendor`,
  `offshore vendor`. General rule: a candidate about a LOCATION or an ATTRIBUTE must be bound to
  phrases that name the record/obligation, never to the attribute's name.

**Diagnostic that generalises:** print the sentence each keyword fired in and ask "is this
sentence ABOUT my candidate?" — not "does the word appear". A sector noun inside a scope list and
a market attribute inside a trend list both read as hits to `_subject_kw_hits` and as nothing to
a reader.

**Practice note (Rule 45 recurrence, Agentic-AI cycle, eighth instance):** with both false
positives confirmed, the fresh grounded pool for the day was **ZERO** and the padding path handed
back `aml-data-residency-cloud` — a verbatim repeat of 2 Nov, six days old, inside the 21-day
window, surviving only because `_repeat` ranks a repeat LAST rather than dropping it and fewer
than two fresh candidates existed. The signal to act on is the empty pool, not the repeat: four
subject-bound candidates were ADDED for the day's own signals — `agentic-intrusion-deception`
(6 hits today / 0 on seven prior days), `five-minute-credential-compromise` (5 / 0),
`provider-continuity-planning` (3 / 0), `agent-observability-consolidation` (4 / 0). Never
loosen a grounding or repeat gate to fill a slot.

**Cross-lane note (now the normal case, not the exception):** with the whole email/inbox layer
stale (Perplexity trial lapsed 6 Nov, every Filter channel hash-identical for a week), the
AMLHive ideation lane now sources from the *same* `research_<date>.json` every morning. On 8 Nov
it had already worked the five-minute Key Vault event (#5, held as a runner-up), the 84/10
authority gap and the APRA 80/55 split. Read `content-ideas-<date>.md` BEFORE finalising the
blog slate, and differentiate by ARTEFACT and READER, not by signal: harishabib.au = the
engineering control/runbook; amlhive.com.au = what the principal's CDD record shows afterwards.
State the split in the slate so the drafting lanes cannot merge the two.

## Rules 99–101 (Nov 9 2026)

**Rule 99 — the empty-slate fallback was the only blog path with NO gates, and it is where the
"off-pillar repeat" class finally surfaced.** When `picks` came back empty, `if not blog_ideas:`
iterated `BLOG_CANDIDATES` and applied exactly one test (`key in KNOWN_BLOGS`) — no pillar, no
freshness, no repeat, no grounding. On a Startup & VC day whose own pillar had zero fresh grounded
candidates it shipped three AI-governance titles, including **"Autonomy Tiers", delivered verbatim
on 7 November, two days earlier**. The scored path was working correctly the whole time; the
fallback quietly bypassed it, which is why the defect survived nine Rule-45 cycles of "add
candidates" fixes. Fix: order the fallback by tier — own pillar before any pillar, grounded before
ungrounded — and run `_fresh`, `_repeat` and the twin gates inside it. A slot filled off-pillar AND
off-window is worse than an honest blank, because the reader cannot tell a fallback from an idea.
General rule: **every path that emits a reader-facing pick must pass the same gates as the
preferred path**; "last resort" means lower-ranked, never ungated. Note the corollary for
diagnosis: when a stale-repeat appears after the gates were "already fixed", read the *branch*, not
the gate list.

**Rule 100 — a shared CTA tier is domain-mixed by construction, and the pillar must be able to
speak first.** On a six-post single-pillar Startup & ESOP day the tiers above ran out, and the
shared alternate list closed the Heidi restructuring post with *"Where is this landing in your own
compliance program — policy, process, or evidence?"* — a reporting-entity close on a founder story.
The compliance-program line is correct for Fintech and AI-governance and wrong for ESOP. Fix:
`CTA_ALTERNATES_BY_PILLAR` (pillar-specific alternates tried before the shared list) plus
`CTA_ALTERNATE_PILLARS` (a shared alternate declares the pillars it suits; unlisted lines suit
all). General rule: Rule 63's "the pillar records what the post is ABOUT" applies to the CLOSE as
well as the pillar assignment — a CTA is reader-facing copy and carries a domain by itself.

**Rule 101 — a verb-FORM token that heads a noun phrase is a noun, and `_ends_on_verb` was
detecting form only.** "Heidi cuts 18% of staff and loses two of three cofounders six weeks after
a A$475m raise" is 88 chars, i.e. inside the 100-char limit, so `_short_title` returned it
unchanged — and `_finalize_hook`'s dangling-verb guard then cut `raise` (listed in
`_DANGLE_VERBS`) and shipped the hook as "…after a A$475m": a complete title truncated by a guard
that never asked what the token *was* in that sentence. Fix: `_ends_on_verb` returns False when the
preceding token is a determiner or a currency/quantity form — "a raise", "the cut", "A$475m raise"
are noun heads, so the clause stands. Harness: `_short_title` over all findings in the 8 retained
research days, old guard vs new — **50 titles, 1 changed, 0 regressions**; must-trim counter-
example ("…gated by IRAP: GovAI Hosting runs") still trims, which proves the guard is narrowed, not
disabled. General rule (Rule 95's lesson, one layer up): every "dangling X" test must branch on the
token's ROLE, and a length-capped path can still be damaged by a post-processing guard — check the
final text at the surface the reader receives.

**Rule 102 (Nov 10 2026) — fixing a fallback's *ordering* is not fixing its *gates*; the
grounding tier survived Rule 99.** Rule 99 rebuilt the empty-slate fallback as four tiers
`(own pillar, grounded) → (any pillar, grounded) → (own pillar, ungrounded) → (any pillar,
ungrounded)`. On 10 Nov every grounded candidate was unusable — `sovereign-cloud-procurement` is
PUBLISHED (it sits in `KNOWN_BLOGS`), and `oaic-adm-disclosure` (delivered 20 Oct),
`asx-escrow-composition` (24 Oct) and `five-minute-credential-compromise` (8 Nov) were all inside
the 21-day window — so tiers 1 and 2 returned nothing and the fallback shipped tier 3 and tier 4
titles: memory poisoning, control channel and PSP licensing, each with ZERO term of its own in a
corpus about the AU ADM deadline, EU Article 50 and a CJEU copyright opinion. The output looked
exactly like a normal slate (no `(signal matches: N)` suffix is the only tell). Fix: the tiers are
now `(True, True)` and `(False, True)` only, with a comment naming grounding as a gate. Verify any
generator change by printing, for each emitted blog idea, the terms that fired and the sentence
each one fired in — an idea with no fired term is a template.

**Rule 103 (Nov 10 2026) — the truncator cuts on more delimiters than the repairer knows about.**
`_short_title` slices at any of `" ,;:-—–"`, but `_complete_tail`'s "drop a list-opener clause"
branch searched `": "` alone. A title written `headline — disclosure duties, sandboxes and an
employment safety net` was therefore sliced to "…legislation — disclosure duties" and the branch
saw no delimiter, so the hook shipped as the first item of a truncated list — the Rule 69 defect
class reaching the surface through a separator the fix never covered (the same lesson as Rule 56,
one layer down: a separator-specific fix is only as general as the separators the pipeline emits).
Fix: find the LAST match of a SPACED `:`/`—`/`–`/`-` separator and take the tail after the
separator's end (`m.end()`, not `idx + 2` — the em-dash separator is three characters). An
unspaced hyphen is a compound noun and is deliberately not a boundary. Guards unchanged: only when
the slice is truncated, the retained clause is ≤4 tokens, it carries no finite verb (exact-token
`_has_finite_verb`, so "duties" is not a verb — Rule 85), and the pre-clause is ≥30 chars.
Harness: `scripts/hook_baseline.py` before/after over 48 findings from the 8 retained research
days → **1 changed, 0 regressions**; the changed hook is the target, and every evidence-carrying
subtitle (": Cloud Concentration as a Financial-Stability Risk") is untouched.

**Practice note (Rule 45 recurrence #10, Nov 10 2026):** with the pool empty the fix was three
subject-bound candidates for the day's own signals, each keyword verified by printing the sentence
it fired in: `eu-article50-marking-evidence` (5 hits, `article 50`/`marking/watermarking`/`digital
omnibus`), `ai-training-output-liability-split` (5, `c-250/25`/`advocate general`/`memorisation`/
`retrieval-augmented`/`opt-out register`) and `us-ai-watchdog-hollowing` (4, `caissi`/`permanent
director`/`standards and innovation`). Replay across 3–9 Nov: 0 everywhere except the Article-50
family's 3 hits on 5 Nov, the day the cliff was first flagged and no idea was emitted for it. The
three never-delivered fallback titles were then pruned from `.blog_title_history.jsonl` (Rule 72,
backup taken first) before re-running, and the ledger checked for duplicate rows afterwards.

**Rule 89 (Nov 11 2026) — the repeat window cannot be the defence against a title's own cycle.**
The 21-day window (Rule 88) is four turns of the `date % 5` topic cycle, so a title delivered on a
cycle returns on the FIFTH turn — 26 days — no matter how much the window is widened, and widening
again only moves the problem one cycle out. On 11 Nov the Cloud slot's entire fresh grounded pool
was exactly the two titles delivered on 16 Oct (`datacentre-energy-grid` "Power, Not Land" and
`cloud-concentration-resilience` "The Missing Substitutability Test"), i.e. a verbatim repeat slate
of one day 26 days earlier. The fix is the standing Rule 45 practice, stated here as the general
rule: **freshness is not a guarantee a long window can supply — the own-pillar pool must hold a
grounded candidate that is bound to a signal the slate has never used.** Run the pool count BEFORE
accepting a slate: enumerate every candidate in the day's pillar, print `today` hits and `prior`
days fired, and if the fresh grounded set is empty, ADD subject-bound candidates from the day's
own sentences. Three were added (`ai-capex-repricing-risk` 5 hits;
`ai-commitment-off-balance-sheet` 3; `datacentre-import-content` 3; 0 on all seven prior retained
research days), each keyword list checked against the sentence it fired in — bare `imported` was
dropped because it fires on any trade story, while `building construction` and
`0.2 percentage points` carry the subject. Deliberately NOT twinned with the older credit/capex
candidates: those gaps describe different artefacts (a vendor bond mark; a capex-to-cash-flow gap)
whereas the new ones describe a contract clause and a commitment schedule — register twins only for
one gap, or the map suppresses legitimate picks.

*Harness note:* the diagnostic that makes this cheap — import the module with
`importlib.util.spec_from_file_location` (main is `__main__`-guarded), rebuild the corpus exactly
as `main()` does, then tabulate `_subject_kw_hits` per candidate for today and every retained
`research_*.json`. Slice the date as `basename[9:19]` (`research_` is 9 chars) — a `[7:17]` slice
silently returns garbage keys and every prior-day count reads 0, which looks like perfect
grounding.

---

## Rules 104–105 (Nov 12 2026)

### Rule 104 — a regular-form-only verb test is not a verb test

`_is_verb_token()` counted a known finite form or an `-ed`/`-ing` participle. English's most
common past tenses are IRREGULAR, so the single token `meant` was classified as a NOUN. On a
title ending `…broking was never |meant to be captured|` the 100-char slice landed mid-word
(`mean`), `rsplit(" ")` dropped it, Rule 65's completion then REFUSED to put `meant` back
because it "was a verb", and the hook shipped as `…broking was never`. A second wall sat
behind it: `_extend_participle_complement` broke at the auxiliary in a passive infinitive
(`meant to **be** captured`), so even a correct slice could only ever reach `…meant to`, which
`_drop_trailing_coordinator` then stripped back to `…never meant`.

Three fixes, all narrow:
1. `_IRREG_VERBS` gains the past forms that appear in regulatory copy (`meant`, `built`, `paid`,
   `bought`, `sold`, `lost`, `sent`, `spent`, `thought`, `told`, `began`, `became`, …). Add to
   the set when a new irregular shows up; never special-case the hook builder.
2. A verb token followed by a PREPOSITION is not clause-final — `meant to`, `applies to`,
   `rests on` all take a complement, so Rule 65 puts the token back and lets the completion
   step finish the phrase.
3. `_extend_participle_complement` accepts `_AUX_TOKENS` (`be`, `been`, `being`, `not`) after
   the preposition, then the participle that closes the passive, then stops.

Same run: a slice can read grammatically complete and still lose the claim. `…the case is about
controls` is a finished clause, so every guard passed — but the title was `…about controls,
**not wording**`, and the contrast IS the point. `_complete_tail` step (2b) re-attaches a
trailing `, not X` / `, rather than X` / `, but X` appendage when it carries no finite verb,
is ≤ 30 chars and stays inside `limit + 30`.

*Harness:* replay every finding title in the last N retained `research_*.json` through OLD and
NEW `_short_title` and diff. **53 titles / 8 days → 3 changed (2 intended, 1 duplicate), 0
regressions**, with must-KEEP counter-examples asserted unchanged: `CoreWeave below 80c at
~15% yield`, `…: Cloud Concentration as a Financial-Stability Risk`, `…six weeks after a A$475m
raise`, `AI Kill Switch and Data Centre Control Bill 2026`.

### Rule 105 — a regulator acronym is context vocabulary, never a subject

`spf-multiparty-liability` ended its keyword list in bare `afca`. It fired exactly once, on
`…and follows an April 2025 AFCA determination` inside the Macquarie Welcome Rate finding — a
savings-rate mis-selling case with no scam, no digital platform and no apportionment in it.
`afca` is a name that appears in ANY banking-conduct story (same class as `asic`, `rce`,
`gartner`); the phrase that identifies the subject is the mechanism (`scam dispute`,
`scam compensation`, `report a scam`). Replay both directions: today 1 → 0, and 0 on all seven
prior retained days with either list — the false hit was the candidate's only ground, so the
honest read is "this candidate has no grounded day in the window", not "the gate killed it".

### Practice note — cross-lane dedupe and the firewall at curation time

Two lanes write content from the same day's corpus: this generator (LinkedIn + harishabib.au)
and the 05:45 AMLHive content-ideas cron. On a single-topic FinTech day they will select the
SAME three findings. Read `content-ideas-<date>.md` BEFORE curating and pick the angles the
other lane did not take — here the AMLHive slate owned the real-estate framing of ASIC's
lead-generation review and AUSTRAC's asset-finance clarification, so the curated set went to
licensing economics, cross-jurisdiction perimeter and the OAIC deadline instead.

The generator's gap texts also carry internal provenance annotations (`(PayLicence AU)`,
`(AML Hive)`). `pluto-content-firewall` forbids naming any Haris product in the
harishabib.au / LinkedIn stream, so the curated section must strip them and say so explicitly —
a gap text pasted straight into a post is a firewall breach, not a formatting slip.

### Rule 106 — the corpus contains OTHER LANES' ideas, so a "signal match" can be an echo

`get_signals_from_files()` reads `mempalace-inputs/*.md`, which includes the AMLHive
content-ideas lane's own files (and their `[AMLHive Content Idea]` headings). On 12 Nov the
`oaic-adm-disclosure` candidate scored "signal matches: 1" — and that one hit was the OTHER
LANE'S IDEA HEADING from 10 November, not a news signal about the OAIC. A candidate grounded on
another lane's prose is grounded on a restatement of our own prior work; it can still be a valid
idea (a dated statutory deadline is a deadline whether or not today's RSS mentions it), but it
must not be reported to Haris as fresh signal.

Check before delivering: print the sentence each keyword fired in AND its file, and label the
idea's provenance — live signal, prior research record, or cross-lane echo. The same rule makes
cross-lane dedupe cheap: if the hit came from `content-ideas-<date>.md`, that lane already owns
the angle and this slate should take a different one.

### Rule 107 — a slice can stop ON a preposition, and every existing extension helper is gated on a VERB

The two completion helpers each have a precondition that excludes this case by construction:
`_complete_tail` (Rule 65) only fires when the next token is a single lowercase content word,
and `_extend_participle_complement` (Rule 89) only fires when the slice's LAST token is a verb.
On 13 Nov the BluePhishing title cut at 100 chars and landed on `inside`, so both helpers
returned unchanged and `_drop_trailing_coordinator` did not strip it either — `inside` was not in
`_TRAIL_COORD` — and the hook shipped as "…creates working agent identities inside".

Fix: `_complete_trailing_prep(head, sliced, limit)` puts the preposition's OBJECT back (≤3 content
tokens, stop at punctuation/punctuation-that-opens-a-clause/verb, inside limit+30), wired into
both slice return paths plus the main path before `_extend_participle_complement`. The delivered
hook completes to "…inside a victim tenant" (118 chars). `_TRAIL_COORD` also gained the locative
prepositions (`inside`, `outside`, `behind`, `below`, `above`, `along`, `around`, `throughout`,
`amid`, `past`) so a failed extension still drops rather than ships the preposition.

General rule: for every "dangling X" guard, ask which stage gates on X and which stage RECOGNISES
X. The guard ran; its trigger set did not contain the token class. Enumerate the closed set from
the grammar (the prepositions that can take an object), never from the defect of the day.

Replay: 48 titles / 8 days → 0 flagged (ends-on-prep / ends-on-verb / ends-on-punct checks).

### Rule 108 — `.get(key, default)` does not protect against an explicit JSON `null`

`himalaya envelope list --output json` returned an envelope whose `from.name` was present and
`null`. `from_field.get("name", "")` returns the DEFAULT only when the key is absent, so
`from_name` was `None` and `"Perplexity" in from_name` raised `TypeError` out of `main()` before
any output file was written — the whole cron produced nothing while the run looked like it had
started normally. Coerce every external-payload field with `(value or "")`, not a `.get` default.

This is the Rule 30 class one layer down: Rule 30 made himalaya FAILURES non-fatal (swallow the
exception, return ""), which is why the crash moved to the payload PARSING instead of the call.
When hardening an external source, harden both the transport and the shape of what it returns.

### Rule 109 — the context-vocabulary defect keeps returning through new words (Rule 49/102 recurrence)

`agent-control-channel` carried `["telegram", "control", "hijack", "phishing", "okta",
"credential"]`. On 13 Nov its ONLY hit was `phishing`, from the BluePhishing story — OAuth consent
phishing against an agent identity, with no human control channel anywhere in the corpus
(`telegram`, `control plane`, `control channel`, `hijack` all ZERO). The candidate was ranked #1
of the blog slate on a word that appears on every security day. The file had ALREADY recorded that
bare `credential` in this same list "has fired off unrelated stories" — the note was written and
the list was left alone, so the defect simply changed word.

Fix: bound to the control plane itself (`telegram`, `control plane`, `control channel`, `command
channel`, `chat interface`, `whatsapp`, `slack`, `human control`, `hijack`); today 1 → 0, and the
candidate keeps its genuine prior grounding. Practice: when a comment records that a keyword is
dirty, remove it in the SAME edit — a documented-but-live context word is a scheduled recurrence.

That free slot went to `nhi-agent-identity` (genuine `agent identity` hit), whose gap then had to
be REWRITTEN (Rule 58) from the NIST NCCoE story to today's BluePhishing evidence, and the other
two gaps in the slate were likewise restated onto today's sentences — a candidate that is fresh
and grounded can still carry a gap describing a source the day never mentioned.

---

## Rules 110–112 (14 Nov 2026) — Startup & VC cycle, 6 findings / 5 high-confidence

### Rule 110 — a delimiter cut can leave a subordinator plus one adjective, and no existing guard sees it

Delivered hook: `Corporate VC retreats (NAB Ventures in doubt) while public`. The title read
`Domestic capital is being restructured: corporate VC retreats (NAB Ventures in doubt) while
public, sovereign and specialist money steps in (…)`. Two independent failures stacked:

1. `_short_title`'s delimiter cut takes `max(rfind(": "), rfind(", "), …)` inside `head[:limit+1]`.
   The first comma inside the window sat after `public`, so the slice stopped there — inside an
   ENUMERATION, one token past the subordinator.
2. Rule 44's subordinate-tail sweep (the guard that exists for exactly this shape) runs BEFORE
   the delimiter cut and its `_tail_has_verb` suffix test called `steps` a verb (`s$`), so the
   8-token `while public, sovereign and specialist money steps in` read as a finished clause and
   survived. `_short_title` had already passed the point where it could be re-checked.

The general lesson: a backstop that runs BEFORE a later step which shortens the text must be
re-evaluated AFTER it (Rule 44's own lesson, one layer down) — and "the tail contains a content
word" is not a test for "the tail states something". Both hooks ended grammatically tidy; only
reading the delivered line shows the missing predicate.

Fix: `_drop_unpredicated_subord_tail()` wired into `_finalize_hook` (so it covers every
`_short_title` return path): a `while|whereas|though|although|because|since` followed by ≤4
tokens with no finite verb is dropped with the clause. Replay 48 titles / 8 days → 1 changed,
0 regressions, 0 flagged hooks. Implementation note worth keeping: the first cut of this helper
took `text[m.end():]` for the tail, which is EMPTY when the match runs to end-of-string, so the
guard silently no-oped and the replay still showed the broken hook — capture the tail as the
regex GROUP. A guard that never fires and a guard that never matches look identical from the
outside; assert on the transformed string, never on "the function ran".

### Rule 111 — `capital 49` is an investor, not a subject: a keyword fired on a different company's round

`tokenised-rails-licensing` ("Stablecoin Rails Still Need a Licence: The Boundary Metal Landed
On") shipped as blog idea #3 on keywords `capital 49` and `loong wang` — both of which fired on
the ALTA Series A story (Capital 49 is an Alta investor; Loong Wang an Alta co-founder), while
the title and gap described Metal's ~US$50m round from a September signal. `metal` and
`stablecoin` were ZERO in today's research corpus. This is Rule 49 one layer down: the keyword
named a co-occurring ENTITY, not the subject, and the entities that co-occur with a funding story
(investors, founders, vehicles) are the worst possible anchors because they recur across every
deal in the same syndicate network.

Fix: RE-BOUND the candidate to the subject that actually carries the signal —
`compliance-as-product-rail`, keywords `alta`, `compliance specialists`, `compliance-first`,
`compliance-focused`, `onboarding banks and payment providers` (5 hits today, 0 on 7–13 Nov), and
the gap REWRITTEN onto today's use-of-proceeds sentence (Rule 58). Practice: print the sentence
each keyword fires in before believing a hit count — an investor name in a syndicate list is
proof the candidate is about somebody else's deal.

### Rule 112 — a gap can survive a grounding fix: check the FIGURES the gap asserts, not just the keywords

`startup-cgt-carveout-draft` was correctly grounded (`ibcc`, `vclp`, `esvclp` all fire) yet its
gap asserted "the September exposure draft … 3-year hold, 15-year eligibility, lifetime cap gone,
$50m revenue cap, removal of 'supporting R&D activities'". In the day's corpus every one of those
figures was ZERO: `exposure draft` 0, `3-year` 0, `15-year` 0, `lifetime cap` 0, `revenue cap` 0,
`supporting r&d` 0 — the day's signal is a BILL introduced 27 Oct, before the House, not
assented, with the IBCC parameters PwC described. So the idea was grounded on its keywords and
fabricated on its evidence (Rule 34's figure check applies to the GAP as well as the title).
Rewritten onto today's sentences, it went from 4 signal matches to 7 — the corpus-consistent gap
is also the better-argued one.

Same class in `bank-cvc-retreat`: `nab ventures` fired (2) while the gap carried "biggest
restructure since 2017 (2,500 jobs)", "redundancy or redeployment", "portfolio companies told the
investment team would be disbanded" — all absent from the corpus. Restated onto the day's
NAB-Ventures/Andrew-Irvine sentence plus the sovereign-money sentences that ARE there. And
`au-retail-offshore-allocation`'s gap still described the 3 Nov Reuters *expectation* story
(Sharesies, CommSec, A$142bn) after the day had the actual S-1 pricing — keywords retargeted to
`australian retail offer`, `class a shares`, `controlled company`, `1.404trn`, `closes 17 november`
(1/1/1/2/2 hits today, 0 prior). It stayed suppressed by the 10-day ledger (verbatim 4 Nov
delivery) and that is the correct outcome — fixing a gap does not license a repeat.

### Practice note

Blog pool after fixes: CGT bill-stage (7 matches), `compliance-as-product-rail` (5),
`bank-cvc-retreat` (4) — three fresh, grounded, corpus-consistent ideas on a day whose 6 findings
were all venture-market stories. No gate was loosened and no candidate was padded in. Curation:
the AMLHive 05:45 lane had already taken the Alto/Metal-compliance angle from the other side
("Compliance-First Is Not a Control: The Fintech Rail Behind Your Buyer's Deposit"), so the blog
angle was kept on the FUNDRAISING/licensing boundary rather than CDD evidence, and the
`(TokenPilot AU + PayLicence AU)` / `(ExitLens AU)` provenance annotations were stripped from the
delivered text per `pluto-content-firewall`.

---

## Rule 113 — 15 November 2026: three defects on an AI-Regulation day

**113a — a NUMBER before a verb is not always a quantity (Rule 101 one layer down).**
`_ends_on_verb` refuses to treat a token as clause-final when the preceding token is a
determiner or matches the quantity regex, because "a raise" / "A$475m raise" are noun heads
(Rule 101). "Article 10 bans dark patterns outright" has `10` before `bans`, so the quantity
branch called `bans` a noun head and the hook shipped ending on the finite verb. An instrument
reference (Article 10, Section 12, Point 13, Annex III, Measure 3.4, Rule 6, CP 392, Table 6)
carries a number that belongs to the NAME. Fixed with an explicit `_instrument_ref` test on
`words[-3]`; the quantity branch is skipped only for those nouns.

**113b — trimming a dangling verb backwards can produce something worse than the slice.**
With `bans` finally recognised, `_drop_dangling_verb_tail` cut it and shipped "…— Article 10",
a dangling instrument reference that states nothing. Every existing guard trims backwards;
none repairs FORWARD. Added `_extend_verb_object(head, sliced, limit)`: when the slice ends on
a finite verb (or its third-person form) and the SOURCE still carries the object, pull up to
four content tokens back in, inside `limit + 30`. Cutting the verb is now the fallback for when
the object genuinely ends the source. Applied at every `_short_title` return path (the two
delimiter paths and the word-slice path), in the same position as
`_extend_participle_complement` — Rule 44/68's lesson: repair the text the reader receives.

**113c — a bare label needs its last word in `_META_LABEL_TAILS`, and `check` was not there.**
"Counter-signal reality check: the AI Act's enforcement machinery is fully built…" shipped with
the label as the hook because Rule 75's condition (b) tests the label's LAST word, and the set
held `counter-signal` and `reality` but not `check`. Added `check` / `reality check` /
`signal check`. Rule 63 practice applies: extend the list when a new bare label appears, never
special-case the hook builder. After the fix the hook became "The AI Act's enforcement
machinery is fully built and almost entirely unused".

**Replay:** `hook_replay.py` (scratch harness: every `###` title from the last 8
`linkedin-ideas_*.md` files plus all `BLOG_CANDIDATES` titles = 175 titles) — **2 changed,
0 regressions**. Both changes are the two defects above, and both read better than the input.

**Practice note (Rule 45 recurrence #12 — the AI-Regulation cycle).** After the automatic
slate ran, the blog block held ONE idea and it was doubly wrong: `aml-readiness-evidence-gap`
had one hit, bare `beneficial ownership` lifted from New York's RAISE Act (an AI-model
registration story), and its gap asserted an "AML Readiness Report" with five percentages
(65.6 / 34.4 / 75.4 / 56.5 / 18%) plus a "31-point" gap — all ZERO across the retained
research corpus (Rule 34/110: a gap can be grounded on keywords and still FABRICATE its
figures). Fixed the candidate (gap restated onto the verification-versus-program distinction,
dirty keyword removed in the same edit) and then ADDED four subject-bound candidates for the
day's uncovered critical signals:
`art50-deployer-territorial-reach` (5 hits, 0 on 8–14 Nov), `dfa-three-surface-interface`
(5, 0), `sandbox-exit-report-evidence` (4, 0) and `apra-ai-stress-test-register` (3, 0).
Two bare context tokens were REMOVED during grounding (`deployer` fired 1 on 13 Nov,
`regulatory sandbox` 1 on 10 Nov). Result: 3 blog ideas, all in the day's own pillar, all
fresh, all grounded — no gate loosened.

**Curation:** the 05:45 AMLHive lane had already taken vendor attestation (EU exit report →
eKYC/CDD), service-provider outsourcing (APRA 80/100), agent-as-counterparty (Art 50), the
enforcement counter-signal, identity-provider consolidation and beneficial ownership. The
harishabib.au slate took the angles it did NOT: deployer-side territorial reach and the
provider-watermark-is-not-a-defence point, the three-surface stacking problem, and the sandbox
as an evidence instrument. One superseded title ("Identity Verification Is Not an AML
Program: The 31-Point Readiness Gap") was written to the ledger by the first run and never
delivered — pruned per Rule 72, and the `(FinAI File AU)` / `(PayLicence AU)` / `(CloudProof AU)`
provenance annotations stripped from the delivered text per `pluto-content-firewall`.

**Practice note (Rule 45 recurrence #13 — the Cloud cycle, 16 Nov 2026).** The auto slate emitted
ONE blog idea and it was a verbatim repeat: `datacentre-energy-grid` ("Power, Not Land"), delivered
16 Oct, 31 days / six turns earlier on the same `date % 5` slot. It passed `_fresh()` because the
21-day window and the ledger window both end at 21 days — the ledger still held the 16 Oct row, so
the information was present and simply outside the gate. The 11 Nov curated note had already refused
to widen the gate for the same candidate at 26 days; the standing fix is the same: **ADD
subject-bound candidates for the day's own signals, never widen a repeat gate**. Three were added,
each with three or more corpus-exclusive terms: `grid-ibl-ride-through` (5 hits: `ride-through`,
`30mw`, `inverter-based load`, `combined-nameplate`, `phase-angle`), `saas-control-plane-split`
(5: `automated health checks`, `exchange online`, `mo1550821`, `defender for office`,
`azure status`) and `social-licence-levy` (5: `3,000 per megawatt`, `community benefit fund`,
`statement of expectations`, `rockliff`, `megawatt of contracted energy`) — every term 0 hits
across the seven prior retained research days (9–15 Nov) and firing only on today's sentences.
Keyword counts were chosen so the three new candidates each carry 5 hits and out-rank the 4-hit
repeat on the existing sort, which removes the repeat WITHOUT touching a gate. The never-delivered
16 Oct title row for today, written by the first run, was pruned per Rule 72 (backup kept).
Curation split the day from the 05:45 AMLHive lane, which had taken the same Microsoft 365 outage
from the CDD-record angle ("The 20-Hour Outage Test"); the blog slate took the dependency-map
angle instead. Live-site check used `harishabib.au/blog/` hrefs (36 posts, no sitemap.xml).

## Rules 114–116 — 17 Nov 2026

**Rule 114 — the accountability regime is fintech regulation.** `pillar_for()`'s product early
return gave a pure APRA/ASIC FAR-reporting story the pillar "AI Agents & Governance" and a
governance CTA, because the research mapped it to FinAI File AU. Rule 67 fixed this for AML
titles and Rule 76 for AML-dominant bodies; FAR is a third subject family. Added
`financial accountability regime|far reporting|accountable person|accountability map` to the
fintech-subject title check. `apra` alone is deliberately NOT added — APRA-anchored
cloud-prudential findings (CPS 230) are legitimately Cloud & Resilience. Result: today's FAR
finding pillared Australian Fintech Regulation; no other finding changed.

**Rule 115 — app names are not a control channel (Rule 49/102 recurrence #4).** `agent-control-channel`
was bound to `telegram`, `whatsapp`, `slack`, `control plane`, `chat interface`, `human control`,
`hijack` — all high-frequency context vocabulary across a 15MB podcast corpus (slack 281,
control plane 59, whatsapp 17, telegram 14). It re-grounded on generic AI-founder product talk
plus AUSTRAC's "never via WhatsApp or Telegram" scam-warning sentence, while `control channel`
and `command channel` were BOTH ZERO. Re-bound to the compromise mechanics
(`agent control plane`, `agent hijack`, `hijacked agent`, `telegram bot`, `whatsapp bot`,
`chat-controlled agent`): today 2 → 0. Lesson: when a candidate's thesis is a MECHANISM, every
keyword must name the mechanism; a noun for a chat app or an infra layer is context.

**Rule 116 — a participant noun is not a licensing event; and a date in a title ages.** 
`digital-asset-licence-cliff` fired only on `digital asset platform` — a noun for a market
participant, present in the PACT story's "30 non-bank payment companies and digital asset
platforms" — and re-proposed itself 36 days after its 12 Oct proposal with a title whose
deadline ("1 October") had already passed. Dropped the participant noun; only licensing
MECHANISM vocabulary grounds it now (`digital asset licence`, `tokenised custody`,
`no-action position`, `transitional relief`, `10% of annual turnover`, `dap licence`).
Two general lessons: (a) any candidate whose keywords include a noun for the ENTITY TYPE will
fire on every day that type is mentioned — bind to the event; (b) a title carrying a calendar
date is a depreciating asset — check the date against today before the candidate is proposed.

**Practice note (Rule 45 recurrence #13):** after both fixes the blog pool emptied, so three
SUBJECT-BOUND candidates were ADDED for the day's own critical signals — never a loosened gate:
`private-credit-spv-disclosure` (10 hits today / 0 across the 7 prior retained days),
`pact-intel-sharing` (8 / 0), `far-reporting-relief` (10 / 16, the prior hits being 12 Nov's
red-tape story while 13 Nov's finalised relief is the new event). All three shipped as the day's
blog slate. **Beware bare `pact` as a keyword: `re.escape` + substring matching makes it fire
inside "impact"** — 553 hits today, 3,657 across prior days. Use `anti-scam`, `scam-safe accord`,
`fintech australia`, `payments anti-scam coordination` instead.

**Curation (Rule 104–105 recurrence):** the AMLHive lane that morning shortlisted Tranche 2
day-100, the destination-account entity check and borrowed-deposit source-of-funds, and its full
slate touched all six of the day's findings. The LinkedIn slate therefore took the angles it did
NOT shortlist (PACT self-regulation, REP 846 disclosure mechanics, CBA contra-leg "remediation is
not a defence", FAR relief) plus one angle absent from its slate entirely (AUSTRAC being
impersonated — the tell being the payment rail). Hooks were rewritten in Haris's voice: the
auto hooks shipped `…build their own` (ends on a possessive with no noun), `…advice files failing`
(dangling participle) and a figure-only list with no finite verb (`42,000 business customers, $8.5m…,
and a $26.4m remediation`). Product names stripped from all copy.

**Rule 117 — an INSTITUTION is not a subject, and a bare mood word grounds nothing.** Two
candidates carried the whole blog slate on a single context keyword each. `neocloud-credit-marks`
ended its list in bare `distressed`, which fired on "distressed-company books" in an insolvency
story while `neocloud`, `bond marks`, `below 80c`, `project jupiter` and `supplier mortality` were
all ZERO. `defence-quantum-capital-route` carried `national reconstruction fund` — an institution
shared by every sovereign-backed round — which fired on Q-CTRL's Series C while `diraq`, `darpa`,
`rheinmetall`, `boxer crv` and `drone swarm` were all ZERO, so it would have shipped a
Diraq/Rheinmetall post on a Q-CTRL day. Both gaps then asserted figures absent from the corpus
(CoreWeave, Oracle Project Jupiter, Gartner; Diraq's DARPA tranche, the Rheinmetall teaming).
General rules: (a) a funding body, government agency or programme name is context vocabulary —
it appears in every story that body touches; bind to the recipient or the mechanism. (b) An
emotional/market mood word (`distressed`, `troubled`, `stressed`) can never ground a candidate;
it is the adjective the reporter chose, not the subject. (c) A hit count of 1 is a prompt to read
the firing sentence, not a pass — both defects looked "grounded" at 1 match.

**Rule 118 — verify the replay before writing "0 hits" in the comment.** The first draft of the
practice note claimed all three new candidates were 0 across the seven prior retained research
days. Replay showed `q-ctrl` and `30% minimum tax` each appeared ONCE before, in the 14 Nov
corpus, as context lines. The candidates still deserved their slots (no live post covers either
gap, and today's findings report the mechanics as news), but the note was corrected rather than
left to reassure the next run. A false replay claim is worse than a repeat: it disables the gate
that would catch the repeat.

**Rule 119 — a twin registration costs a slot, and that is the point.** Registering
`trust-tax-cgt-bargaining` ↔ `startup-cgt-carveout-draft` (one bill family: discount mechanics vs
the trust tax that buys the crossbench votes) marked the new candidate a repeat because its twin
had shipped 14 Nov. The slate delivered two blog ideas instead of three. Correct outcome: Rule 39
prefers two well-matched ideas to three where one is a repeat of the same family, and the angle is
held in the curated section for the next CGT cycle rather than shipped early.

**Practice note (Rule 45 recurrence #14):** after both grounding fixes the blog pool emptied, so
three SUBJECT-BOUND candidates were ADDED for the day's own signals — never a loosened gate:
`super-emerging-asset-benchmark` (7 hits today / 0 prior), `sovereign-corporate-coinvestment`
(6 / 1 context mention on 14 Nov), `trust-tax-cgt-bargaining` (5 / 1 context mention).
Curation took the angles the AMLHive lane did not: that lane shortlisted the AUSTRAC-lodgement
trail, the trust-beneficiary refusal and the designated-services scope check, and its #4 used the
Morgan AI insolvency seed — so the generated LinkedIn idea #3 (same seed) was DROPPED rather than
re-delivered to a second audience.

**Rule 120 — a gap AGES even when its title does not.** `digital-duty-of-care-ai-service` was
written on 20 Oct with a dated peg inside the gap text ("referred to a Senate committee the same
day … report due 20 November"). By 20 Nov the title was still fresh (never proposed) and still
grounded (one hit on `digital duty of care` in The Conversation's scope critique), so every gate
passed — and the delivered gap asserted a report date that two Google News sweeps could not
confirm, on the very day it claimed the report was due. The peg was replaced with two verified
facts (House passage 29 Oct, submissions closed 30 Oct, both carried by two publications each),
the unverifiable date deleted, and the gap re-led onto the day's own sentence. Rule 58/110 applied
to a PRE-EXISTING candidate: freshness is a property of the TITLE, accuracy is a property of the
TEXT, and the two age at different rates. Verify any date, penalty figure or stage-of-passage
claim in a candidate's gap against live sources before it ships.

**Rule 121 — one fresh grounded candidate is a sourcing signal, not a thin day.** With 5 of the
day's 6 findings in AI governance, the pillar's pool held exactly one usable candidate: the rest
were published, inside the 21-day window, or zero-hit (28 titles). Two subject-bound candidates
were ADDED rather than any gate loosened — `frontier-assurance-triad` (7 distinct terms today:
independent evaluation / third-party oversight / immediate shutdown / recursive self-improvement /
risk-containment / baseline standards / incident notification) and `board-ai-oversight-reporting-line`
(5: board readiness / briefs the board / no basic ai governance framework / general counsel risk
index / chief legal officers). Replay honestly: B is 0 on every prior retained day, A is 0 except
2 terms on 13 Nov, where the incident-register candidate owns that vocabulary — say so in the code
comment instead of claiming a clean sweep. And when two new candidates cover one domain, check the
gaps describe DIFFERENT artefacts (reporting line vs named accountability) before shipping both.

**Rule 122 (21 Nov 2026) — suppressing a delivered TITLE does not remove the CANDIDATE.**
On 21 Nov the `datacentre-energy-grid` blog candidate re-proposed **"Power, Not Land"**, a title
delivered verbatim on 16 Oct. The 16 Nov run had already spotted the repeat, pruned its
never-delivered ledger row and reported it as handled — yet the candidate itself was never
retired or re-bound, and its keywords still fire on any power/grid day, so it re-entered the pool
and won a slot five weeks later on the same `date % 5` Cloud rotation. Both suppression surfaces
(the 10-day file scan and the ledger window) are SHORTER than the observed repeat interval, so a
candidate whose vocabulary is generic to its pillar will always outlive them. Fix belongs at the
candidate, not the title: retire or re-bind it, register the subject-bound replacement
(`datacentre-power-exposure`), and twin it both ways against family members
(`datacentre-energy-grid`, `grid-connection-financing`) so the gap cannot re-propose itself under
another key. General rule: a dedupe ledger records what was DELIVERED; it can never stop what a
live candidate will PROPOSE.

**Rule 123 (21 Nov 2026) — the keyword gate can pass while the GAP fabricates its evidence.**
`provider-bond-viability` fired legitimately: `CoreWeave` and `Gartner` are both present in
today's corpus. But its gap text asserted "CoreWeave below 80c at ~15% yield", "~$18bn of Oracle's
Project Jupiter loans stressed", "QTS and Hyperion below par" and "Gartner expects over 80% of
neoclouds to cease independent operations by 2030" — replaying the gap's OWN figures against the
corpus returns `80c` 0, `15%` 0, `Hyperion` 0, `Jupiter` 0, `bond` 0, `yield` 0. Two keywords from
two unrelated sentences (CoreWeave's share price, a Gartner citation in a source list) were enough
to ground a paragraph of invented numbers. Rule 34/58/110 class, but a surface the earlier fixes
never covered: **gate the gap's numbers against the corpus, not just the title's**, and treat "two
hits from two different sentences" as two context mentions, never as grounding. The repaired
version was rewritten onto the day's own sentences (CoreWeave ~-25% in a month; lenders splitting
hyperscalers from short-contract AI facilities; Goldman's SPV owning the chips under a lease of
five years or less) and the title moved off "bond price" because bonds are absent from the corpus.

## Rule 122 (Nov 24 2026) — RETIRE a candidate whose grounding is a NAME or a phrase of analysis

Two `BLOG_CANDIDATES` shipped on the same day against a corpus containing neither subject. This is
the Rule 49/56 defect one layer into the candidate registry itself, and the reason it survives every
existing gate is that both candidates *did* report hits — just not on their own subject.

`govt-coinvestment-accountability` — keywords `innovation victoria`, `breakthrough victoria`,
`launchvic`, `returned to taxpayers`, `wind the fund up`, `21.9%`, `taxpayer`. It fired on exactly
one term: **"Innovation Victoria"**, appearing as a *passing investor name* in the Andromeda round
("Forerunner Ventures and Innovation Victoria backing the round"). `breakthrough victoria`,
`launchvic`, `returned to taxpayers`, `wind the fund up` were all ZERO. Every figure in its gap —
$529.3m, 103 investments, 21.9% FY25 IRR, $83.7m returned — replayed to **0 hits**, and its peg
(a 28 November Victorian election) had aged out. An investor name is not a subject.

`ai-acqui-hire-exit-modelling` — keywords `acqui-hire`, `acqui-hired`, `liquidity event`,
`repeat buyers`, `rollup`, `consolidation inside the ai cohort`, `prices were disclosed for only 12`.
One term fired: **"liquidity event"**, lifted from the ESS dry-tax sentence ("taxed on paper value
before any liquidity event"). `acqui-hire` 0, and the gap's "195 AI-on-AI acquisitions by 29 Sep
2026 / 14% above 2025 / 67 repeat buyers / ~42% of deals / price disclosed for only 12" replayed to
**0 hits**. A phrase of analysis is not grounding, and a census the day never mentions is an
invented statistic regardless of the title being clean.

**Rule:** when a candidate's keyword list can only fire on (a) a company or investor NAME or
(b) a phrase that belongs to another story's argument, the candidate is ungrounded — retire it
rather than re-bind it, because a re-bound keyword list will keep colliding with whatever sentence
in the shared corpus happens to contain the phrase. Retiring is a removal, never a loosened gate;
then ADD subject-bound candidates for the day's own signals.

Replacements added the same run, each keyword verified 2–4 hits on the 24 Nov corpus and 0 across
the prior seven research days: `agent-adverse-action-authorisation` (`automated email`,
`access was revoked`, `redundancies`, `brought the talks forward`), `form-d-round-reading`
(`form d`, `unsold`, `first sale`, `targeted us$75m`), `post-listing-exercise-decision`
(`opened thursday`, `first-day`, `debut pop`, `secondary liquidity`). All three fired at 4 signal
matches and their gaps describe the day's own sentences.

**Practice note:** the corpus read used to verify grounding must include the research JSON *and*
`gumby-brief-input.md` — a figure that appears in the brief but not the JSON is still grounded.
And after replacing candidates, prune the never-delivered titles from the ledger (Rule 72): both
retired titles had already been recorded for 2026-11-24 and would otherwise have suppressed those
titles for 10 days without ever shipping.

## Rules 123–125 (25 Nov 2026)

**Rule 123 — a gap that names a STAGE of a process ages the moment that stage completes.**
The frontier-AI candidate's gap still described the Joint Select Committee's *12 October interim
advice* and promised a "30 November report"; the final report tabled 24 November, so the gap
described a superseded stage and asserted a vendor-contract incident-reporting flow-down that the
corpus never stated (`incident report`, `frontier lab`, `vendor contract`, `model supplier` — each
**0** hits today). Re-derive any candidate's gap from today's sentences when it re-fires; a gap whose
anchors are all zero is an ungrounded candidate, never a padding option.

**Rule 124 — ledger suppression windows are AGE windows, not freshness gates.** A **36-day-old** and
a **44-day-old** title both shipped verbatim because neither fell inside the 10-day `_repeat` window
and nothing re-tested their gaps. Add a second test above ~30 days: the gap is re-verified against
the day's corpus, and a title whose gap has 0 corpus anchors loses to any fresh grounded candidate.
Silence from the ledger is not approval.

**Rule 125 — `portfolio_hit` is not the subject, at any pillar.** Rule 69 fixed the AML-subject case;
a UK DRCF agentic-liability finding carrying `portfolio_hit: PayLicence AU` still resolved to
*Australian Fintech Regulation* with a "licence application" CTA. The earlier dominance guards
(66/76/80/87) all require a regulator term to be PRESENT, so a finding naming no ASIC/APRA/AUSTRAC
term at all fell through to the `PORTFOLIO_PILLAR` map. `pillar_for()` now ends with an AI-dominance
guard before that fallback (`_ai_n3 >= 3 and _ai_n3 > _fin_n3` → AI Agents & Governance; the CTA
follows because `_pick_cta` already drops a portfolio CTA whose pillar disagrees). Replay across
`research_2026-11-18..25.json`, 48 findings: **1 changed** (the DRCF finding, intended), **0
regressions**. `portfolio_hit` records which product is AFFECTED; the pillar records what the post
is ABOUT.

**Practice note (today's run):** both auto blog ideas were replaced, not padded. Two subject-bound
candidates were ADDED and replayed per-day across `research_2026-11-1*.json`
(`datacentre-ownership-security`: 7 hits today, 0 on 17–24 Nov; `ai-literacy-evidence-standard`:
12 today, 0 on 17–24 Nov). The two undelivered titles were pruned from `.blog_title_history.jsonl`
(Rule 72) and the two delivered titles recorded the same run; a backup was kept first. The AUSTRAC
enforcement piece was neither delivered nor suppressed — it is a carry-over with an explicit
"re-verify the figures and update the roll count" precondition.
