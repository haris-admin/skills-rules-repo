---
name: alt-funding-sparktoro-model
description: Evaluate and draft SparkToro-style alternative funding — a non-VC angel raise (profit-share LLC/unit structure, capital-back-first waterfall, no forced exit) as popularized by Rand Fishkin/SparkToro, and assess whether it fits a given venture better than traditional priced-equity VC. Use when the user asks to review, compare, or apply "SparkToro-style funding," "profit-share funding," "revenue-share equity," "non-dilutive angel structure," or asks whether their venture should raise this way instead of a normal VC/priced round; also use when drafting a fit memo or term sheet outline for such a raise, including for an Australian venture where the US LLC mechanics don't transplant directly.
---

# SparkToro-style alternative funding

Evaluates fit for, and drafts starting documents for, the non-VC angel funding model SparkToro
popularized: an LLC (or local equivalent) raising from angels via units/shares that carry a
capital-back-first profit-share right instead of priced preferred stock — built for founders who
want a plausible profitable-but-not-VC-scale outcome to remain a *good* outcome for investors too,
not a failure.

## Workflow

1. **Understand the venture.** Get (or infer from context already available): stage/revenue,
   total capital need and timeframe, growth ambition (bounded-profitable vs. VC-scale), founder
   control preference, jurisdiction of the operating entity, and what investor base is realistically
   reachable (angels vs. institutional funds).

2. **Read `references/sparktoro-model-mechanics.md`** for the actual mechanics before assessing
   fit or drafting anything — don't reconstruct the model from memory. It covers the entity choice,
   the profit-distribution waterfall, governance terms, deal size/process, and what the model
   explicitly is *not* (not a SAFE, not revenue-based financing, not preferred stock).

3. **Assess fit** using `assets/fit-memo-template.md`'s signal table (outcome-size expectations,
   capital need, growth appetite, control preference, exit intent, investor base, distribution
   mechanics). Fill it in against the venture's actual profile rather than treating the model as
   universally good — it is a poor fit for a venture that genuinely needs VC-scale capital or has
   investors expecting a priced markup.

4. **If the venture is Australian (or any non-US jurisdiction), read
   `references/australian-structuring-notes.md` before drafting anything.** The US LLC's
   pass-through profit distribution does not map cleanly onto Australian entity types — there's a
   real trade-off between a Pty Ltd + bespoke share class (familiar, but company tax before
   franked dividends) and a unit trust (closer to LLC pass-through economics, but broadly-offered
   units risk being caught as a managed investment scheme requiring an AFSL). Fundraising-exemption
   caps (wholesale/sophisticated investor certification vs. the 20-investor/$2M small-scale
   exemption) also mean the investor-count and check-size assumptions from SparkToro's own raise
   may need to shrink or restructure. Flag these as open legal questions in any output rather than
   silently picking one path.

5. **Produce the deliverable(s) the user asked for:**
   - A fit assessment → fill out `assets/fit-memo-template.md` and present the recommendation
     (good fit / partial fit with named blockers / poor fit with a better alternative named).
   - A term sheet or structuring starting point → fill out `assets/term-sheet-outline.md`, keeping
     every bracketed term open pending legal review.

6. **Always close with the legal/tax caveat.** This model touches securities-offer exemptions and
   entity tax treatment — both templates already carry a "not legal advice, get a lawyer before
   this goes to a real investor" line. Never drop it when adapting the templates' text.

## What not to do

- Don't present this as a drop-in replacement for VC without running the fit table — it's a
  genuinely different bet (bounded outcome, investor yield via dividends) not a strictly-better
  option.
- Don't assume the US entity/instrument choices apply unchanged outside the US — always check
  jurisdiction first.
- Don't draft investor-facing documents as final/ready-to-send — these are discussion drafts for
  the founder and their own counsel, not something to hand an investor as-is.
